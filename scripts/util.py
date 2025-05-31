import time
from functools import wraps
from PyPDF2 import PdfReader, PdfWriter

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        duration = end - start
        print(f"[TIMEIT] Function '{func.__name__}' executed in {duration:.4f} seconds")
        return result
    return wrapper


def time_function(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, round(end - start, 2)


def split_pdf(filepath, output_prefix, parts):
    reader = PdfReader(filepath)
    total_pages = len(reader.pages)
    part_size = total_pages // parts
    for i in range(parts):
        writer = PdfWriter()
        for j in range(i * part_size, (i + 1) * part_size if i < parts - 1 else total_pages):
            writer.add_page(reader.pages[j])
        with open(f"{output_prefix}_part{i+1}.pdf", "wb") as f:
            writer.write(f)

