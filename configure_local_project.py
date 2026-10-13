"""One-time Windows folder and boundary setup for the Hakaluki research project.

Run from its companion .bat placed next to the existing project files.
Uses Python standard library only and does not contact Earth Engine.
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STUDY_SHP = ROOT / 'Study area' / 'Hakaluki_Haor.shp'
WINDOWS_ROOT = r'F:\Wetland Test\Hakaluki_Haor_Wetland_Test_Jupyter_GEE_Project'
SETTINGS = ROOT / 'config' / 'settings.json'
NOTEBOOKS = sorted((ROOT / 'notebooks').glob('*.ipynb'))


def main():
    print('Hakaluki project: local Windows configuration')
    print('Folder:', ROOT)
    expected_folder = WINDOWS_ROOT.rsplit('\\', 1)[-1]
    if ROOT.name.casefold() != expected_folder.casefold():
        raise SystemExit(f'ERROR: This helper belongs in the {expected_folder} folder, not {ROOT.name}.')
    for required in [SETTINGS, ROOT / 'src' / 'hakaluki_core.py', ROOT / 'src' / 'ee_pipeline.py']:
        if not required.exists():
            raise SystemExit(f'ERROR: Missing project file: {required}')
    if len(NOTEBOOKS) < 5:
        raise SystemExit('ERROR: Could not find all five research notebooks in notebooks/.')
    missing = [STUDY_SHP.with_suffix(s) for s in ('.shp', '.shx', '.dbf', '.prj')
               if not STUDY_SHP.with_suffix(s).is_file()]
    if missing:
        print('\nMissing shapefile companion files:')
        for p in missing: print('  -', p)
        raise SystemExit('ERROR: Add these files alongside the .shp. Do not guess the CRS or create an empty .prj.')

    replacements = {}
    original_pattern = re.compile(r'ROOT\s*=\s*Path\(r[\'\"]F:\\Wetland Test[\'\"]\)')
    for path in NOTEBOOKS:
        notebook = json.loads(path.read_text(encoding='utf-8'))
        found_root = False
        for cell in notebook['cells']:
            if cell['cell_type'] != 'code':
                continue
            source = ''.join(cell['source'])
            new_source, n = original_pattern.subn(lambda _: 'ROOT = Path(r"' + WINDOWS_ROOT + '")', source)
            if n: found_root = True
            if path.name.startswith('00_') and ('download_candidate_boundary(' in new_source and 'boundary_audit(' in new_source):
                new_source = '''# Load the shapefile YOU supplied; do not silently download another boundary.
local_shp = ROOT / 'Study area' / 'Hakaluki_Haor.shp'
assert local_shp.exists(), f'Study-area shapefile not found: {local_shp}'
boundary_source = local_shp
source_status = 'user-supplied boundary; geometry and provenance NOT independently verified'
GDF = load_boundary(boundary_source)
AUDIT = boundary_audit(GDF)
AUDIT['source_file'] = str(boundary_source)
AUDIT['source_status'] = source_status
AUDIT['provenance'] = 'User-supplied Hakaluki_Haor.shp; independently verify original source.'
print(json.dumps(AUDIT, indent=2))
(PATHS['boundary'] / 'boundary_audit.json').write_text(json.dumps(AUDIT, indent=2))
export_candidate_geojson(GDF, PATHS['boundary'] / 'hakaluki_analysis_candidate.geojson')
make_boundary_reference_figure(GDF, PATHS['maps'] / '01_boundary_audit_candidate.png')
display(GDF.head())
'''
            cell['source'] = new_source.splitlines(keepends=True)
        if not found_root and WINDOWS_ROOT not in ''.join(''.join(c.get('source',[])) for c in notebook['cells']):
            raise SystemExit(f'ERROR: Could not find expected ROOT line in {path.name}. No changes saved.')
        if path.name.startswith('00_'):
            notebook['cells'][0]['source'] = ('''# 00 — Hakaluki Haor user-supplied boundary and Earth Engine setup

Uses `Study area/Hakaluki_Haor.shp` and its companion files. The shapefile is **user supplied, not independently verified**. Audit its coordinates, extent and provenance before final publication. No new boundary will be downloaded from GitHub by this notebook.
''').splitlines(keepends=True)
            notebook['cells'][3]['source'] = ('''## B. Audit your Hakaluki Haor shapefile

The polygon is read directly from `Study area/Hakaluki_Haor.shp`, checked for CRS and geometry, and saved to `data/boundary/hakaluki_analysis_candidate.geojson` for the other notebooks. The presence of a GIS file does not establish whether it represents the full haor, a protected-area boundary, or a seasonal inundation footprint.
''').splitlines(keepends=True)
        replacements[path] = notebook

    config = json.loads(SETTINGS.read_text(encoding='utf-8'))
    config['local_project_directory'] = WINDOWS_ROOT
    config['earth_engine_cloud_project'] = 'axial-paratext-491911-b6'
    config['boundary_source'] = 'user_supplied_shapefile_requires_validation'
    config['study_area_status'] = 'USER_SUPPLIED_UNVERIFIED'
    config['run_label'] = 'user_supplied_hakaluki_boundary_v1__2022_pilot'

    backup = ROOT / 'backup_before_local_configuration'
    backup.mkdir(exist_ok=True)
    for path in [SETTINGS, *NOTEBOOKS]:
        dest = backup / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists(): shutil.copy2(path, dest)

    SETTINGS.write_text(json.dumps(config, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for path, notebook in replacements.items():
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('\nSUCCESS: Configuration updated.')
    print('  ROOT:', WINDOWS_ROOT)
    print('  Shapefile:', str(STUDY_SHP))
    print('  Cloud project:', config['earth_engine_cloud_project'])
    print('  Notebooks updated:', len(replacements))
    print('  Originals backed up in:', backup)
    print('\nNEXT: Launch 02_start_jupyter.bat, open Notebook 00, and Run All.')
    print('NOTE: GEE authentication and spatial validation have not been performed by this helper.')

if __name__ == '__main__':
    main()
