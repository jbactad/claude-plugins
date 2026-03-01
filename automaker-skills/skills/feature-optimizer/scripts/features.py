#!/usr/bin/env python3
"""Automaker feature discovery and bulk operations.

Usage:
  features.py list [--status=STATUS] [--category=CATEGORY] [--field=FIELD:VALUE] [--format=FORMAT]
  features.py stats
  features.py update --filter=FIELD:VALUE --set=FIELD:VALUE [--dry-run]
  features.py get ID

Formats: table (default), json, ids

Examples:
  # List all pending features
  features.py list --status=pending

  # List by category
  features.py list --category=Core

  # Filter by any field (e.g. features with requirePlanApproval=true)
  features.py list --field=requirePlanApproval:true

  # Features with a specific planningMode
  features.py list --field=planningMode:skip

  # Show summary statistics
  features.py stats

  # Bulk set planningMode=skip on all backlog features
  features.py update --filter=status:backlog --set=planningMode:skip

  # Bulk disable plan approval on pending features (dry-run first)
  features.py update --filter=status:pending --set=requirePlanApproval:false --dry-run

  # Get full details of a single feature
  features.py get cache-policy

  # Output as JSON for piping
  features.py list --status=completed --format=json

  # Output just IDs for scripting
  features.py list --status=pending --format=ids
"""

import json
import os
import sys
from pathlib import Path


def find_features_dir() -> Path:
    """Walk up from cwd to find .automaker/features/."""
    current = Path.cwd()
    while current != current.parent:
        candidate = current / '.automaker' / 'features'
        if candidate.is_dir():
            return candidate
        current = current.parent
    print('Error: .automaker/features/ not found in any parent directory.', file=sys.stderr)
    sys.exit(1)


def load_features(features_dir: Path) -> list[dict]:
    """Load all feature.json files."""
    features = []
    for entry in sorted(features_dir.iterdir()):
        fpath = entry / 'feature.json'
        if fpath.is_file():
            with open(fpath) as f:
                features.append(json.load(f))
    return features


def matches(feature: dict, field: str, value: str) -> bool:
    """Check if a feature field matches a value (with type coercion)."""
    actual = feature.get(field)
    if actual is None:
        return value.lower() in ('none', 'null', '')
    if isinstance(actual, bool):
        return value.lower() in ('true', '1') if actual else value.lower() in ('false', '0')
    return str(actual) == value


def filter_features(features: list[dict], filters: list[tuple[str, str]]) -> list[dict]:
    """Apply all filters (AND logic)."""
    result = features
    for field, value in filters:
        result = [f for f in result if matches(f, field, value)]
    return result


def print_table(features: list[dict]) -> None:
    """Print features as a compact table."""
    if not features:
        print('No features found.')
        return
    # Determine columns
    cols = [
        ('id', 30),
        ('status', 12),
        ('category', 20),
        ('title', 40),
    ]
    header = '  '.join(name.ljust(width) for name, width in cols)
    print(header)
    print('-' * len(header))
    for f in features:
        row = '  '.join(
            str(f.get(name, ''))[:width].ljust(width) for name, width in cols
        )
        print(row)
    print(f'\n{len(features)} feature(s)')


def cmd_list(args: list[str]) -> None:
    """List features with optional filters."""
    features_dir = find_features_dir()
    features = load_features(features_dir)
    filters: list[tuple[str, str]] = []
    fmt = 'table'

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--status='):
            filters.append(('status', arg.split('=', 1)[1]))
        elif arg.startswith('--category='):
            filters.append(('category', arg.split('=', 1)[1]))
        elif arg.startswith('--field='):
            field, value = arg.split('=', 1)[1].split(':', 1)
            filters.append((field, value))
        elif arg.startswith('--format='):
            fmt = arg.split('=', 1)[1]
        i += 1

    results = filter_features(features, filters)

    if fmt == 'json':
        print(json.dumps(results, indent=2))
    elif fmt == 'ids':
        for f in results:
            print(f.get('id', ''))
    else:
        print_table(results)


