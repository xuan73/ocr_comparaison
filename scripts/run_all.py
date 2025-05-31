# run_all.py

import subprocess

def run_benchmark():
    print("\n🚀 Running Benchmark Runner...")
    subprocess.run(["python", "scripts/benchmark_runner.py"], check=True)

def run_accuracy():
    print("\n🧮 Running OCR Accuracy Evaluation...")
    subprocess.run(["python", "scripts/ocr_accuracy.py"], check=True)

def run_report():
    print("\n📝 Generating OCR Benchmark Report...")
    subprocess.run(["python", "scripts/ocr_report.py"], check=True)

def main():
    run_benchmark()
    run_accuracy()
    run_report()
    print("\n✅ All tasks completed successfully!")

if __name__ == "__main__":
    main()
