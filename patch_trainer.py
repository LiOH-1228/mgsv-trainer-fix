"""Apply or reverse the verified MGSV 1.0.15.4 trainer compatibility fix."""
import argparse
import hashlib
from pathlib import Path

ORIGINAL = 'e0e26c1138715cd38d9e68a433e62a94a8b6f1194084c4f033c05071b8feda4f'
PATCHED = '995e007ac9d25bf446e0468b71f7011a66e2f49cbf7ce127fdf6ce1246c7f86c'
REPLACEMENTS = (
    (b'8B 02 03 01 31 C9', b'8B 02 03 01 33 C9', 3),
    (b'41 8B 0C 00 89 CA', b'41 8B 0C 00 8B D1', 2),
)


def transform(data, reverse=False):
    source, target = (PATCHED, ORIGINAL) if reverse else (ORIGINAL, PATCHED)
    if hashlib.sha256(data).hexdigest() != source:
        raise ValueError('Input SHA-256 does not match the supported trainer; no output written.')
    for old, new, count in REPLACEMENTS:
        if reverse:
            old, new = new, old
        if data.count(old) != count:
            raise ValueError('Unexpected signature count; no output written.')
        data = data.replace(old, new)
    if hashlib.sha256(data).hexdigest() != target:
        raise ValueError('Output verification failed; no output written.')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path, help='New output file; existing files are never overwritten')
    parser.add_argument('--reverse', action='store_true')
    args = parser.parse_args()
    try:
        data = transform(args.input.read_bytes(), args.reverse)
        with args.output.open('xb') as stream:
            stream.write(data)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(f'Verified output: {args.output}\nSHA-256: {hashlib.sha256(data).hexdigest()}')


if __name__ == '__main__':
    main()
