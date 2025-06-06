# OCR Comparison Benchmark

This project benchmarks and compares two OCR systems:

- **Mistral OCR** (via SDK, Web API, Split + Batch, Split + Web API)
- **Datalab OCR** (Local marker model)

It measures **speed** and **accuracy** (BLEU, ROUGE) of converting PDF documents into Markdown.

## 📦 Project Structure

```
ocr_comparison/
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
| attention.pdf | 11.51s | 11.24s | 32.02s | 12.89s | 36.58s |
| CV - Yuxuan Wang.pdf | 3.19s | 2.62s | 7.56s | 2.83s | 8.33s |

## Nb splitting 

| File | Mistral Whole | 2 parts | 4 parts | 8 parts | 16 parts |
|---|---|---|---|---|---|
| attention.pdf | 11.51s | 16.49s | 12.89s | 14.17s | 11.57s |
| CV - Yuxuan Wang.pdf | 3.19s | 2.61s | 2.83s | 2.59s | 2.11s |


## Accuracy Benchmark (Similarity)

| File | Similarity |
|---|---|
| attention | 0.9305 |
| cv - yuxuan wang | 0.9762 |

---

✅ **Ready for large-scale OCR benchmarking!**