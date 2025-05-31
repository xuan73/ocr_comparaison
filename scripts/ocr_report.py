# ocr_report.py

import json
from pathlib import Path
import matplotlib.pyplot as plt

# Configuration
RESULTS_DIR = Path("results")
REPORT_PATH = RESULTS_DIR / "benchmark_report.md"

# Load Results
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_report():
    speed_data = load_json(RESULTS_DIR / "benchmark_speed.json")
    accuracy_data = load_json(RESULTS_DIR / "benchmark_accuracy.json")

    # Create Markdown Report
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# OCR Benchmark Report\n\n")

        # Speed Results
        f.write("## Speed Benchmark\n\n")
        f.write("| File | Mistral Whole | Mistral WebAPI | Mistral Split | Mistral Split WebAPI | Datalab Whole |\n")
        f.write("|---|---|---|---|---|---|\n")
        for entry in speed_data:
            f.write(f"| {entry['file']} | {entry['mistral_whole_time']}s | {entry['mistral_webapi_time']}s | {entry['mistral_split_batch_time']}s | {entry['mistral_split_webapi_time']}s | {entry['datalab_whole_time']}s |\n")

        f.write("\n")

        # Accuracy Results
        f.write("## Accuracy Benchmark (Diff Ratio)\n\n")
        f.write("| File | Diff Ratio |\n")
        f.write("|---|---|\n")
        for entry in accuracy_data:
            f.write(f"| {entry['file']} | {entry['diff_ratio']:.4f} |\n")

        f.write("\n")

    print(f"\n✅ Report generated: {REPORT_PATH}")

    # Create Charts
    create_charts(speed_data, accuracy_data)

def create_charts(speed_data, accuracy_data):
    # Speed Chart
    files = [d['file'] for d in speed_data]
    mistral_whole = [d['mistral_whole_time'] for d in speed_data]
    mistral_webapi = [d['mistral_webapi_time'] for d in speed_data]
    mistral_split_batch = [d['mistral_split_batch_time'] for d in speed_data]
    mistral_split_webapi = [d['mistral_split_webapi_time'] for d in speed_data]
    datalab_whole = [d['datalab_whole_time'] for d in speed_data]

    plt.figure(figsize=(12, 6))
    plt.plot(files, mistral_whole, label='Mistral Whole')
    plt.plot(files, mistral_webapi, label='Mistral WebAPI')
    plt.plot(files, mistral_split_batch, label='Mistral Split Batch')
    plt.plot(files, mistral_split_webapi, label='Mistral Split WebAPI')
    plt.plot(files, datalab_whole, label='Datalab Whole')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Time (s)')
    plt.title('OCR Speed Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "speed_chart.png")

    # Accuracy Chart
    accuracy_files = [d['file'] for d in accuracy_data]
    diff_ratios = [d['diff_ratio'] for d in accuracy_data]

    plt.figure(figsize=(12, 6))
    plt.bar(accuracy_files, diff_ratios, label='Diff Ratio')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0.85, 1)
    plt.ylabel('Diff Ratio (1 = Perfect Match)')
    plt.title('OCR Diff Ratio Comparison')
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "accuracy_chart.png")
    

if __name__ == "__main__":
    generate_report()