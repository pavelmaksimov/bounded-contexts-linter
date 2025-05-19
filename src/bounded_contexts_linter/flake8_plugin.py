import warnings
from pathlib import Path
from typing import Generator, Tuple

from bounded_contexts_linter.main import (
    check_imports_isolation,
    load_bounded_contexts,
)


class BoundedContextLinter:
    name = "bounded-contexts-linter"
    version = "1.0.0"

    def __init__(self, tree, filename, lines, options):
        self.filename = filename
        self.options = options

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        config_path = getattr(self.options, "bc_config", None)
        if not config_path:
            warnings.warn("Bounded contexts check skipped: config path not specified")
            return

        config_path = Path(config_path).resolve()
        if not config_path.exists() or not config_path.is_file():
            warnings.warn(
                f"Bounded contexts check skipped: config file {config_path} does not exist"
            )
            return

        if len(self.options.filenames) == 0:
            warnings.warn("Bounded contexts check skipped: no project root to check")
            return

        if len(self.options.filenames) > 1:
            warnings.warn("Bounded contexts check skipped: multiple files not supported")
            return

        contexts = load_bounded_contexts(str(config_path))
        violations = check_imports_isolation(self.options.filenames[0], contexts)

        for file_path, line_number, importing_module, imported_module, message in violations:
            yield line_number, 0, f"BC001 {message}", type(self)

    @staticmethod
    def add_options(option_manager):
        option_manager.add_option(
            "--bc-config",
            type=str,
            dest="bc_config",
            help="Path to linter configuration file (bounded-contexts.toml)",
            parse_from_config=True,
            default="bounded-contexts.toml",
        )
