import argparse
import sys

from bounded_contexts_linter.main import (
    check_bounded_contexts,
    check_imports_isolation,
    load_bounded_contexts,
)


def main():
    """
    Main function to run the bounded contexts linter.
    """
    parser = argparse.ArgumentParser(
        description="Bounded Contexts Linter - checks isolation between bounded contexts in DDD projects",
        prog="bc-linter",
    )

    parser.add_argument("project_dir", help="Directory of the project to analyze")

    parser.add_argument(
        "--config",
        default="bounded-contexts.toml",
        help="Path to the bounded contexts configuration file (default: <current_working_dir>/bounded-contexts.toml)",
    )

    args = parser.parse_args()

    bounded_contexts = load_bounded_contexts(args.config)

    overlaps = check_bounded_contexts(args.project_dir, args.config)

    if overlaps:
        print("Found overlapping modules between bounded contexts:", file=sys.stderr)
        for context1, context2, modules in overlaps:
            print(f"Overlap between '{context1}' and '{context2}':", file=sys.stderr)
            for module in sorted(modules):
                print(f"  - {module}", file=sys.stderr)

        raise ValueError("Found overlapping modules between bounded contexts")

    violations = check_imports_isolation(args.project_dir, bounded_contexts)

    exit_code = 0

    if violations:
        print("Found bounded contexts isolation violations:", file=sys.stderr)

        for file_path, line_number, importing_module, imported_module, message in violations:
            print(f"{file_path}:{line_number}: BC001 {message}", file=sys.stderr)

        exit_code = 1
    else:
        print("All checks have been successful!")

    sys.exit(exit_code)
