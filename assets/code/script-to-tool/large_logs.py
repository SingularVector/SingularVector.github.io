import argparse
import json
from pathlib import Path
import sys


def positive_bytes(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1 byte")
    return number


def scan_logs(folder, minimum_bytes):
    rows = []
    for item in sorted(folder.iterdir()):
        if item.is_symlink() or item.suffix != ".log":
            continue
        if item.is_file():
            size = item.stat().st_size
            if size >= minimum_bytes:
                rows.append({"path": str(item), "bytes": size})
    return rows


def main():
    parser = argparse.ArgumentParser(description="Report large log files.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--minimum-bytes", type=positive_bytes,
                        default=104857600)
    args = parser.parse_args()
    try:
        rows = scan_logs(args.path, args.minimum_bytes)
    except OSError as error:
        print(f"Scan failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
