"""Build a clean installable Calibre plugin ZIP."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parent
source = root / "vcfr_calibre"
target = root / "VCFR-Calibre.zip"
with ZipFile(target, "w", ZIP_DEFLATED) as archive:
    for path in sorted(source.iterdir()):
        if path.suffix == ".py":
            archive.write(path, path.name)
    archive.writestr("plugin-import-name-vcfr.txt", "")
print(target)
