import hashlib
import argparse
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(base_dir: Path, hashes_file: Path) -> int:
    ok = 0
    bad = 0
    missing = 0

    for line in hashes_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue

        expected, rel_path = line.split(None, 1)
        rel_path = rel_path.strip()
        target = base_dir / rel_path

        if not target.exists():
            print(f"[MISSING] {rel_path}")
            missing += 1
            continue

        actual = sha256_file(target)
        if actual.lower() == expected.lower():
            print(f"[OK] {rel_path}")
            ok += 1
        else:
            print(f"[BAD] {rel_path}")
            print(f"  expected: {expected}")
            print(f"  actual:   {actual}")
            bad += 1

    print("\n=== Summary ===")
    print(f"OK: {ok}")
    print(f"BAD: {bad}")
    print(f"MISSING: {missing}")

    return 0 if bad == 0 and missing == 0 else 1


def main():
    ap = argparse.ArgumentParser(
        description="Verify SHA256 hashes against a directory of files."
    )
    ap.add_argument("base_dir", help="Directory containing the files")
    ap.add_argument("hashes_file", help="hashes.sha256 file")
    args = ap.parse_args()

    exit(verify(Path(args.base_dir), Path(args.hashes_file)))


if __name__ == "__main__":
    main()
