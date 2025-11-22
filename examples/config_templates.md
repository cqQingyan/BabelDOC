# BabelDOC 模式与配置示例

## 常用场景
- 标准模式：适用于大多数 PDF。
- 高兼容模式：排版或字体异常时提升鲁棒性。
- OCR 优先模式：扫描件或文字缺失时优先走 OCR 路径。

示例命令：

```bash
# 使用标准模式直接运行
babeldoc --mode=standard --files ./sample.pdf --openai --openai-api-key "$OPENAI_API_KEY" --output ./output

# 使用高兼容模式的 TOML 配置
babeldoc -c examples/mode_compatibility.toml

# 使用 OCR 优先模式配置（扫描件）
babeldoc -c examples/mode_ocr_priority.toml
```

## 配置模板（TOML）
- `examples/mode_standard.toml`：标准模式的最小配置。
- `examples/mode_compatibility.toml`：高兼容模式，附带可选的排版安全项。
- `examples/mode_ocr_priority.toml`：OCR 优先模式，适合扫描件。

## 维护者/调试选项
以下参数保留给维护者或问题定位时使用，避免日常开启：

- `--debug`、`--show-char-box`：详细日志和字符框渲染。
- `--skip-translation`、`--only-parse-generate-pdf`：绕过翻译阶段，验证解析和渲染链路。
- `--report-interval`、`--skip-form-render` 等：性能或渲染排查时使用。

示例调试命令：

```bash
babeldoc --mode=compatibility --files ./sample.pdf --openai --openai-api-key "$OPENAI_API_KEY" --debug --show-char-box --skip-translation
```
