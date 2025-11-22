from __future__ import annotations

import shutil
from pathlib import Path

import importlib.util
import pytest

if importlib.util.find_spec("pymupdf") is None:
    pytest.skip("pymupdf is required for pipeline tests", allow_module_level=True)

try:  # pragma: no cover - handled by pytest skip
    import numpy as np
except ImportError:  # pragma: no cover - handled by pytest skip
    np = None

import pymupdf

from babeldoc.format.pdf import high_level
from babeldoc.format.pdf.translation_config import TranslationConfig
from babeldoc.format.pdf.translation_config import TranslateResult
from babeldoc.format.pdf.translation_config import WatermarkOutputMode
from babeldoc.translator.translator import BaseTranslator


class StubTranslator(BaseTranslator):
    name = "stub"

    def __init__(self, lang_in: str = "en", lang_out: str = "en"):
        super().__init__(lang_in=lang_in, lang_out=lang_out, ignore_cache=True)

    def do_translate(self, text, rate_limit_params=None):
        return f"{text} [translated]"

    def do_llm_translate(self, text, rate_limit_params=None):
        return self.do_translate(text, rate_limit_params=rate_limit_params)


def _create_sample_pdf(tmp_path: Path) -> Path:
    if pymupdf is None:
        pytest.skip("pymupdf is required to build sample PDFs")
    doc = pymupdf.open()
    table_text = "Table: R1C1 | R1C2\nR2C1 | R2C2"
    formula_text = "Formula: E = mc^2"
    pages = [
        "Page 1 body text\n" + table_text + "\n" + formula_text,
        "Page 2 body text\nMore content on the next page.",
    ]
    for content in pages:
        page = doc.new_page()
        page.insert_text((72, 72), content, fontsize=12)
    pdf_path = tmp_path / "input.pdf"
    doc.save(pdf_path)
    return pdf_path


def _render_first_page_bytes(pdf_path: Path) -> bytes:
    doc = pymupdf.open(pdf_path)
    pixmap = doc[0].get_pixmap()
    return pixmap.tobytes()


def _stub_do_translate_single(pm, translation_config: TranslationConfig) -> TranslateResult:
    if pymupdf is None:
        pytest.skip("pymupdf is required for stubbed pipeline")
    input_doc = pymupdf.open(translation_config.input_file)
    out_doc = pymupdf.open()

    for page in input_doc:
        source_text = page.get_text("text").strip()
        translation = translation_config.translator.translate(source_text)

        original_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
        original_page.insert_text((72, 72), source_text, fontsize=12)
        if translation_config.watermark_output_mode != WatermarkOutputMode.NoWatermark:
            original_page.insert_text(
                (72, page.rect.height - 72),
                "WATERMARK",
                fontsize=16,
                rotate=45,
                color=(0.7, 0.7, 0.7),
            )

        if translation_config.use_alternating_pages_dual:
            translated_page = out_doc.new_page(
                width=page.rect.width, height=page.rect.height
            )
            translated_page.insert_text((72, 72), translation, fontsize=12)
            if (
                translation_config.watermark_output_mode
                == WatermarkOutputMode.Both
            ):
                translated_page.insert_text(
                    (72, page.rect.height - 72),
                    "WATERMARK",
                    fontsize=16,
                    rotate=45,
                    color=(0.7, 0.7, 0.7),
                )
        else:
            original_page.insert_text(
                (page.rect.width / 2, 72), translation, fontsize=12
            )

    output_dir = Path(translation_config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dual_path = output_dir / "dual.pdf"
    out_doc.save(dual_path)

    return TranslateResult(mono_pdf_path=None, dual_pdf_path=dual_path)


@pytest.fixture()
def sample_pdf(tmp_path: Path) -> Path:
    return _create_sample_pdf(tmp_path)


@pytest.fixture()
def stubbed_pipeline(monkeypatch):
    if pymupdf is None:
        pytest.skip("pymupdf is required for stubbed pipeline")
    monkeypatch.setattr(high_level, "_do_translate_single", _stub_do_translate_single)


def test_dual_pagination_and_visual_diff(sample_pdf, tmp_path, stubbed_pipeline):
    if np is None:
        pytest.skip("numpy is required for pixel-level comparison")
    translator = StubTranslator()
    output_dir = tmp_path / "out"
    working_dir = tmp_path / "work"

    config = TranslationConfig(
        input_file=str(sample_pdf),
        translator=translator,
        lang_in="en",
        lang_out="zh",
        use_alternating_pages_dual=True,
        watermark_output_mode=WatermarkOutputMode.Both,
        enhance_compatibility=True,
        working_dir=working_dir,
        output_dir=output_dir,
        use_rich_pbar=False,
    )

    first_result = high_level.translate(config)
    assert first_result.dual_pdf_path.is_file()

    dual_doc = pymupdf.open(first_result.dual_pdf_path)
    assert dual_doc.page_count == 4
    assert any("[translated]" in dual_doc[i].get_text("text") for i in range(dual_doc.page_count))
    assert "WATERMARK" in dual_doc[0].get_text("text")

    second_output_dir = tmp_path / "out_second"
    second_config = TranslationConfig(
        input_file=str(sample_pdf),
        translator=translator,
        lang_in="en",
        lang_out="zh",
        use_alternating_pages_dual=True,
        watermark_output_mode=WatermarkOutputMode.Both,
        enhance_compatibility=True,
        working_dir=tmp_path / "work_second",
        output_dir=second_output_dir,
        use_rich_pbar=False,
    )
    second_result = high_level.translate(second_config)

    first_bytes = _render_first_page_bytes(first_result.dual_pdf_path)
    second_bytes = _render_first_page_bytes(second_result.dual_pdf_path)
    assert np.array_equal(np.frombuffer(first_bytes, dtype=np.uint8), np.frombuffer(second_bytes, dtype=np.uint8))


@pytest.mark.parametrize(
    "enhance_compatibility,use_alternating_pages_dual,ocr_workaround",
    [
        (True, True, False),
        (False, True, True),
        (True, False, True),
    ],
)
def test_option_matrix_runs_pipeline(
    sample_pdf,
    tmp_path,
    stubbed_pipeline,
    enhance_compatibility,
    use_alternating_pages_dual,
    ocr_workaround,
):
    config = TranslationConfig(
        input_file=str(sample_pdf),
        translator=StubTranslator(),
        lang_in="en",
        lang_out="fr",
        use_alternating_pages_dual=use_alternating_pages_dual,
        watermark_output_mode=WatermarkOutputMode.Watermarked,
        enhance_compatibility=enhance_compatibility,
        ocr_workaround=ocr_workaround,
        working_dir=tmp_path / "work",
        output_dir=tmp_path / f"out_{enhance_compatibility}_{use_alternating_pages_dual}_{ocr_workaround}",
        use_rich_pbar=False,
    )

    result = high_level.translate(config)
    assert result.dual_pdf_path.is_file()

    generated = pymupdf.open(result.dual_pdf_path)
    assert generated.page_count >= (2 if use_alternating_pages_dual else 1)
    text_content = "\n".join(generated[0].get_text("text").splitlines())
    assert "[translated]" in text_content

    if enhance_compatibility:
        assert config.skip_clean
        assert config.dual_translate_first
    if ocr_workaround:
        assert config.skip_scanned_detection

    if config.output_dir.exists():
        shutil.rmtree(config.output_dir)
