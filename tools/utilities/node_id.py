"""Generate random node ids that look like git commit ids: lowercase hex.

A 40-character id carries 160 random bits, the same length as a git SHA-1.
Ids are random rather than sequential so Firestore writes keyed by them
spread across key ranges instead of hotspotting one.
Run from the repo root: .\\env\\Scripts\\python.exe tools\\utilities\\node_id.py [-n COUNT] [--length LENGTH]
"""

import argparse
import secrets

DEFAULT_LENGTH = 40  # same as a full git commit id
MIN_LENGTH = 16  # 64 random bits; shorter ids start to risk collisions in large trees
MAX_LENGTH = 64


def new_node_id(length: int = DEFAULT_LENGTH) -> str:
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError(
            f"length must be between {MIN_LENGTH} and {MAX_LENGTH}, got {length}"
        )
    # token_hex(n) returns 2n hex characters, so round up and trim for odd lengths.
    return secrets.token_hex((length + 1) // 2)[:length]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print random git-style hex node ids.")
    parser.add_argument(
        "-n", "--count", type=int, default=1, help="how many ids to print (default 1)"
    )
    parser.add_argument(
        "--length",
        type=int,
        default=DEFAULT_LENGTH,
        help=f"characters per id, {MIN_LENGTH} to {MAX_LENGTH} (default {DEFAULT_LENGTH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        ids = [new_node_id(args.length) for _ in range(args.count)]
    except ValueError as err:
        raise SystemExit(f"error: {err}") from err
    if ids:
        print("\n".join(ids))


if __name__ == "__main__":
    main()
