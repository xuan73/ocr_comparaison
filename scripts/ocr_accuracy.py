# ocr_accuracy.py

import os
import json
from pathlib import Path
import re
from difflib import unified_diff

# Configuration
MISTRAL_OUT = Path("data/output/mistral")
DATALAB_OUT = Path("data/output/datalab")
RESULTS_DIR = Path("results")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def read_markdown(file_path) -> str:
    with open(file_path, 'r', encoding='utf-8') as f1:
        return f1.read()
    return ''

def clean_text(text):
    text = re.sub(r'[.\-#<>\[\]$⋄]', ' ', text) 
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def extract_words(text):
    words = re.findall(r'\b\w+\b', text)
    return set(words)

def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0

def calculate_diff_ratio(text_mistral, text_datalab):
    cleaned_mistral = clean_text(text_mistral)
    cleaned_datalab = clean_text(text_datalab)

    words1 = extract_words(cleaned_mistral)
    words2 = extract_words(cleaned_datalab)

    return jaccard_similarity(words1, words2)


def evaluate_accuracy():
    report = []
    for file in MISTRAL_OUT.glob("*_mistral.md"):
        mistral_name = file.stem # xxx_mistral
        base_name = '_'.join(mistral_name.split('_')[:-1])
        mistral_file = MISTRAL_OUT / f"{mistral_name}.md"
        datalab_file = DATALAB_OUT / f"{base_name}_datalab.md"
        
        mistral_text = read_markdown(mistral_file)
        datalab_text = read_markdown(datalab_file)

        similarity = calculate_diff_ratio(mistral_text, datalab_text)

        report.append({
            "file": base_name,
            "similarity": similarity
        })

    with open(RESULTS_DIR / "benchmark_accuracy.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Accuracy evaluation (Similarity-based) completed. Results saved to 'results/benchmark_accuracy.json'")

if __name__ == "__main__":
    evaluate_accuracy()
