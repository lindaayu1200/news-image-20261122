#!/usr/bin/env python3
"""Copy entry.png to MAKEFUN_OUTPUT_DIR, verifying it is a valid 1024x1024 PNG.

Uses only the Python standard library. Before copying, the source file is
checked for the PNG signature, an IHDR chunk reporting exactly 1024x1024
pixels, and a trailing IEND chunk, and that the file is at most 1 MiB.
"""

import os
import shutil
import struct
import sys

# Location of the entry image, relative to this script.
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

MAX_BYTES = 1 * 1024 * 1024  # At most 1 MiB.
EXPECTED_SIZE = (1024, 1024)  # Required pixel dimensions.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IHDR_LENGTH = 13  # Fixed payload length of the IHDR chunk.


def verify_png(path: str) -> None:
    """Exit with an error unless path is a valid, correctly-sized PNG.

    Checks: PNG signature, IHDR width/height, IEND trailer, and 1 MiB limit.
    """
    try:
        with open(path, "rb") as fh:
            # 1. PNG signature.
            if fh.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
                sys.exit(f"error: {path} does not start with the PNG signature")

            # 2. First chunk must be IHDR with the required dimensions.
            #    Layout: 4-byte length, 4-byte type, then the 13-byte payload.
            header = fh.read(4 + 4 + IHDR_LENGTH)
            if len(header) < 4 + 4 + IHDR_LENGTH:
                sys.exit(f"error: {path} is too short to contain an IHDR chunk")
            length, chunk_type = struct.unpack(">I4s", header[:8])
            if chunk_type != b"IHDR" or length != IHDR_LENGTH:
                sys.exit(f"error: {path} does not begin with a valid IHDR chunk")
            width, height = struct.unpack(">II", header[8:16])
            if (width, height) != EXPECTED_SIZE:
                sys.exit(
                    f"error: {path} is {width}x{height}, "
                    f"expected {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}"
                )
            fh.seek(4, os.SEEK_CUR)  # Skip the IHDR chunk's CRC.

            # 3. Scan chunks to find the terminating IEND chunk.
            while True:
                head = fh.read(8)
                if len(head) < 8:
                    sys.exit(f"error: {path} is missing the IEND chunk")
                (length,), chunk_type = struct.unpack(">I", head[:4]), head[4:8]
                if chunk_type == b"IEND":
                    break
                fh.seek(length + 4, os.SEEK_CUR)  # Skip payload + CRC.

            # 4. Size limit.
            fh.seek(0, os.SEEK_END)
            if fh.tell() > MAX_BYTES:
                sys.exit(f"error: {path} is larger than 1 MiB")

    except OSError as exc:
        sys.exit(f"error: cannot read {path}: {exc}")


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    verify_png(SRC)
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    size = os.path.getsize(dst)
    print(dst)
    print(size)


if __name__ == "__main__":
    main()
