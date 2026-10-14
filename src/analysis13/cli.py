"""Command-line entry for the six-stage local analysis.

Run from research root: python -m src.analysis13.cli preflight --root .
No command pushes to GitHub or reprocesses large satellite data unless explicitly
chosen (13A and 13B require Earth Engine; 13F-L2 requires NetCDF input).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import preflight, project_root


def build_parser():
    p=argparse.ArgumentParser(description="Hakaluki 13A–13F integrated research pipeline; local only")
    p.add_argument('stage',choices=['preflight','offline','radiometry','spatial','hydrology',
                                     'validation-design','validation-score','methane-box','methane-l2'])
    p.add_argument('--root',default=None,help='Research project folder; default autodetect')
    p.add_argument('--scene-csv',default=None,help='Existing scene12 CSV (offline stage only)')
    p.add_argument('--output-root',default=None,help='Alternative output folder for offline analyses')
    p.add_argument('--pairs',nargs='*',default=None,help='Pair IDs defined in src/analysis13/pairs.py')
    p.add_argument('--points',type=int,default=550,help='Fixed-coordinate SAR point samples in 13A')
    p.add_argument('--force',action='store_true',help='Recompute cached SAR scene rasters (13B)')
    p.add_argument('--stage-file',default=None,help='Real stage_observations CSV path, 13D')
    p.add_argument('--upstream-file',default=None,help='Real upstream_rain CSV path, 13D')
    p.add_argument('--raster',default=None,help='4-band matched SAR GeoTIFF for validation design')
    p.add_argument('--scene-id',default=None,help='Actual scene ID used for validation sampling')
    p.add_argument('--labelled-csv',default=None,help='Completed independently interpreted labels')
    p.add_argument('--scenarios',default=None,help='Explicit hypothetical methane scenario CSV')
    p.add_argument('--l2-dir',default=None,help='Directory of native TROPOMI L2 CH4 .nc products')
    return p


def run(args):
    root=project_root(args.root)
    stage=args.stage
    if stage=='preflight':
        return preflight(root)
    if stage=='offline':
        from .offline import run_offline
        return run_offline(root,scene_file=Path(args.scene_csv) if args.scene_csv else None,
                           output_root=Path(args.output_root) if args.output_root else None)
    if stage=='radiometry':
        from .radiometry import run_radiometry
        return run_radiometry(root,n_points=args.points,pair_names=args.pairs)
    if stage=='spatial':
        from .spatial import run_spatial
        return run_spatial(root,pair_names=args.pairs,force=args.force)
    if stage=='hydrology':
        from .hydrology import run_hydrology
        return run_hydrology(root,stage_path=Path(args.stage_file) if args.stage_file else None,
                             upstream_path=Path(args.upstream_file) if args.upstream_file else None)
    if stage=='validation-design':
        if not args.raster or not args.scene_id:
            raise ValueError('Supply --raster and --scene-id for actual scene reference design')
        from .validation import make_sample
        return make_sample(root,Path(args.raster),scene_id=args.scene_id)
    if stage=='validation-score':
        from .validation import score_reference
        return score_reference(root,labels=Path(args.labelled_csv) if args.labelled_csv else None)
    if stage=='methane-box':
        from .methane import run_detectability
        template=Path(__file__).resolve().parents[2]/'data_templates'/'methane_hypothetical_scenarios.csv'
        # When the source library is merged into the project, templates live
        # in the same project root, not inside src/.
        default=root/'data_templates'/'methane_hypothetical_scenarios.csv'
        location=Path(args.scenarios) if args.scenarios else (default if default.exists() else template)
        return run_detectability(root,location)
    if stage=='methane-l2':
        if not args.l2_dir:
            raise ValueError('Provide native L2 files via --l2-dir; never substitute L3 CSV')
        from .methane import run_l2_audit
        return run_l2_audit(root,Path(args.l2_dir))
    raise ValueError(f'Unexpected stage {stage}')


def main():
    args=build_parser().parse_args()
    result=run(args)
    print(json.dumps(result,indent=2,default=str))
    return result


if __name__=='__main__':
    main()
