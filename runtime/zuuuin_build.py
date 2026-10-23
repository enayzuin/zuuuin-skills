"""Dependency-free PEP 517 wheel builder for an approved local runtime artifact."""
import base64
import csv
import hashlib
import io
from pathlib import Path
import zipfile

NAME = "zuuuin_engine"
VERSION = "0.1.1"
DIST = f"{NAME}-{VERSION}.dist-info"


def get_requires_for_build_wheel(config_settings=None):
    return []


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    root=Path(__file__).resolve().parent
    target=Path(wheel_directory);target.mkdir(parents=True,exist_ok=True)
    filename=f"{NAME}-{VERSION}-py3-none-any.whl"
    entries={}
    for p in sorted((root/NAME).rglob("*.py")):
        if p.is_symlink():raise ValueError("Runtime source symlink refused")
        entries[p.relative_to(root).as_posix()]=p.read_bytes()
    license_file = root / "LICENSE"
    if license_file.is_symlink() or not license_file.is_file():
        raise ValueError("Selected runtime license required")
    entries[DIST+"/licenses/LICENSE"] = license_file.read_bytes()
    entries[DIST+"/METADATA"]=(f"Metadata-Version: 2.4\nName: zuuuin-engine\nVersion: {VERSION}\nSummary: Local supervised Zuuuin engine runtime\nRequires-Python: >=3.10\nAuthor: enayzuin\nAuthor-email: 42486373+enayzuin@users.noreply.github.com\nLicense-Expression: MIT\nLicense-File: LICENSE\nProject-URL: Source, https://github.com/enayzuin/zuuuin-skills\nProject-URL: Documentation, https://enayzuin.github.io/zuuuin-skills/\nClassifier: Operating System :: POSIX\n\n").encode()
    entries[DIST+"/WHEEL"]=b"Wheel-Version: 1.0\nGenerator: zuuuin-local-stdlib\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    record=io.StringIO();writer=csv.writer(record,lineterminator="\n")
    for path,data in sorted(entries.items()):
        checksum=base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
        writer.writerow([path,"sha256="+checksum,len(data)])
    writer.writerow([DIST+"/RECORD","",""])
    entries[DIST+"/RECORD"]=record.getvalue().encode()
    with zipfile.ZipFile(target/filename,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        for path,data in sorted(entries.items()):
            info=zipfile.ZipInfo(path,date_time=(2020,1,1,0,0,0));info.external_attr=0o100644<<16
            archive.writestr(info,data)
    return filename