def cmd_stats(args: list[str]) -> None:
    """Show feature statistics."""
    features_dir = find_features_dir()
    features = load_features(features_dir)

    statuses: dict[str, int] = {}
    categories: dict[str, int] = {}
    planning_modes: dict[str, int] = {}
    with_approval = 0

    for f in features:
        s = f.get('status', 'no-status')
        c = f.get('category', 'no-category')
        pm = f.get('planningMode', 'not-set')
        statuses[s] = statuses.get(s, 0) + 1
        categories[c] = categories.get(c, 0) + 1
        planning_modes[pm] = planning_modes.get(pm, 0) + 1
        if f.get('requirePlanApproval'):
            with_approval += 1

    print(f'Total features: {len(features)}')
    print(f'\nBy status:')
    for k, v in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f'  {k:20s} {v}')
    print(f'\nBy category:')
    for k, v in sorted(categories.items(), key=lambda x: -x[1]):
        print(f'  {k:20s} {v}')
    print(f'\nBy planning mode:')
    for k, v in sorted(planning_modes.items(), key=lambda x: -x[1]):
        print(f'  {k:20s} {v}')
    print(f'\nRequire plan approval: {with_approval}')


def cmd_update(args: list[str]) -> None:
    """Bulk update features matching a filter."""
    features_dir = find_features_dir()
    features = load_features(features_dir)
    filters: list[tuple[str, str]] = []
    updates: list[tuple[str, str]] = []
    dry_run = False

    for arg in args:
        if arg.startswith('--filter='):
            field, value = arg.split('=', 1)[1].split(':', 1)
            filters.append((field, value))
        elif arg.startswith('--set='):
            field, value = arg.split('=', 1)[1].split(':', 1)
            updates.append((field, value))
        elif arg == '--dry-run':
            dry_run = True

    if not filters:
        print('Error: --filter is required.', file=sys.stderr)
        sys.exit(1)
    if not updates:
        print('Error: --set is required.', file=sys.stderr)
        sys.exit(1)

    matched = filter_features(features, filters)
    if not matched:
        print('No features matched the filter.')
        return

    print(f'{"[DRY RUN] " if dry_run else ""}Updating {len(matched)} feature(s):')
    for field, value in updates:
        print(f'  {field} = {value}')
    print()

    for f in matched:
        fid = f.get('id', '')
        fpath = features_dir / fid / 'feature.json'
        if not fpath.is_file():
            # Try directory name matching
            for entry in features_dir.iterdir():
                candidate = entry / 'feature.json'
                if candidate.is_file():
                    with open(candidate) as fp:
                        data = json.load(fp)
                    if data.get('id') == fid:
                        fpath = candidate
                        break

        if not fpath.is_file():
            print(f'  SKIP {fid} (file not found)')
            continue

        with open(fpath) as fp:
            data = json.load(fp)

        for field, value in updates:
            # Type coercion
            if value.lower() == 'true':
                data[field] = True
            elif value.lower() == 'false':
                data[field] = False
            elif value.lower() in ('null', 'none'):
                data.pop(field, None)
            elif value.isdigit():
                data[field] = int(value)
            else:
                data[field] = value

        if dry_run:
            print(f'  WOULD UPDATE {fid}')
        else:
            with open(fpath, 'w') as fp:
                json.dump(data, fp, indent=2)
                fp.write('\n')
            print(f'  UPDATED {fid}')

    print(f'\n{"[DRY RUN] " if dry_run else ""}Done.')


def cmd_get(args: list[str]) -> None:
    """Get full details of a single feature."""
    if not args:
        print('Error: feature ID required.', file=sys.stderr)
        sys.exit(1)

    features_dir = find_features_dir()
    fid = args[0]
    fpath = features_dir / fid / 'feature.json'

    if not fpath.is_file():
        print(f'Error: feature "{fid}" not found.', file=sys.stderr)
        sys.exit(1)

    with open(fpath) as f:
        data = json.load(f)
    print(json.dumps(data, indent=2))


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', 'help'):
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    rest = sys.argv[2:]

    commands = {
        'list': cmd_list,
        'stats': cmd_stats,
        'update': cmd_update,
        'get': cmd_get,
    }

    if cmd not in commands:
        print(f'Unknown command: {cmd}', file=sys.stderr)
        print(f'Available: {", ".join(commands)}', file=sys.stderr)
        sys.exit(1)

    commands[cmd](rest)


if __name__ == '__main__':
    main()
