import os
import json
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from ocr_model import MistralOCR, DatalabOCR, OcrModel
from util import timeit

# Configuration
DATA_DIR = Path("data/input")
MISTRAL_OUT = Path("data/output/mistral")
DATALAB_OUT = Path("data/output/datalab")
RESULTS_DIR = Path("results")

for directory in [MISTRAL_OUT, DATALAB_OUT, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Helper function for timing
def time_function(func, *args, **kwargs):
    total = 0
    for i in range(3):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        total += end - start
    return round(total / 3.0, 2)

# OCR Runner
class OCRBenchmark:
    def __init__(self, ocr_model: OcrModel):
        self.ocr_model = ocr_model

    def run_whole(self, pdf_path, output_md_path):
        duration = time_function(self.ocr_model.convert, str(pdf_path), output_md_path)
        return duration

    def run_webapi(self, pdf_path, output_md_path):
        duration = time_function(self.ocr_model.convert_webapi, str(pdf_path), output_md_path)
        return duration

    def run_split_batch(self, pdf_path, output_md_path, parts=5):
        duration = time_function(self.ocr_model.convert_split_batch, str(pdf_path), output_md_path, parts)
        return duration

    def run_split_webapi(self, pdf_path, output_md_path, parts=5):
        duration = time_function(self.ocr_model.convert_split_webapi, str(pdf_path), output_md_path, parts)
        return duration

# Main benchmark process
def main():
    # Initialize models
    mistral_model = MistralOCR()
    datalab_model = DatalabOCR()

    # Initialize benchmark runners
    mistral_benchmark = OCRBenchmark(mistral_model)
    datalab_benchmark = OCRBenchmark(datalab_model)

    report = []

    for pdf in DATA_DIR.glob("*.pdf"):
        base_name = pdf.stem
        # if base_name == '2021PVAG':
        #     continue

        print(f"\n[Processing] {pdf.name}")

        # Mistral Whole
        mistral_whole_md = MISTRAL_OUT / f"{base_name}_mistral.md"
        mistral_whole_time = mistral_benchmark.run_whole(pdf, mistral_whole_md)

        # Mistral WebAPI
        mistral_webapi_md = MISTRAL_OUT / f"{base_name}_webapi.md"
        mistral_webapi_time = mistral_benchmark.run_webapi(pdf, mistral_webapi_md)

        # Mistral Split + Batch
        mistral_split_md = MISTRAL_OUT / f"{base_name}_split.md"
        mistral_split_time = mistral_benchmark.run_split_batch(pdf, mistral_split_md, parts=4)

        # Mistral Split + WebAPI
        mistral_split_webapi_md = MISTRAL_OUT / f"{base_name}_split_2_webapi.md"
        mistral_split_2_webapi_time = mistral_benchmark.run_split_webapi(pdf, mistral_split_webapi_md, parts=2)

        mistral_split_webapi_md = MISTRAL_OUT / f"{base_name}_split_4_webapi.md"
        mistral_split_4_webapi_time = mistral_benchmark.run_split_webapi(pdf, mistral_split_webapi_md, parts=4)

        mistral_split_webapi_md = MISTRAL_OUT / f"{base_name}_split_8_webapi.md"
        mistral_split_8_webapi_time = mistral_benchmark.run_split_webapi(pdf, mistral_split_webapi_md, parts=8)

        mistral_split_webapi_md = MISTRAL_OUT / f"{base_name}_split_16_webapi.md"
        mistral_split_16_webapi_time = mistral_benchmark.run_split_webapi(pdf, mistral_split_webapi_md, parts=16)

        # Datalab Whole
        datalab_whole_md = DATALAB_OUT / f"{base_name}_datalab.md"
        if base_name == '2021PVAG':
            datalab_whole_time = 0
        else:
            datalab_whole_time = datalab_benchmark.run_whole(pdf, datalab_whole_md)

        report.append({
            "file": pdf.name,
            "mistral_whole_time": mistral_whole_time,
            "mistral_webapi_time": mistral_webapi_time,
            "mistral_split_batch_time": mistral_split_time,
            "mistral_split_2_webapi_time": mistral_split_2_webapi_time,
            "mistral_split_4_webapi_time": mistral_split_4_webapi_time,
            "mistral_split_8_webapi_time": mistral_split_8_webapi_time,
            "mistral_split_16_webapi_time": mistral_split_16_webapi_time,
            "datalab_whole_time": datalab_whole_time
        })

    # Save report
    with open(RESULTS_DIR / "benchmark_speed.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Benchmark completed. Results saved to 'results/benchmark_speed.json'")

if __name__ == "__main__":
    main()