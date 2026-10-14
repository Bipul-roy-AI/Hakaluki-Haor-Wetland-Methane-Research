"""Unit tests for new analysis; synthetic fixtures are NOT research results."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.analysis13.core import load_scenes
from src.analysis13.offline import consecutive_transitions, run_offline
from src.analysis13.pairs import select_pairs
from src.analysis13.hydrology import first_observed_threshold_crossings, match_stage_to_sar, read_stage
from src.analysis13.methane import box_column_enhancement_ppb, scenarios_from_csv
from src.analysis13.spatial import compare_array_pair
from src.analysis13.validation import _strata, score_reference


def sample_scenes():
    rows=[]
    for i,(date,aa) in enumerate([('2022-05-11T11:56:00Z',40),('2022-05-23T11:56:00Z',162)]):
        rows.append({'scene_id':f'scene{i}','acquisition_utc':date,'pass':'ASCENDING',
                     'relative_orbit':41,'year':2022,'observed_km2':172,
                     'lowvv_m19_km2':aa-10,'lowvv_m17_km2':aa,
                     'lowvv_m15_km2':aa+3})
    return pd.DataFrame(rows)


def test_loaded_scene_validity(tmp_path):
    p=tmp_path/'scenes.csv'
    sample_scenes().to_csv(p,index=False)
    data=load_scenes(tmp_path,p)
    assert len(data)==2
    assert str(data.iloc[0].acquisition_local.tzinfo) == 'Asia/Dhaka'
    assert data.iloc[0].m17_fraction_observed == pytest.approx(40/172)


def test_no_invalid_threshold_order(tmp_path):
    sample=sample_scenes()
    sample.loc[0,'lowvv_m19_km2']=50
    p=tmp_path/'bad.csv'; sample.to_csv(p,index=False)
    with pytest.raises(ValueError,match='Threshold order'):
        load_scenes(tmp_path,p)


def test_same_orbit_transitions():
    d=sample_scenes()
    d['acquisition_utc']=pd.to_datetime(d.acquisition_utc,utc=True)
    d['acquisition_local']=d.acquisition_utc.dt.tz_convert('Asia/Dhaka')
    trans=consecutive_transitions(d)
    assert len(trans)==1
    assert trans.iloc[0].delta_m17_km2 == pytest.approx(122)
    assert trans.iloc[0].same_sign_all_thresholds


def test_no_interorbit_consecutive_transition():
    d=sample_scenes()
    d.loc[1,'pass']='DESCENDING'; d.loc[1,'relative_orbit']=77
    d['acquisition_utc']=pd.to_datetime(d.acquisition_utc,utc=True)
    d['acquisition_local']=d.acquisition_utc.dt.tz_convert('Asia/Dhaka')
    result=consecutive_transitions(d)
    assert result.empty
    assert "delta_m17_km2" in result.columns


def test_first_observed_crossing_is_bracket_only():
    d=sample_scenes()
    d['acquisition_utc']=pd.to_datetime(d.acquisition_utc,utc=True)
    d['acquisition_local']=d.acquisition_utc.dt.tz_convert('Asia/Dhaka')
    d['m17_fraction_observed']=d.lowvv_m17_km2/d.observed_km2
    out=first_observed_threshold_crossings(d,0.85)
    assert out.iloc[0].status=='first_observed_crossing_bracket'
    assert out.iloc[0].interval_days == pytest.approx(12)


def test_spatial_mask_four_exclusive_classes():
    a=np.zeros((4,2,2),dtype='float32');b=np.zeros_like(a)
    a[0]=np.array([[-20,-14],[-21,-14]],dtype='float32')
    b[0]=np.array([[-20,-20],[-14,-14]],dtype='float32')
    a[1]=b[1]=-30
    a[3]=b[3]=1
    result,m=compare_array_pair(a,b,np.ones((2,2),bool),pixel_area_km2=.0009)
    r=result[result.threshold_db==-17].iloc[0]
    assert r.both_km2==pytest.approx(.0009)
    assert r.newly_low_vv_km2==pytest.approx(.0009)
    assert r.no_longer_low_vv_km2==pytest.approx(.0009)
    assert r.neither_km2==pytest.approx(.0009)
    assert sorted(m['transition_m17'].ravel().tolist())==[1,2,3,4]


def test_spatial_joint_mask_avoids_unobserved_dry():
    a=np.zeros((4,1,2),dtype='float32');b=np.zeros_like(a)
    a[0]=[-20,-20];b[0]=[-14,-14]
    a[1]=b[1]=-28
    a[3]=1;b[3]=[1,0]
    result,m=compare_array_pair(a,b,np.ones((1,2),bool))
    assert result.iloc[1].shared_grid_pixels==1
    assert result.iloc[1].no_longer_low_vv_km2==pytest.approx(.0009)
    assert not m['joint_valid'][0,1]


def test_methane_box_arithmetic_without_noise_claim():
    estimate=box_column_enhancement_ppb(10,172,3)
    assert 0.07<estimate<0.11
    assert box_column_enhancement_ppb(100,172,3)==pytest.approx(estimate*10)
    assert box_column_enhancement_ppb(10,172,5)==pytest.approx(estimate*3/5)
    with pytest.raises(ValueError):
        box_column_enhancement_ppb(10,172,0)


def test_decline_to_calculate_unlabelled_accuracy(tmp_path):
    out=tmp_path/'results'/'tables'/'analysis13';out.mkdir(parents=True)
    a=pd.DataFrame({'point_id':['p1']*1,'stratum_id':[1],'stratum_area_km2':[1],
                    'stratum_sample_count':[1],'prediction_open_water_m17':[True]})
    b=pd.DataFrame({'point_id':['p1'],'reference_label':[''],'reference_image_date':[''],
                    'reference_data_source':[''],'analyst':['']})
    a.to_csv(out/'13E_private_validation_sample_metadata.csv',index=False)
    b.to_csv(out/'13E_BLIND_reference_labelling.csv',index=False)
    with pytest.raises(RuntimeError,match='validation incomplete'):
        score_reference(tmp_path)


def test_reference_sampling_strata():
    vv=np.array([[-22,-17,-13]],dtype=float)
    m=_strata(vv,np.ones((1,3),bool))
    assert m.tolist()==[[1,2,3]]


def test_stage_tolerance_no_imputation():
    scene=sample_scenes().iloc[:1].copy()
    scene['acquisition_utc']=pd.to_datetime(scene.acquisition_utc,utc=True)
    scene['acquisition_local']=scene.acquisition_utc.dt.tz_convert('Asia/Dhaka')
    gauge=pd.DataFrame({'station_id':['s'],
       'timestamp_local':pd.to_datetime(['2022-05-16T05:00:00+06:00'],utc=True).tz_convert('Asia/Dhaka'),
       'water_level_m':[11], 'vertical_datum':['source datum'],'source_reference':['source'],
       'quality_flag':['good']})
    merged=match_stage_to_sar(scene,gauge,tolerance_hours=36)
    assert pd.isna(merged.iloc[0].water_level_m)


def test_full_uploaded_scene_data_if_supplied():
    # Optional fixture: place the actual 94-scene CSV in local project results.
    project=Path(__file__).resolve().parents[1]
    f=project/'results'/'tables'/'scene12_S1_per_acquisition_2022_2025.csv'
    if not f.exists():
        pytest.skip('Actual Notebook12 CSV is on researcher computer, not bundled')
    d=load_scenes(project,f)
    assert len(d)==94
    assert len(select_pairs(d))==6


def test_scenarios_read_works_with_pandas_set_indexer_restriction():
    path=Path(__file__).resolve().parents[1]/'data_templates/methane_hypothetical_scenarios.csv'
    scenarios=scenarios_from_csv(path)
    assert len(scenarios)==27
    assert scenarios.scenario_basis.eq('hypothetical_not_observed_not_wetland_specific').all()


def test_stage_requires_explicit_timezone(tmp_path):
    p=tmp_path/'stage.csv'
    pd.DataFrame({'station_id':['mock_station'],'timestamp_local':['2022-06-19 05:47'],
                  'water_level_m':[10.5],'vertical_datum':['fixture'],
                  'source_reference':['SYNTHETIC TEST'],'quality_flag':['good']}).to_csv(p,index=False)
    with pytest.raises(ValueError,match='explicit timezone'):
        read_stage(p)


def test_chronology_distinguishes_utc_and_local_month():
    a=pd.DataFrame({'scene_id':['utc_june_local_july'],
        'acquisition_utc':['2022-06-30 23:47:44+00:00'],
        'pass':['DESCENDING'],'relative_orbit':[77], 'year':[2022],
        'observed_km2':[172], 'lowvv_m19_km2':[150],
        'lowvv_m17_km2':[160], 'lowvv_m15_km2':[165]})
    # Month derived from local acquisition time is July, not June.
    a['acquisition_local']=pd.to_datetime(a.acquisition_utc,utc=True).dt.tz_convert('Asia/Dhaka')
    assert a.acquisition_local.dt.month.iloc[0]==7
    assert pd.to_datetime(a.acquisition_utc,utc=True).dt.month.iloc[0]==6
