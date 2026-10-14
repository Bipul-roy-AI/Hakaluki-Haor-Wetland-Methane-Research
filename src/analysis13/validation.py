"""13E: stratified image reference design and design-weighted validation.

SAR LOW-VV = an unvalidated predictor. Independent interpretation from
coincident imagery defines open_water / flooded_vegetation / dry_or_other.
No labels are generated from SAR itself, and no accuracy is fabricated.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from pyproj import Transformer
from shapely.ops import transform as shapely_transform

from .core import load_boundary, outputs, write_json

REFERENCE_LABELS={"open_water","flooded_vegetation","dry_or_other","unobservable"}


def _strata(vv: np.ndarray, good: np.ndarray) -> np.ndarray:
    strata=np.zeros(vv.shape,dtype='uint8')
    strata[good&(vv<=-19)]=1
    strata[good&(vv>-19)&(vv<=-15)]=2
    strata[good&(vv>-15)]=3
    return strata


def make_sample(root: Path, reference_raster: Path, *, scene_id: str,
                n_each: int=60, seed: int=9214) -> dict:
    """Blind-reference sample from a single eligible scene raster.

    Stratification uses SAR *prediction* only for sample efficiency; reference
    imagery must be assessed independently, preferably by blinded annotators.
    """
    if not 15<=n_each<=500:
        raise ValueError('n_each must be between 15 and 500')
    root=Path(root).resolve()
    reference_raster=Path(reference_raster).resolve()
    if not reference_raster.is_file():
        raise FileNotFoundError('Need an actual 4-band 13B matched-grid GeoTIFF from 13B')
    polygon=load_boundary(root)
    proj=Transformer.from_crs('EPSG:4326','EPSG:32646',always_xy=True)
    utm=shapely_transform(proj.transform,polygon)
    td,_=outputs(root,'analysis13')
    with rasterio.open(reference_raster) as src:
        if src.count!=4 or src.crs.to_epsg()!=32646:
            raise ValueError('Reference raster must be aligned 4-band UTM46 scene export')
        vv=src.read(1)
        observed=src.read(4)>0.5
        inside=geometry_mask([utm.__geo_interface__],out_shape=(src.height,src.width),
                             transform=src.transform,invert=True)
        good=inside&observed&np.isfinite(vv)&(vv>-100)
        strata=_strata(vv,good)
        rng=np.random.default_rng(seed)
        to_ll=Transformer.from_crs('EPSG:32646','EPSG:4326',always_xy=True)
        rows=[];areas=[]
        pixel_area_km2=abs(src.transform.a*src.transform.e-src.transform.b*src.transform.d)/1e6
        for code,name in [(1,'VV_below_minus19'),(2,'VV_minus19_to_minus15'),(3,'VV_above_minus15')]:
            rc=np.argwhere(strata==code)
            n_total=len(rc)
            if n_total==0:
                raise ValueError(f'Stratum {name} empty; redesign before sampling')
            n=min(n_each,n_total)
            chosen=rc[rng.choice(n_total,size=n,replace=False)]
            area=n_total*pixel_area_km2
            areas.append({'stratum_id':code,'stratum_name':name,'n_pixel_population':n_total,
                          'sample_count':n,'stratum_area_km2':area,
                          'inclusion_probability':n/n_total})
            for rr,cc in chosen:
                x,y=rasterio.transform.xy(src.transform,int(rr),int(cc),offset='center')
                lon,lat=to_ll.transform(x,y)
                rows.append({'point_id':f'V{code}_{len(rows)+1:04d}',
                             'scene_id':scene_id,'stratum_id':code,
                             'row':int(rr),'col':int(cc),
                             'longitude':lon,'latitude':lat,
                             'VV_db':float(vv[rr,cc]),
                             'prediction_open_water_m17':bool(vv[rr,cc]<=-17),
                             'stratum_population_pixels':n_total,
                             'stratum_sample_count':n,
                             'stratum_area_km2':area})
    df=pd.DataFrame(rows)
    df.to_csv(td/'13E_private_validation_sample_metadata.csv',index=False)
    # Blind view excludes screen predictions, class values and thresholds.
    blind=df[['point_id','scene_id','longitude','latitude']].copy()
    blind['reference_image_date']=''
    blind['reference_data_source']=''
    blind['reference_label']=''
    blind['interpretation_confidence']=''
    blind['analyst']=''
    blind['notes']=''
    blind.to_csv(td/'13E_BLIND_reference_labelling.csv',index=False)
    pd.DataFrame(areas).to_csv(td/'13E_area_and_sample_design.csv',index=False)
    manifest={'status':'REFERENCE_LABELS_NEEDED_NOT_VALIDATED',
              'generated_utc':datetime.now(timezone.utc).isoformat(),
              'scene_id':scene_id,'raster':str(reference_raster),
              'sample_size':len(df),'strata':areas,
              'classification_predicted':'VV<=−17dB means candidate low-VV screen, not independently verified water',
              'independence_rule':'Labels must come from separate close-date imagery/ground reference and be evaluated blind to prediction.',
              'uncertain_reference_rule':'Do not silently drop unobservable points or treat them as dry.'}
    write_json(td/'13E_reference_design_manifest.json',manifest)
    return manifest


def score_reference(root: Path, *, private_sample: Path | None=None,
                    labels: Path | None=None, n_boot: int=750, seed: int=3091) -> dict:
    """Stratum area-weighted binary open-water score plus multiclass context.

    All sample points must be labelled. Unobservable points require resolving
    reference imagery; no error-matrix point estimates are fabricated otherwise.
    Simple stratified bootstrap is exploratory; spatial correlation not corrected.
    """
    root=Path(root).resolve()
    td,_=outputs(root,'analysis13')
    a=Path(private_sample) if private_sample else td/'13E_private_validation_sample_metadata.csv'
    b=Path(labels) if labels else td/'13E_BLIND_reference_labelling.csv'
    if not a.exists() or not b.exists():
        raise FileNotFoundError('Need the generated sample metadata and independently labelled CSV')
    meta=pd.read_csv(a)
    lab=pd.read_csv(b)
    required={'point_id','reference_label','reference_image_date','reference_data_source','analyst'}
    if not required.issubset(lab.columns):
        raise ValueError(f'Reference label table lacks {required-set(lab.columns)}')
    if lab.point_id.duplicated().any():
        raise ValueError('Duplicate annotated point IDs')
    joined=meta.merge(lab[['point_id','reference_label','reference_image_date',
                           'reference_data_source','analyst']],on='point_id',how='left',validate='one_to_one')
    labels=joined.reference_label.fillna('').str.strip().str.lower()
    empty=labels.eq('')
    invalid=~labels.isin(REFERENCE_LABELS)&~empty
    uncertain=labels.eq('unobservable')
    if empty.any() or invalid.any() or uncertain.any():
        status={'status':'VALIDATION_INCOMPLETE_DO_NOT_CALCULATE_ACCURACY',
                'missing_reference_labels':int(empty.sum()),'invalid_labels':int(invalid.sum()),
                'unobservable_labels':int(uncertain.sum()),'total_design_points':len(joined)}
        write_json(td/'13E_reference_scoring_gate.json',status)
        raise RuntimeError(f"Reference validation incomplete: {status}")
    if joined[['reference_image_date','reference_data_source','analyst']].isna().any().any() or \
       (joined[['reference_image_date','reference_data_source','analyst']].astype(str).apply(lambda col:col.str.strip().eq('')).any().any()):
        raise RuntimeError('Reference imagery date, data source and analyst must be documented for every label')
    joined['reference_open_water']=labels.eq('open_water')
    joined['predicted_open_water']=joined.prediction_open_water_m17.astype(bool)
    if joined.groupby('stratum_id').size().min()<15:
        raise RuntimeError('Insufficient reference samples for at least one stratum')
    joined['sampling_weight_km2']=joined.stratum_area_km2/joined.stratum_sample_count
    # Design-corrected confusion cells (km2 over observed pixel-grid domain).
    confusion=(joined.groupby(['predicted_open_water','reference_open_water'],dropna=False)
               .sampling_weight_km2.sum().reset_index())
    confusion.to_csv(td/'13E_area_weighted_openwater_error_matrix.csv',index=False)
    def compute(df):
        w=df.sampling_weight_km2.to_numpy(dtype=float)
        prediction=df.predicted_open_water.to_numpy(dtype=bool)
        truth=df.reference_open_water.to_numpy(dtype=bool)
        tp=w[prediction&truth].sum()
        tn=w[~prediction&~truth].sum()
        fp=w[prediction&~truth].sum()
        fn=w[~prediction&truth].sum()
        area=w.sum()
        return {'OA':(tp+tn)/area if area else np.nan,
                'openwater_user_accuracy':tp/(tp+fp) if tp+fp>0 else np.nan,
                'openwater_producer_accuracy':tp/(tp+fn) if tp+fn>0 else np.nan,
                'estimated_openwater_km2':tp+fn,
                'area_km2':area,
                'flooded_vegetation_reference_km2':w[df.reference_label.str.lower().eq('flooded_vegetation').to_numpy()].sum(),
                'flooded_vegetation_lowVV_m17_km2':w[(df.reference_label.str.lower().eq('flooded_vegetation')&df.predicted_open_water).to_numpy()].sum()}
    metrics=compute(joined)
    rng=np.random.default_rng(seed)
    boot=[]
    for _ in range(n_boot):
        pieces=[]
        for _,g in joined.groupby('stratum_id'):
            indices=rng.integers(0,len(g),size=len(g))
            pieces.append(g.iloc[indices])
        boot.append(compute(pd.concat(pieces,ignore_index=True)))
    for key in ('OA','openwater_user_accuracy','openwater_producer_accuracy','estimated_openwater_km2'):
        sample=np.array([v[key] for v in boot],dtype=float)
        if np.isfinite(sample).sum()>20:
            metrics[key+'_percentile_bootstrap_2p5']=float(np.nanpercentile(sample,2.5))
            metrics[key+'_percentile_bootstrap_97p5']=float(np.nanpercentile(sample,97.5))
    manifest={'status':'REFERENCE_ACCURACY_ESTIMATED_FROM_SUPPLIED_LABELS_NOT_FIELD_VERIFIED',
              'created_utc':datetime.now(timezone.utc).isoformat(),
              'design_points':len(joined),
              'domain':'scene-support raster-cell domain, NOT full-unobserved extent',
              'binary_reference_class':'open_water only; flooded_vegetation separate',
              'bootstrap_limits':'naive within-stratum resampling; spatial autocorrelation and systematic label errors not accounted for',
              'metrics':{k:float(v) if np.isscalar(v) else v for k,v in metrics.items()}}
    write_json(td/'13E_reference_scoring_results.json',manifest)
    return manifest
