"""Unified command-line interface helper and criteria checklist tools."""
import argparse
import sys
from pathlib import Path
from typing import Optional
from . import __version__
from .criteria_config import generate_criteria_template, load_criteria_config


def add_common_a11y_args(parser: argparse.ArgumentParser) -> None:
    """Add standardized accessibility command-line arguments to any format tool parser."""
    parser.add_argument(
        "--criteria",
        type=Path,
        metavar="PATH",
        help="Path to criteria checklist file ([x]/[ ]) or YAML config for what-if exclusions.",
    )
    parser.add_argument(
        "--init-criteria",
        type=Path,
        nargs="?",
        const=Path("a11y-criteria.txt"),
        metavar="PATH",
        help="Generate a baseline criteria checklist template with all WCAG SCs pre-populated.",
    )
    parser.add_argument(
        "--format",
        nargs="+",
        choices=["md", "html", "pdf", "json"],
        default=["md", "html"],
        help="Report formats to generate (default: md html).",
    )
    parser.add_argument(
        "--theme",
        default="light",
        help="Visual theme for HTML/PDF reports (light, dark, forest, ocean, high-contrast, print).",
    )


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="engine-a11y",
        description="Core engine and tools for document accessibility auditing and remediation.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    add_common_a11y_args(parser)

    args = parser.parse_args(argv)

    if args.init_criteria:
        out = generate_criteria_template(args.init_criteria)
        print(f"Generated criteria checklist template at: {out}")
        return 0

    if args.criteria:
        inc, exc = load_criteria_config(args.criteria)
        print(f"Loaded criteria config from {args.criteria}:")
        print(f"  Active criteria: {len(inc)}")
        print(f"  Excluded criteria (what-if mode): {len(exc)}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
