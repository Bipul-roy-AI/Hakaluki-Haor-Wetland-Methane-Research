"""Tests use intentionally synthetic file fixtures only. No synthetic result is published."""
from pathlib import Path
import tempfile
import unittest
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.academic_showcase import build


class ShowcaseTest(unittest.TestCase):
    def _fixture(self, root):
        (root/'config').mkdir()
        (root/'config'/'settings.json').write_text('{}')
        (root/'data'/'processed').mkdir(parents=True)
        (root/'results'/'rasters').mkdir(parents=True)
        (root/'results'/'figures').mkdir(parents=True)
        (root/'results'/'tables').mkdir(parents=True)
        df=pd.DataFrame({'period':['2022-03','2022-04','2022-05'],
                         'year':[2022]*3,'month':[3,4,5],
                         'ch4_xch4_ppb_roi':[1900,None,1920],
                         'water_area_km2':[1,2,3],
                         'cache_fingerprint':['abc']*3})
        df.to_csv(root/'data'/'processed'/'hakaluki_monthly_2019_2025.csv',index=False)

    def test_preview_is_non_destructive_and_source_grounded(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self._fixture(root)
            (root/'README.md').write_text('Old README')
            report=build(root)
            self.assertEqual(report['months'],3)
            self.assertEqual(report['methane_available'],2)
            self.assertEqual(report['rasters'],0)
            self.assertEqual((root/'README.md').read_text(),'Old README')
            self.assertTrue((root/'docs'/'index.html').exists())
            self.assertIn('2 / 3', (root/'README_ACADEMIC_PREVIEW.md').read_text())
            self.assertEqual(json.loads((root/'docs'/'summary.json').read_text())['status'],
                             'exploratory_not_field_calibrated')

    def test_publish_saves_original_readme(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self._fixture(root)
            (root/'README.md').write_text('Original readme')
            build(root,publish_root_readme=True)
            self.assertEqual((root/'README.before_academic_showcase.md').read_text(), 'Original readme')
            self.assertIn('Hakaluki Haor', (root/'README.md').read_text())

    def test_rejects_mixed_provenance_fingerprints(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self._fixture(root)
            source=root/'data'/'processed'/'hakaluki_monthly_2019_2025.csv'
            df=pd.read_csv(source)
            df.loc[0,'cache_fingerprint']='different'
            df.to_csv(source,index=False)
            with self.assertRaises(ValueError):
                build(root)


if __name__=='__main__':
    unittest.main()
