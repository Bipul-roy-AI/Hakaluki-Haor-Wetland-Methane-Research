"""13B: aligned, within-pass SAR raster comparisons, including continuous ΔVV/ΔVH.

All areas refer to the common 30m raster grid and to pixels valid in BOTH
acquisitions. They are NOT ground-validated water-area changes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import math
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject
from pyproj import Transformer
from shapely.ops import transform as shapely_transform

from .core import (
    SCALE_M, CRS_M, ANGLE_MIN, ANGLE_MAX,
    ee_initialize, load_boundary, load_scenes, outputs, write_json,
)
from .pairs import select_pairs


def spatial_grid(polygon, scale: int = SCALE_M) -> dict:
    """Globally snapped fixed UTM raster grid; used by every pair."""
    trans=Transformer.from_crs("EPSG:4326",CRS_M,always_xy=True)
    utm=shapely_transform(trans.transform,polygon)
    xmin,ymin,xmax,ymax=utm.bounds
    left=math.floor(xmin/scale)*scale
    bottom=math.floor(ymin/scale)*scale
    right=math.ceil(xmax/scale)*scale
    top=math.ceil(ymax/scale)*scale
    width=int(round((right-left)/scale))
    height=int(round((top-bottom)/scale))
    if width*height>2_500_000:
        raise RuntimeError("Spatial grid exceeds 2.5 million cells; audit boundary")
    transform=from_origin(left,top,scale,scale)
    inside=geometry_mask([utm.__geo_interface__],out_shape=(height,width),
                         transform=transform,invert=True)
    return {"height":height,"width":width,"transform":transform,
            "inside":inside,"utm_geometry":utm,"scale_m":scale}


def ee_spatial_bands(ee, scene_id):
    image=ee.Image("COPERNICUS/S1_GRD/"+scene_id)
    angle=image.select('angle')
    ok=angle.gte(ANGLE_MIN).And(angle.lte(ANGLE_MAX))
    vv0=image.select('VV').updateMask(ok)
    vh0=image.select('VH').updateMask(ok)
    vv=vv0.focal_median(radius=30,kernelType='circle',units='meters').updateMask(vv0.mask())
    vh=vh0.focal_median(radius=30,kernelType='circle',units='meters').updateMask(vh0.mask())
    vv_valid=vv.mask().unmask(0).gt(0)
    return ee.Image.cat([
        vv.rename('VV_db').unmask(-9999).toFloat(),
        vh.rename('VH_db').unmask(-9999).toFloat(),
        angle.rename('angle_deg').unmask(-9999).toFloat(),
        vv_valid.rename('valid_VV').unmask(0).toFloat(),
    ])


def download_scene_grid(root: Path, ee, roi_ee, scene_id: str, grid: dict,
                        *, force=False) -> Path:
    """Small-area Earth Engine download, reprojected locally to one fixed UTM grid.

    The reprojected raster holds continuous VV, VH, incidence-angle and original
    masked VV-valid indicator. This preserves support and pixel alignment.
    """
    import requests
    data_path=root/"data"/"processed"/"analysis13_scene_rasters"
    data_path.mkdir(parents=True,exist_ok=True)
    token=hashlib.sha256(scene_id.encode()).hexdigest()[:12]
    dest=data_path/f"{token}_matched_30m_EPSG32646.tif"
    if dest.is_file() and not force:
        with rasterio.open(dest) as test:
            if (test.count==4 and test.crs.to_epsg()==32646 and
                test.width==grid['width'] and test.height==grid['height'] and
                test.transform==grid['transform']):
                return dest
        raise ValueError(f"Existing cached raster has incompatible grid: {dest}")
    image=ee_spatial_bands(ee,scene_id).clip(roi_ee)
    # A small-area getDownloadURL request can fail if EE's 32MB/download or
    # pixel-count limit is reached. Reduce region or use EE batch export then.
    url=image.getDownloadURL({'region':roi_ee,'crs':CRS_M,
                              'scale':SCALE_M,'format':'GEO_TIFF','filePerBand':False})
    response=requests.get(url,timeout=180)
    response.raise_for_status()
    raw=data_path/f"{token}_ee_raw.tif"
    raw.write_bytes(response.content)
    profile={"driver":"GTiff", "height":grid['height'], "width":grid['width'],
             "count":4,"dtype":"float32", "crs":CRS_M,"transform":grid['transform'],
             "nodata":-9999.0,"compress":"deflate","predictor":3}
    with rasterio.open(raw) as src, rasterio.open(dest,'w',**profile) as dst:
        if src.count!=4:
            raise RuntimeError(f"Unexpected EE raster bands ({src.count}) for {scene_id}")
        for band in range(1,5):
            reproject(source=rasterio.band(src,band),destination=rasterio.band(dst,band),
                      src_transform=src.transform,src_crs=src.crs,
                      src_nodata=-9999.0,dst_transform=grid['transform'],
                      dst_crs=CRS_M,dst_nodata=-9999.0,resampling=Resampling.nearest)
            dst.set_band_description(band,('VV_db','VH_db','angle_deg','VV_valid')[band-1])
    # Keep the raw Earth Engine download only for audit when requested; the
    # matching output is the main raster for spatial comparisons.
    raw.unlink(missing_ok=True)
    return dest


def compare_array_pair(early: np.ndarray, late: np.ndarray,
                       roi_inside: np.ndarray, *, pixel_area_km2=0.0009,
                       thresholds=(-19.0,-17.0,-15.0)) -> tuple[pd.DataFrame,dict]:
    """Pure pair comparison; bands (VV,VH,angle,valid), 2D arrays matching grid."""
    if early.shape!=late.shape or early.ndim!=3 or early.shape[0]!=4:
        raise ValueError('Both rasters require exactly four matching bands')
    if early.shape[1:]!=roi_inside.shape:
        raise ValueError('ROI mask shape must match raster')
    good=roi_inside & (early[3]>0.5) & (late[3]>0.5) & \
         np.isfinite(early[0]) & np.isfinite(late[0]) & \
         (early[0]>-100) & (late[0]>-100)
    count=int(good.sum())
    if count==0:
        raise RuntimeError('Zero shared-support pixels; cannot report change')
    stats=[]
    maps={"joint_valid":good,"vv_delta":np.where(good,late[0]-early[0],np.nan),
          "vh_delta":np.where(good & (early[1]>-100) & (late[1]>-100),late[1]-early[1],np.nan)}
    for thr in thresholds:
        a=early[0]<=thr
        b=late[0]<=thr
        both=good & a & b
        new=good & ~a & b
        lost=good & a & ~b
        neither=good & ~a & ~b
        cat=np.zeros(good.shape,dtype='uint8')
        cat[neither]=1;cat[both]=2;cat[new]=3;cat[lost]=4
        tag=f'{abs(thr):.0f}'
        maps[f'transition_m{tag}']=cat
        stats.append({"threshold_db":thr,"shared_grid_pixels":count,
                      "shared_grid_support_km2":count*pixel_area_km2,
                      "neither_km2":int(neither.sum())*pixel_area_km2,
                      "both_km2":int(both.sum())*pixel_area_km2,
                      "newly_low_vv_km2":int(new.sum())*pixel_area_km2,
                      "no_longer_low_vv_km2":int(lost.sum())*pixel_area_km2,
                      "net_km2":(int(new.sum())-int(lost.sum()))*pixel_area_km2,
                      "changed_km2":(int(new.sum())+int(lost.sum()))*pixel_area_km2,
                      "median_VV_change_db":float(np.nanmedian(maps['vv_delta'])),
                      "p10_VV_change_db":float(np.nanpercentile(maps['vv_delta'],10)),
                      "p90_VV_change_db":float(np.nanpercentile(maps['vv_delta'],90))})
    return pd.DataFrame(stats),maps


def save_spatial_maps(maps: dict, pair_name: str, dest: Path) -> None:
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cat=maps['transition_m17']
    cols=['#ffffff','#dddddd','#296b9c','#3ca56d','#b45e42']
    cm=ListedColormap(cols)
    fig,axs=plt.subplots(1,3,figsize=(17,5),constrained_layout=True)
    masked=np.ma.masked_where(cat==0,cat)
    axs[0].imshow(masked,cmap=cm,vmin=0,vmax=4,interpolation='nearest')
    axs[0].set_title('−17 dB transition states\n1 neither · 2 both · 3 new · 4 lost')
    for ax,name,label in ((axs[1],'vv_delta','ΔVV (dB)'),(axs[2],'vh_delta','ΔVH (dB)')):
        dx=maps[name]
        limit = max(3.0, float(np.nanpercentile(np.abs(dx[np.isfinite(dx)]),98))) if np.isfinite(dx).any() else 3.0
        img=ax.imshow(dx,cmap='coolwarm',vmin=-limit,vmax=limit,interpolation='nearest')
        fig.colorbar(img,ax=ax,label=label,shrink=.67)
        ax.set_title(f'Later minus earlier {label}')
    for ax in axs:
        ax.axis('off')
    fig.suptitle(pair_name.replace('_',' ')+' | shared valid ROI pixels only\nNot validated water transitions')
    fig.savefig(dest,dpi=145,bbox_inches='tight')
    plt.close(fig)


def run_spatial(root: Path, *, pair_names=None, force=False) -> dict:
    root=Path(root).resolve()
    scenes=load_scenes(root)
    pairs=select_pairs(scenes,names=pair_names)
    polygon=load_boundary(root)
    grid=spatial_grid(polygon)
    ee=ee_initialize()
    roi=ee.Geometry(polygon.__geo_interface__)
    td,fd=outputs(root,'analysis13')
    all_rows=[]
    files={}
    for j,(pair,a,b) in enumerate(pairs,1):
        print(f'Spatial pair {j}/{len(pairs)}: {pair.name}')
        first=download_scene_grid(root,ee,roi,a,grid,force=force)
        second=download_scene_grid(root,ee,roi,b,grid,force=force)
        with rasterio.open(first) as x,rasterio.open(second) as y:
            if x.transform!=y.transform or x.crs!=y.crs or x.shape!=y.shape:
                raise RuntimeError('Pair raster grids differ; no spatial comparison allowed')
            results,maps=compare_array_pair(x.read(),y.read(),grid['inside'],
                                            pixel_area_km2=SCALE_M**2/1e6)
        results.insert(0,'pair',pair.name)
        results.insert(1,'early_scene_id',a)
        results.insert(2,'late_scene_id',b)
        all_rows.append(results)
        dest=fd/f'13B_{pair.name}_spatial_change.png'
        save_spatial_maps(maps,pair.name,dest)
        files[pair.name]=str(dest)
    table=pd.concat(all_rows,ignore_index=True)
    table.to_csv(td/'13B_paired_spatial_transitions.csv',index=False)
    report={"created_utc":datetime.now(timezone.utc).isoformat(),
            "status":"executed_unvalidated_SAR_screening_change", "pair_count":len(pairs),
            "grid_crs":CRS_M,"grid_cell_m":SCALE_M,"grid_pixels":int(grid['width']*grid['height']),
            "area_support":"common observed cell centres, not exact polygon-boundary EE pixelArea",
            "spatial_map_files":files,
            "validation":"No independent water-class reference labels. Continuous backscatter change is not water-level change."}
    write_json(td/'13B_manifest.json',report)
    return report
