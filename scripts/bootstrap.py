#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from install_global import build_codex_spec, run_bootstrap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the minimal Codex bootstrap for Everything Automate."
    )
    parser.add_argument(
        "--provider",
        default="codex",
        choices=("codex",),
        help="Compatibility flag; only codex is supported.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Override the target Codex global root for testing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.provider != "codex":
        raise ValueError(f"Unsupported provider: {args.provider}")

    spec = build_codex_spec(args.codex_home)
    return run_bootstrap(spec)


if __name__ == "__main__":
    raise SystemExit(main())
