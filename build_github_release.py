"""One-click Windows export; no Earth Engine credentials needed for local packaging."""
from pathlib import Path
from src.portfolio_export import build_release

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    print('Project root:',root)
    report=build_release(root,include_rasters=False)
    for key,value in report.items():
        print(f'{key}: {value}')
    print('PORTFOLIO: Open results/github_release/index.html')
    print('GITHUB: Upload the contents of results/github_release to your repository.')
