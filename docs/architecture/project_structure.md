# Project structure and normalization proposals

This page summarizes the current layout of the repository and outlines pragmatic steps to normalize code, documentation, and folder structure. It is intended as a quick reference for contributors who want to keep the project organized while evolving features.

## Current repository layout (2025-03)

- `babeldoc/`: Python package containing translation pipeline, providers, parsing, rendering, and utilities.
  - `translator/`: Provider-specific integrations plus orchestration helpers.
  - `format/`: Intermediate representations and parsers (e.g., PDF IL schema, xsdata outputs).
  - `docvision/`: Layout detection and table detection helpers.
  - `pdfminer/`: Vendored/augmented pdfminer components.
  - `utils/` and `tools/`: Mixed utility modules; naming is not yet fully standardized.
- `examples/`: Sample assets for manual and automated checks.
- `tests/`: Unit and end-to-end regression coverage.
- `docs/`: MkDocs content published to the documentation site.
- `mkdocs.yml`: MkDocs configuration and navigation entrypoint.

## Normalization goals

- Make it obvious where to put new code or docs by establishing clear domains and naming rules.
- Reduce duplication between utility modules and provider implementations.
- Keep contributor-facing guidance in a single place and link it from the main README.

## Suggested actions for code structure

- **Separate core pipeline from providers**: Gradually group reusable orchestration code under a `babeldoc/core/` (or similar) namespace, and keep provider adapters in subpackages like `babeldoc/translator/providers/<provider_name>/`. This keeps the public surface easy to scan and simplifies dependency boundaries.
- **Unify utilities**: Audit `babeldoc/utils/` and `babeldoc/tools/` for overlapping helpers (logging, file IO, chunking). Move shared helpers into one namespace (e.g., `babeldoc/utils/`) and limit `tools/` to CLI-only helpers.
- **Centralize configuration**: Collect CLI/ENV configuration parsing into a single module (e.g., `babeldoc/config.py`) that can be reused by both `babeldoc/main.py` and provider factories. Include typed defaults and schema validation to reduce drift between CLI flags and runtime objects.
- **Provider template**: Standardize provider modules around consistent entrypoints such as `translate_page`, `build_prompt`, and `retry_policy`. Provide a lightweight abstract base class in `babeldoc/translator/providers/base.py` and update each provider to implement the same surface so tests can be shared.
- **Explicit staging**: Keep transformation phases separated (`ingest -> layout -> translate -> render`). Create small modules or packages for each phase with explicit inputs/outputs to make cross-cutting changes safer.

## Suggested actions for documentation

- **Add navigation buckets**: Organize MkDocs content into clear groups (e.g., `Guides`, `Reference`, `Architecture`). Place deep dives such as layout detection or cache behavior under `Architecture`.
- **Write living architecture notes**: Maintain short “How it’s wired” pages for key subsystems (pipeline stages, provider lifecycle, rendering) alongside diagrams when possible. Link these from provider docs and the README to keep new contributors oriented.
- **Document configuration sources**: Co-locate tables of CLI flags, environment variables, and config file keys so readers do not need to cross-reference README snippets.
- **Examples index**: Add a `docs/examples.md` that lists available sample assets in `/examples`, their intent, and how to run the associated tests.

## Suggested actions for folders and naming

- Use hyphen-less, lowercase directory names for new folders (e.g., `architecture`, `reference`), and prefer snake_case module names inside the package.
- Keep public artifacts (generated PDFs, cache outputs) in a dedicated top-level folder such as `artifacts/` that is gitignored; avoid mixing them into `examples/` or `tests/`.
- When adding new end-to-end scenarios, mirror the directory name inside `tests/` (e.g., `tests/examples/<scenario>` matching `examples/<scenario>`).

## Implementation checklist

- [ ] Create provider base class and migrate existing providers to the shared interface.
- [ ] Consolidate overlapping helpers in `utils/` vs `tools/` and document the chosen split.
- [ ] Add a centralized config module and update CLI + pipelines to consume it.
- [ ] Add MkDocs navigation groups (`Architecture`, `Guides`, `Reference`) and link structure pages.
- [ ] Document `examples/` usage and ensure associated tests clean up artifacts.

These recommendations can be implemented incrementally; start by codifying interfaces (providers, config) so new contributions naturally follow the normalized layout.
