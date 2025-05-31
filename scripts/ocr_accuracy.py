# ocr_accuracy.py

import os
import json
from pathlib import Path
from difflib import unified_diff

# Configuration
MISTRAL_OUT = Path("data/output/mistral")
DATALAB_OUT = Path("data/output/datalab")
RESULTS_DIR = Path("results")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Read Markdown content
def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

# Calculate diff ratio
def calculate_diff_ratio(mistral_lines, datalab_lines):
    diff = list(unified_diff(mistral_lines, datalab_lines))
    total_lines = max(len(mistral_lines), len(datalab_lines))
    diff_lines = sum(1 for line in diff if line.startswith("- ") or line.startswith("+ "))
    ratio = 1 - (diff_lines / total_lines) if total_lines > 0 else 1.0
    return ratio

def evaluate_accuracy():
    report = []

    mistral_files = sorted(MISTRAL_OUT.glob("*_whole.md"))
    datalab_files = sorted(DATALAB_OUT.glob("*_datalab.md"))

    for mistral_file, datalab_file in zip(mistral_files, datalab_files):
        mistral_lines = read_markdown(mistral_file)
        datalab_lines = read_markdown(datalab_file)

        diff_ratio = calculate_diff_ratio(mistral_lines, datalab_lines)

        report.append({
            "file": mistral_file.stem,
            "diff_ratio": diff_ratio
        })

    with open(RESULTS_DIR / "benchmark_accuracy.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Accuracy evaluation (Diff-based) completed. Results saved to 'results/benchmark_accuracy.json'")

if __name__ == "__main__":
    evaluate_accuracy()
