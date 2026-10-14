"""Pre-specified scene pairs selected for physical/radiometric QA.

All dates are Bangladesh LOCAL acquisition dates; pairs never mix orbit tracks.
Pair selection reflects a prior exploration of this seven-year dataset and must
not be represented as an independent confirmatory experiment.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ScenePair:
    name: str
    year: int
    orbit_pass: str
    orbit: int
    before_local: str
    after_local: str
    reason: str


PAIRS = (
    ScenePair("2022_may_expansion",2022,"ASCENDING",41,"2022-05-11","2022-05-23","large May low-VV increase"),
    ScenePair("2022_june_stable",2022,"ASCENDING",41,"2022-06-04","2022-06-28","already-high low-VV screening in June"),
    ScenePair("2023_june_expansion",2023,"ASCENDING",41,"2023-06-11","2023-06-23","large June within-orbit change"),
    ScenePair("2024_june_early_to_mid",2024,"ASCENDING",41,"2024-06-05","2024-06-17","threshold-sensitive apparent decline"),
    ScenePair("2024_june_mid_to_late",2024,"ASCENDING",41,"2024-06-17","2024-06-29","threshold-sensitive recovery"),
    ScenePair("2025_may_june_descending",2025,"DESCENDING",77,"2025-05-22","2025-06-03","extreme 3 June −19 versus −15 dB sensitivity"),
)


def select_pairs(scenes, *, names=None):
    """Map local calendar date, pass and orbit to unique actual scene IDs."""
    result=[]
    for pair in PAIRS:
        if names and pair.name not in names:
            continue
        matched=[]
        for date in (pair.before_local,pair.after_local):
            subset=scenes.loc[(scenes['local_date'].dt.strftime('%Y-%m-%d')==date)&
                              (scenes['pass']==pair.orbit_pass)&
                              (scenes.relative_orbit==pair.orbit)]
            if len(subset)!=1:
                raise ValueError(f"Expected exactly one scene for {pair.name}: {date}, found {len(subset)}")
            matched.append(subset.iloc[0].scene_id)
        result.append((pair,matched[0],matched[1]))
    return result
