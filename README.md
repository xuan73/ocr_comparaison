# OCR Comparison Benchmark

This project benchmarks and compares two OCR systems:

- **Mistral OCR** (via SDK, Web API, Split + Batch, Split + Web API)
- **Datalab OCR** (Local marker model)

It measures **speed** and **accuracy** (BLEU, ROUGE) of converting PDF documents into Markdown.

## 📦 Project Structure

```
ocr_comparison_project/
├── scripts/
│   ├── ocr_model.py         # OCR Model Abstraction and Implementation
│   ├── benchmark_runner.py  # Speed Benchmark Script
│   ├── ocr_accuracy.py      # Accuracy Benchmark Script
│   ├── ocr_report.py        # Generate Markdown Report
│   ├── run_all.py           # Run all benchmarks in sequence
│   ├── util.py              # Helper functions
├── data/
│   ├── input/               # Input PDFs
│   ├── output/              # Output Markdown files
│       ├── mistral/         # Mistral OCR Outputs
│       ├── datalab/         # Datalab OCR Outputs
├── results/
│   ├── benchmark_speed.json    # Speed Benchmark Results
│   ├── benchmark_accuracy.json # Accuracy Benchmark Results
│   ├── benchmark_report.md     # Final Markdown Report
│   ├── speed_chart.png         # Speed Comparison Chart
│   ├── accuracy_chart.png      # Accuracy Comparison Chart
```

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Make sure you have:
- Mistral API Key in `.env` file as `MISTRAL_API_KEY`
- `marker` library installed
- NLTK and ROUGE libraries for accuracy evaluation

### 2. Run the Full Benchmark
```bash
python run_all.py
```

### 3. Individual Scripts
- Speed benchmark:
  ```bash
  python benchmark_runner.py
  ```
- Accuracy evaluation:
  ```bash
  python ocr_accuracy.py
  ```
- Generate report:
  ```bash
  python ocr_report.py
  ```

## 📊 Benchmark Output

- `benchmark_speed.json`: Speed results per document.
- `benchmark_accuracy.json`: Diff in percentage between Mistral whole and Datalab.
- `benchmark_report.md`: Final Markdown report with tables.
- `speed_chart.png`: Speed comparison plot.
- `accuracy_chart.png`: Accuracy comparison plot.

## 📝 Sample Report Excerpt

# OCR Benchmark Report

## Speed Benchmark

| File | Mistral Whole | Mistral WebAPI | Mistral Split | Mistral Split WebAPI | Datalab Whole |
|---|---|---|---|---|---|
| attention.pdf | 9.27s | 8.75s | 33.52s | 10.2s | 38.26s |
| NBA.pdf | 14.06s | 12.35s | 42.51s | 12.8s | 86.51s |

## Accuracy Benchmark (Diff Ratio)

| File | Diff Ratio |
|---|---|
| NBA_whole | 0.9986 |
| attention_whole | 0.9072 |
---

✅ **Ready for large-scale OCR benchmarking!**