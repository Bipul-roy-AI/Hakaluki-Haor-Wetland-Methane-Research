import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.hakaluki_core import monthly_periods, otsu_from_histogram, OFFICIAL_ENVELOPE

def test_month_rollover():
    p=list(monthly_periods(2022,2022))
    assert len(p)==12 and p[-1]['end']=='2023-01-01'

def test_otsu_bimodal():
    h={'bucketMeans':[-21,-20,-19,-15,-14,-13], 'histogram':[1,20,4,3,19,1]}
    t=otsu_from_histogram(h)
    assert -19 <= t <= -14

def test_envelope():
    assert OFFICIAL_ENVELOPE[0] < OFFICIAL_ENVELOPE[2]
    assert OFFICIAL_ENVELOPE[1] < OFFICIAL_ENVELOPE[3]
