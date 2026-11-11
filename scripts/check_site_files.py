"""Validate the explicit list of files selected for the browser reading site."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = ROOT / 'site-files.txt'
    if not manifest.is_file():
        raise SystemExit('Create site-files.txt with the reviewed report and asset paths.')
    selected = [line.strip() for line in manifest.read_text().splitlines() if line.strip()]
    errors = []
    if not selected:
        errors.append('The website file list is empty.')
    if len(selected) != len(set(selected)):
        errors.append('The website file list contains duplicate paths.')
    for rel in selected:
        path = ROOT / rel
        if Path(rel).is_absolute() or '..' in Path(rel).parts or '.git' in Path(rel).parts:
            errors.append(f'Invalid website path: {rel}')
        elif Path(rel).as_posix() != rel:
            errors.append(f'Use a normalized repository-relative path: {rel}')
        elif path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            errors.append(f'Missing or unsafe file: {rel}')
        elif path.stat().st_size >= 100 * 1024 * 1024:
            errors.append(f'File is too large for this static reading site: {rel}')
    if 'README.md' not in selected:
        errors.append('Select README.md as the project overview.')
    if errors:
        raise SystemExit('Website file check failed:\n' + '\n'.join(errors))
    print(f'Website file check passed: {len(selected)} selected files.')


if __name__ == '__main__':
    main()

