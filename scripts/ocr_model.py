
import os
from pathlib import Path
import base64
import json
import time
import asyncio
import httpx
from abc import ABC, abstractmethod
from PyPDF2 import PdfReader, PdfWriter
import requests
from concurrent.futures import ThreadPoolExecutor

# Datalab imports
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# Mistral imports
from mistralai import Mistral
from util import timeit

class OcrModel(ABC):
    """Abstract base class for OCR models."""
    @abstractmethod
    def convert(self, pdf_path: str, output_md_path: str):
        """Convert a PDF file to Markdown and save to output path."""
        pass

class MistralOCR(OcrModel):
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.api_url = "https://api.mistral.ai/v1/ocr"
        self.model = "mistral-ocr-latest"
        self.client = Mistral(api_key=self.api_key)

    def encode_pdf_to_data_url(self, pdf_path):
        with open(pdf_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            return f"data:application/pdf;base64,{encoded}"

    @timeit
    def convert(self, pdf_path, output_md_path):
        data_url = self.encode_pdf_to_data_url(pdf_path)
        response = self.client.ocr.process(
            model=self.model,
            document={
                "type": "document_url",
                "document_url": data_url,
                "document_name": os.path.basename(pdf_path)
            },
            include_image_base64=False
        )
        with open(output_md_path, "w", encoding="utf-8") as f:
            for page in response.pages:
                f.write(page.markdown + "\n\n")
        print(f"[SUCCESS] Single PDF (SDK) converted: {output_md_path}")

    @timeit
    def convert_webapi(self, pdf_path, output_md_path):
        data_url = self.encode_pdf_to_data_url(pdf_path)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "document": {
                "document_url": data_url,
                "document_name": os.path.basename(pdf_path),
                "type": "document_url"
            },
            "include_image_base64": False
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                with open(output_md_path, "w", encoding="utf-8") as f:
                    for page in data.get("pages", []):
                        f.write(page.get("markdown", "") + "\n\n")
                print(f"[SUCCESS] Single PDF (Web API) converted: {output_md_path}")
            else:
                print(f"[FAILED] Web API failed (Status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"[FAILED] Web API request error: {e}")

    def split_pdf(self, input_pdf, output_dir, parts):
        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)
        if total_pages < parts:
            part_size = 1
            parts = total_pages
        else:
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

    def create_batch_jsonl(self, part_files, jsonl_output_path):
        with open(jsonl_output_path, "w", encoding="utf-8") as f:
            for idx, part_file in enumerate(part_files):
                data_url = self.encode_pdf_to_data_url(part_file)
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

    def run_batch_ocr(self, jsonl_path):
        upload = self.client.files.upload(
            file={
                "file_name": os.path.basename(jsonl_path),
                "content": open(jsonl_path, "rb")
            },
            purpose="batch"
        )
        job = self.client.batch.jobs.create(
            input_files=[upload.id],
            model=self.model,
            endpoint="/v1/ocr",
            metadata={"job_type": "split_pdf_batch"}
        )
        print(f"[→] Submitted batch job: {job.id}")

        while True:
            status = self.client.batch.jobs.get(job_id=job.id)
            done = status.succeeded_requests + status.failed_requests
            percent = round(done / status.total_requests * 100, 2)
            print(f"Status: {status.status} | Done: {done}/{status.total_requests} ({percent}%)")
            if status.status in ["SUCCESS", "FAILED", "CANCELLED"]:
                break
            time.sleep(2)

        return status.output_file

    @timeit
    def convert_split_batch(self, input_pdf, output_md, parts=5):
        part_files = self.split_pdf(input_pdf, "temp_parts_split", parts)
        batch_file = "batch_parts.jsonl"
        self.create_batch_jsonl(part_files, batch_file)
        output_file_id = self.run_batch_ocr(batch_file)

        response = self.client.files.download(file_id=output_file_id)
        text = response.read().decode("utf-8")
        results = [json.loads(line) for line in text.strip().split("\n")]
        results.sort(key=lambda r: int(r["custom_id"].split("_")[-1]))

        with open(output_md, "w", encoding="utf-8") as f:
            for r in results:
                try:
                    f.write(r["response"]["body"]["pages"][0]["markdown"])
                except:
                    print(f"[FAILED] convert_split {input_pdf}, custom_id = {r['custom_id']}")
        print(f"[SUCCESS] Batch-based OCR Markdown written to: {output_md}")

    # async def send_part_mistral(self, part_file):
    #     try:
    #         with open(part_file, "rb") as f:
    #             file_content = f.read()

    #             res = await self.client.files.upload_async(file={
    #                 "file_name": os.path.basename(part_file),
    #                 "content": file_content,
    #             })

    #             if res.status_code == 200:
    #                 data = await res.json()
    #                 md_file = os.path.join("temp_md_webapi", os.path.basename(part_file).replace(".pdf", ".md"))
    #                 with open(md_file, "w", encoding="utf-8") as f:
    #                     for page in data.get("pages", []):
    #                         f.write(page.get("markdown", "") + "\n\n")
    #                 return md_file
    #             else:
    #                 print(f"[FAILED] Upload {part_file} failed (Status {res.status_code})")
    #                 return None
    #     except Exception as e:
    #         print(f"[FAILED] Web API error on {part_file}: {e}")
    #         return None

    async def send_part(self, client, part_file):
        begin_wait = time.time()
        data_url = self.encode_pdf_to_data_url(part_file)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "document": {
                "type": "document_url",
                "document_url": data_url,
                "document_name": os.path.basename(part_file),
            },
            "include_image_base64": False
        }
        try:
            response = await client.post(self.api_url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                md_file = os.path.join("temp_md_webapi", os.path.basename(part_file).replace(".pdf", ".md"))
                with open(md_file, "w", encoding="utf-8") as f:
                    for page in data.get("pages", []):
                        f.write(page.get("markdown", "") + "\n\n")
                finish_wait = time.time()
                print(f"WAIT TIME = {finish_wait - begin_wait}")
                return md_file
            else:
                print(f"[FAILED] Part {part_file} failed (Status {response.status_code})")
                return None
        except Exception as e:
            print(f"[FAILED] Web API error on {part_file}: {e}")
            return None

    async def aync_convert_split_webapi(self, input_pdf, output_md, parts=5, max_connections=None):
        begin_split = time.time()
        part_files = self.split_pdf(input_pdf, "temp_parts_webapi", parts)
        os.makedirs("temp_md_webapi", exist_ok=True)

        limits = httpx.Limits(max_connections=max_connections, keepalive_expiry=None)
        begin_request = time.time()
        wait_time = []
        async with httpx.AsyncClient(limits=limits, timeout=60.0) as client:
            tasks = [self.send_part(client, part_file) for part_file in part_files]
            md_files = await asyncio.gather(*tasks)

        # tasks = [self.send_part_mistral(part_file) for part_file in part_files]
        # md_files = await asyncio.gather(*tasks)

        begin_merge = time.time()
        md_files = [f for f in md_files if f]
        md_files.sort(key=lambda x: int(os.path.basename(x).split("_")[-1].split(".")[0]))
        with open(output_md, "w", encoding="utf-8") as fout:
            for md_file in md_files:
                with open(md_file, "r", encoding="utf-8") as fin:
                    fout.write(fin.read() + "\n")
        finish_merge = time.time()

        print(f"[SUCCESS] Web API Split + Parallel OCR Markdown saved: {output_md}")
        print(f"SPLIT TIME = {begin_request - begin_split}, \
              REQUEST TIME = {begin_merge - begin_request}, \
              MERGE TIME = {finish_merge - begin_merge}")

    @timeit
    def convert_split_webapi(self, input_pdf, output_md, parts=5, max_connections=None):
        asyncio.run(self.aync_convert_split_webapi(input_pdf, output_md, parts=parts, max_connections=max_connections))



class DatalabOCR(OcrModel):
    def __init__(self):
        self.converter = PdfConverter(artifact_dict=create_model_dict())
        self.text_from_rendered = text_from_rendered

    @timeit
    def convert(self, pdf_path: str, output_md_path: str):
        rendered = self.converter(pdf_path)
        text, _, _ = self.text_from_rendered(rendered)
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[SUCCESS] DatalabOCR output saved to {output_md_path}")



def main():
    input_dir = Path("data/input")
    mistral_output_dir = Path("data/output/mistral")
    datalab_output_dir = Path("data/output/datalab")

    mistral_output_dir.mkdir(parents=True, exist_ok=True)
    datalab_output_dir.mkdir(parents=True, exist_ok=True)

    mistral = MistralOCR()
    datalab = DatalabOCR()


    for pdf_file in input_dir.glob("*.pdf"):
        base_name = pdf_file.stem.lower()
        # if base_name != 'cv - yuxuan wang':
        #     continue
        print(f"\n[Processing] {pdf_file.name}")

        mistral.convert(str(pdf_file), mistral_output_dir / f"{base_name}_mistral.md")
        # mistral.convert_webapi(str(pdf_file), mistral_output_dir / f"{base_name}_mistral_webapi.md")
        # mistral.convert_split_batch(str(pdf_file), mistral_output_dir / f"{base_name}_mistral_split.md", parts=4)
        begin = time.time()
        mistral.convert_split_webapi(str(pdf_file), mistral_output_dir / f"{base_name}_mistral_split_2_webapi.md", parts=2, max_connections=None)
        split_2 = time.time()
        print(f'2 parts splitted and read: {split_2 - begin}')
        mistral.convert_split_webapi(str(pdf_file), mistral_output_dir / f"{base_name}_mistral_split_4_webapi.md", parts=4, max_connections=None)
        split_4 = time.time()
        print(f'4 parts splitted and read: {split_4 - split_2}')
        mistral.convert_split_webapi(str(pdf_file), mistral_output_dir / f"{base_name}_mistral_split_8_webapi.md", parts=8, max_connections=None)
        split_8 = time.time()
        print(f'8 parts splitted and read: {split_8 - split_4}')
        mistral.convert_split_webapi(str(pdf_file), mistral_output_dir / f"{base_name}_mistral_split_16_webapi.md", parts=16, max_connections=None)
        split_16 = time.time()
        print(f'16 parts splitted and read: {split_16 - split_8}')

        # datalab.convert(str(pdf_file), datalab_output_dir / f"{base_name}_datalab.md")

if __name__ == "__main__":
    main()