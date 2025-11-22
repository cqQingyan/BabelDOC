# Examples and sample configurations

This page summarizes the example assets bundled with BabelDOC so contributors can quickly run smoke tests or illustrate specific pipeline behaviors.

## Quick start

- Use the **standard** preset for most PDFs:
  ```bash
  babeldoc -c examples/mode_standard.toml --files ./sample.pdf --openai --openai-api-key "$OPENAI_API_KEY" --output ./output
  ```
- Switch to **compatibility** mode when fonts or layout are tricky:
  ```bash
  babeldoc -c examples/mode_compatibility.toml --files ./sample.pdf --openai --openai-api-key "$OPENAI_API_KEY" --output ./output
  ```
- Force **OCR-first** behavior for scans:
  ```bash
  babeldoc -c examples/mode_ocr_priority.toml --files ./sample.pdf --openai --openai-api-key "$OPENAI_API_KEY" --output ./output
  ```

See `examples/config_templates.md` for additional flags and troubleshooting tips.

## Asset catalog

| Path | Description |
| --- | --- |
| `examples/ci/test.pdf` | Small PDF used in continuous integration smoke tests. |
| `examples/basic.xml` | Minimal IL sample with simple paragraphs for parser and renderer sanity checks. |
| `examples/complex.xml` | Rich IL sample combining multiple layout elements to validate end-to-end translation. |
| `examples/code-figure.xml` | IL sample focused on figure blocks and monospaced code segments. |
| `examples/formular.xml` | Math-oriented IL sample containing formulas and inline expressions. |
| `examples/table.xml` | Table-heavy IL sample for verifying cell extraction and rendering. |
| `examples/config_templates.md` | Markdown reference that explains the preset TOML files and CLI usage. |
| `examples/mode_standard.toml` | Default translation pipeline settings intended for typical documents. |
| `examples/mode_compatibility.toml` | Safer preset that favors layout robustness when fonts or spacing are problematic. |
| `examples/mode_ocr_priority.toml` | Preset that prioritizes OCR for heavily scanned inputs. |

## How to extend

- Add new assets to `examples/` and briefly document their intent in this table so other contributors know when to use them.
- Mirror any new scenarios in `tests/` (for example under `tests/examples/<scenario>`).
- Prefer sharing reusable CLI flags and configurations through TOML presets instead of long command snippets.
