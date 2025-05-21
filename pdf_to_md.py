import os
import base64
import requests
from dotenv import load_dotenv
import json
from PyPDF2 import PdfReader, PdfWriter
from mistralai import Mistral
import time
from IPython.display import clear_output

from util import timeit

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")
API_URL = "https://api.mistral.ai/v1/ocr"  # Replace with official endpoint if different
client = Mistral(api_key=API_KEY)
ocr_model = "mistral-ocr-latest"

def encode_pdf_to_data_url(pdf_path):
    """Encode a PDF file to a base64 data URL format."""
    try:
        with open(pdf_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            return f"data:application/pdf;base64,{encoded}"
    except Exception as e:
        print(f"[!] Failed to encode PDF: {e}")
        return None

@timeit
def convert_pdf_to_markdown(pdf_path, output_md_path):
    """Send the PDF to Mistral OCR API and save the Markdown output."""
    data_url = encode_pdf_to_data_url(pdf_path)
    if data_url is None:
        return

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "document_url": data_url,
            "document_name": os.path.basename(pdf_path),
            "type": "document_url"
        },
        "include_image_base64": False,
        "pages": [],
        "image_limit": 0,
        "image_min_size": 0
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            with open(output_md_path, "w", encoding="utf-8") as f:
                for page in data.get("pages", []):
                    f.write(page.get("markdown", "") + "\n\n")
            print(f"[SUCCESS] Conversion completed: {output_md_path}")
        else:
            print(f"[FAILED] Conversion failed (Status {response.status_code}): {response.text}")
    except Exception as e:
        print(f"[FAILED] Request error: {e}")



def split_pdf(input_pdf, output_dir, parts):
    """Split PDF into N parts and return file paths"""
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    part_size = total_pages // parts
    os.makedirs(output_dir, exist_ok=True)
    output_files = []

    for i in range(parts):
        writer = PdfWriter()
        start = i * part_size
        end = (i + 1) * part_size if i < parts - 1 else total_pages
        for j in range(start, end):
            writer.add_page(reader.pages[j])
        out_path = os.path.join(output_dir, f"part_{i+1}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append(out_path)

    return output_files

def create_batch_jsonl(part_files, jsonl_output_path):
    with open(jsonl_output_path, "w", encoding="utf-8") as f:
        for idx, part_file in enumerate(part_files):
            data_url = encode_pdf_to_data_url(part_file)
            entry = {
                "custom_id": f"part_{idx+1}",
                "body": {
                    "document": {
                        "type": "document_url",
                        "document_url": data_url,
                        "document_name": os.path.basename(part_file),
                    },
                    "include_image_base64": False
                }
            }
            f.write(json.dumps(entry) + "\n")
    print(f"[SUCCESS] Batch JSONL created: {jsonl_output_path}")


def run_batch_ocr(jsonl_path):
    upload = client.files.upload(
        file={
            "file_name": os.path.basename(jsonl_path),
            "content": open(jsonl_path, "rb")
        },
        purpose="batch"
    )
    created_job = client.batch.jobs.create(
        input_files=[upload.id],
        model=ocr_model,
        endpoint="/v1/ocr",
        metadata={"job_type": "split_pdf_batch"}
    )
    print(f"[→] Submitted batch job: {created_job.id}")

    while True:
        job = client.batch.jobs.get(job_id=created_job.id)
        done = job.succeeded_requests + job.failed_requests
        percent = round(done / job.total_requests * 100, 2)
        print(f"Status: {job.status} | Done: {done}/{job.total_requests} ({percent}%)")
        if job.status in ["SUCCESS", "FAILED", "CANCELLED"]:
            break
        time.sleep(2)

    return job.output_file

@timeit
def convert_split_and_save_batch(input_pdf, output_md, parts: int=5):
    """Split PDF, submit batch OCR, then merge markdown output"""
    part_files = split_pdf(input_pdf, "temp_parts", parts)
    batch_file = "batch_parts.jsonl"
    create_batch_jsonl(part_files, batch_file)
    output_file_id = run_batch_ocr(batch_file)

    # Download and merge markdown
    response = client.files.download(file_id=output_file_id)
    text = response.read().decode("utf-8")
    results = [json.loads(line) for line in text.strip().split("\n")]    
    results.sort(key=lambda r: int(r["custom_id"].split("_")[-1]))

    with open(output_md, "w", encoding="utf-8") as f:
        for r in results:
            md = r["response"]['body']["pages"][0]["markdown"]
            f.write(md + "\n")

    print(f"[SUCCESS] Batch-based OCR Markdown written to: {output_md}")


if __name__ == "__main__":
    convert_pdf_to_markdown("input/NBA.pdf", "output/NBA.md")
    