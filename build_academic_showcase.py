"""Run locally from the research project root."""
from pathlib import Path
from src.academic_showcase import build

if __name__ == '__main__':
    result=build(Path(__file__).resolve().parent, publish_root_readme=False)
    for key,value in result.items():
        print(f'{key}: {value}')
    print('\nReview README_ACADEMIC_PREVIEW.md before replacing root README.md.')
