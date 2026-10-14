"""13A: same-coordinate VV/VH radiometric investigation via Earth Engine.

Does not use independent reference class labels. Processed and native backscatter,
viewing angle and mask support are sampled on a stable UTM reference grid.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .core import (
    ANGLE_MIN, ANGLE_MAX, CRS_M, SCALE_M, ee_initialize, load_boundary,
    load_scenes, outputs, write_json,
)
from .pairs import select_pairs


def fixed_reference_points(polygon, n: int = 550, seed: int = 20261014) -> pd.DataFrame:
    """Generate reproducible fixed UTM-grid-aligned point locations within ROI.

    Equal-probability point sampling for radiometry (NOT a formal validation
    probability sample and NOT labelled water ground truth).
    """
    from shapely.geometry import Point
    from pyproj import Transformer
    if not 40 <= n <= 2500:
        raise ValueError("n reference points must be between 40 and 2500")
    to_utm=Transformer.from_crs("EPSG:4326",CRS_M,always_xy=True)
    to_ll=Transformer.from_crs(CRS_M,"EPSG:4326",always_xy=True)
    from shapely.ops import transform
    poly_utm=transform(to_utm.transform,polygon)
    minx,miny,maxx,maxy=poly_utm.bounds
    rng=np.random.default_rng(seed)
    used=set()
    coords=[]
    for _ in range(n*150):
        xx=rng.uniform(minx,maxx)
        yy=rng.uniform(miny,maxy)
        # Snap to a global fixed 30m UTM grid; avoid subpixel sample drift
        xx=(np.floor(xx/SCALE_M)+0.5)*SCALE_M
        yy=(np.floor(yy/SCALE_M)+0.5)*SCALE_M
        key=(int(round(xx/SCALE_M)),int(round(yy/SCALE_M)))
        if key in used or not poly_utm.contains(Point(xx,yy)):
            continue
        used.add(key)
        lon,lat=to_ll.transform(xx,yy)
        coords.append({"point_id":f"Q{len(coords)+1:04d}","utm_x_m":xx,"utm_y_m":yy,
                       "longitude":lon,"latitude":lat})
        if len(coords)==n:
            break
    if len(coords)!=n:
        raise RuntimeError(f"Only sampled {len(coords)}/{n} points; inspect polygon")
    return pd.DataFrame(coords)


def _polarizations(ee, scene_id: str):
    image=ee.Image("COPERNICUS/S1_GRD/"+scene_id)
    angle=image.select("angle")
    angle_ok=angle.gte(ANGLE_MIN).And(angle.lte(ANGLE_MAX))
    vv0=image.select("VV").updateMask(angle_ok)
    vh0=image.select("VH").updateMask(angle_ok)
    vv=vv0.focal_median(radius=30,kernelType="circle",units="meters").updateMask(vv0.mask())
    vh=vh0.focal_median(radius=30,kernelType="circle",units="meters").updateMask(vh0.mask())
    return ee.Image.cat([
        vv.rename("VV_smoothed_db"),vh.rename("VH_smoothed_db"),
        vv0.rename("VV_original_db"),vh0.rename("VH_original_db"),
        angle.rename("incidence_angle_deg")
    ])


def run_radiometry(root: Path, *, n_points=550, seed=20261014, pair_names=None) -> dict:
    root=Path(root).resolve()
    scene=load_scenes(root)
    pairs=select_pairs(scene,names=pair_names)
    if not pairs:
        raise ValueError("No scene pairs selected")
    polygon=load_boundary(root)
    table_dir, fig_dir=outputs(root,"analysis13")
    points=fixed_reference_points(polygon,n=n_points,seed=seed)
    # Stable point coordinates retained, not regenerated between scenes.
    points_path=table_dir/"13A_fixed_reference_points.csv"
    points.to_csv(points_path,index=False)
    ee=ee_initialize()
    unique_scenes=list(dict.fromkeys(s for _,a,b in pairs for s in (a,b)))
    sample_points=ee.FeatureCollection([
        ee.Feature(ee.Geometry.Point([float(r.longitude),float(r.latitude)]),
                   {"point_id":str(r.point_id)})
        for r in points.itertuples(index=False)])
    rows=[]
    for i,scene_id in enumerate(unique_scenes,1):
        print(f"Sampling scene {i}/{len(unique_scenes)}: {scene_id[:44]}")
        data=_polarizations(ee,scene_id)
        # sampleRegions snaps the *same fixed points* to the target grid.
        selected=data.sampleRegions(collection=sample_points,properties=["point_id"],
                                    projection=ee.Projection(CRS_M).atScale(SCALE_M),
                                    scale=SCALE_M,geometries=False)
        result=selected.getInfo()
        for item in result['features']:
            p=item['properties']
            rows.append({"scene_id":scene_id,**p})
    samples=pd.DataFrame(rows)
    if samples.empty or not {"scene_id","point_id","VV_smoothed_db","VH_smoothed_db","incidence_angle_deg"} <= set(samples.columns):
        raise RuntimeError("No valid sampled radiometry; inspect scene and mask")
    if samples.duplicated(["scene_id","point_id"]).any():
        raise RuntimeError("Earth Engine returned duplicated point IDs")
    samples.to_csv(table_dir/"13A_same_coordinate_VV_VH_samples.csv",index=False)
    grouped=[]
    for scene_id,g in samples.groupby("scene_id"):
        vv=g.VV_smoothed_db.astype(float)
        vh=g.VH_smoothed_db.astype(float)
        angle=g.incidence_angle_deg.astype(float)
        bins=np.floor(vh*2)/2
        most_frequent= float(bins.value_counts(normalize=True).max())
        grouped.append({"scene_id":scene_id,"sample_count":len(g),
                        "missing_fixed_point_fraction":1-len(g)/n_points,
                        "vv_median_db":vv.median(),"vv_p10_db":vv.quantile(.1),"vv_p90_db":vv.quantile(.9),
                        "vh_median_db":vh.median(),"vh_p10_db":vh.quantile(.1),"vh_p90_db":vh.quantile(.9),
                        "incidence_angle_median_deg":angle.median(),
                        "incidence_angle_p10_deg":angle.quantile(.1),
                        "incidence_angle_p90_deg":angle.quantile(.9),
                        "vv_fraction_below_m19":float((vv<=-19).mean()),
                        "vv_fraction_below_m17":float((vv<=-17).mean()),
                        "vv_fraction_below_m15":float((vv<=-15).mean()),
                        "vh_fraction_in_most_common_halfdb_bin":most_frequent})
    summary=pd.DataFrame(grouped)
    summary.to_csv(table_dir/"13A_scene_radiometric_statistics.csv",index=False)
    changes=[]
    for pair,one,two in pairs:
        a=samples.loc[samples.scene_id==one].set_index('point_id')
        b=samples.loc[samples.scene_id==two].set_index('point_id')
        pts=a.join(b,how='inner',lsuffix='_early',rsuffix='_late')
        if len(pts)<0.4*n_points:
            warnings.warn(f"{pair.name}: <40% of fixed sample points jointly observed")
        if pts.empty:
            raise RuntimeError(f"No shared reference coordinates for {pair.name}")
        delta_vv=pts.VV_smoothed_db_late-pts.VV_smoothed_db_early
        delta_vh=pts.VH_smoothed_db_late-pts.VH_smoothed_db_early
        for pid in pts.index:
            changes.append({"pair":pair.name,"point_id":pid,
                            "before_id":one,"after_id":two,
                            "VV_change_db":float(delta_vv.loc[pid]),
                            "VH_change_db":float(delta_vh.loc[pid]),
                            "angle_change_deg":float(pts.loc[pid,'incidence_angle_deg_late']-pts.loc[pid,'incidence_angle_deg_early'])})
    changes=pd.DataFrame(changes)
    changes.to_csv(table_dir/"13A_paired_same_location_backscatter_changes.csv",index=False)
    fig,axes=plt.subplots(1,2,figsize=(14,5),constrained_layout=True)
    for ax,col,title in ((axes[0],"VV_change_db","Within-pair ΔVV"),(axes[1],"VH_change_db","Within-pair ΔVH")):
        vals=[g[col].dropna().to_numpy() for _,g in changes.groupby('pair')]
        names=[p for p,_ in changes.groupby('pair')]
        ax.boxplot(vals, tick_labels=names,showfliers=False)
        ax.axhline(0,color='grey',lw=1)
        ax.set_title(title)
        ax.set_ylabel("Later − earlier (dB)")
        ax.tick_params(axis='x',rotation=45)
    fig.suptitle("Fixed-coordinate VV/VH changes: radar diagnostics, not water labels")
    fig.savefig(fig_dir/"13A_paired_VV_VH_change_diagnostics.png",dpi=145,bbox_inches='tight')
    plt.close(fig)
    report={"created_utc":datetime.now(timezone.utc).isoformat(),"status":"executed_radiometric_screening_not_validation",
            "total_fixed_points":int(n_points),"scene_count":len(unique_scenes),
            "pair_count":len(pairs),"same_coordinate_points":True,
            "warning":"Threshold changes and backscatter shifts cannot alone classify water or determine flood severity."}
    write_json(table_dir/"13A_manifest.json",report)
    return report
