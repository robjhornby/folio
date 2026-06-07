import re
import sys
import tomllib
from pathlib import Path


ALLOWED_EXPORT_KEYS = {"show_code", "slug"}
PEP_723_SCRIPT_METADATA_REGEX = (
    r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s"
    r"(?P<content>(^#(| .*)$\s)+)^# ///$"
)
SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def script_metadata(path: Path) -> dict:
    script = path.read_text(encoding="utf-8")
    # Adapted from the PEP 723 reference implementation:
    # https://peps.python.org/pep-0723/#reference-implementation
    matches = [
        match
        for match in re.finditer(PEP_723_SCRIPT_METADATA_REGEX, script)
        if match.group("type") == "script"
    ]

    if len(matches) > 1:
        raise SystemExit(f"{path}: multiple PEP 723 script metadata blocks found")
    if not matches:
        return {}

    content = "".join(
        line[2:] if line.startswith("# ") else line[1:]
        for line in matches[0].group("content").splitlines(keepends=True)
    )
    return tomllib.loads(content)


def export_options(path: Path) -> str:
    export_config = page_export_config(path)
    show_code = export_config.get("show_code", False)
    if not isinstance(show_code, bool):
        raise SystemExit(f"{path}: tool.folio.export.show_code must be a boolean")

    return "--show-code" if show_code else "--no-show-code"


def page_export_config(path: Path) -> dict:
    metadata = script_metadata(path)
    export_config = metadata.get("tool", {}).get("folio", {}).get("export", {})
    if not isinstance(export_config, dict):
        raise SystemExit(f"{path}: tool.folio.export must be a table")

    unknown_keys = set(export_config) - ALLOWED_EXPORT_KEYS
    if unknown_keys:
        unknown = ", ".join(sorted(unknown_keys))
        allowed = ", ".join(sorted(ALLOWED_EXPORT_KEYS))
        raise SystemExit(
            f"{path}: unknown tool.folio.export key(s): {unknown}; allowed: {allowed}"
        )

    return export_config


def page_slug(path: Path) -> str:
    export_config = page_export_config(path)
    slug = export_config.get("slug", path.stem.replace("_", "-"))

    if not isinstance(slug, str):
        raise SystemExit(f"{path}: tool.folio.export.slug must be a string")
    if not SLUG_REGEX.fullmatch(slug):
        raise SystemExit(
            f"{path}: tool.folio.export.slug must match {SLUG_REGEX.pattern}"
        )

    return slug


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: page_export_options.py [--slug|--export-options] PAGE")

    command = "--export-options"
    page_arg = sys.argv[1]
    if len(sys.argv) == 3:
        command = sys.argv[1]
        page_arg = sys.argv[2]

    path = Path(page_arg)
    if command == "--slug":
        print(page_slug(path))
    elif command == "--export-options":
        print(export_options(path))
    else:
        raise SystemExit(f"unknown command: {command}")



if __name__ == "__main__":
    main()
