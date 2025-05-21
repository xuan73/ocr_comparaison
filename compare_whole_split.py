import os
from difflib import unified_diff
from concurrent.futures import ThreadPoolExecutor, as_completed # Try IOHttp

from pdf_to_md import convert_pdf_to_markdown, split_pdf, convert_split_and_save_batch
from util import timeit

NB_PROCESSES = 10

def convert_whole_and_save(input_pdf, output_md):
    """Whole document conversion using existing function"""
    convert_pdf_to_markdown(input_pdf, output_md)

@timeit
def convert_split_and_save_single_process(input_pdf, output_md, parts=5):
    """Split PDF and convert each part, then merge Markdown"""
    part_files = split_pdf(input_pdf, "temp_parts", parts)
    all_md = []

    for part_file in part_files:
        temp_md = part_file.replace(".pdf", ".md")
        convert_pdf_to_markdown(part_file, temp_md)
        with open(temp_md, "r", encoding="utf-8") as f:
            all_md.append(f.read())
        os.remove(temp_md)

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("".join(all_md))

    print(f"[SUCCESS] Merged {parts} Markdown parts to: {output_md}")

def compare_markdown_files(md1_path, md2_path):
    """Compare two Markdown files line by line and print diff summary"""
    with open(md1_path, "r", encoding="utf-8") as f1:
        lines1 = f1.readlines()
    with open(md2_path, "r", encoding="utf-8") as f2:
        lines2 = f2.readlines()

    print(f"\n[compare_markdown_files] Comparing '{md1_path}' vs '{md2_path}'...")

    diff = list(unified_diff(lines1, lines2, fromfile="whole", tofile="split", lineterm=""))
    if not diff:
        print("[compare_markdown_files] No difference found between the two markdown files.")
    else:
        print(f"[compare_markdown_files] Difference found! Showing first 20 lines of diff:")
        for line in diff[:20]:
            print(line)

    num_para_1 = sum(1 for l in lines1 if l.strip())
    num_para_2 = sum(1 for l in lines2 if l.strip())
    num_headers_1 = sum(1 for l in lines1 if l.strip().startswith("#"))
    num_headers_2 = sum(1 for l in lines2 if l.strip().startswith("#"))

    print(f"\n[compare_markdown_files] Paragraph count: whole={num_para_1}, split={num_para_2}")
    print(f"[compare_markdown_files] Header count:    whole={num_headers_1}, split={num_headers_2}")


def convert_part_to_markdown(part_file):
    """Worker function to convert a part PDF to Markdown"""
    temp_md = part_file.replace(".pdf", ".md")
    convert_pdf_to_markdown(part_file, temp_md)
    with open(temp_md, "r", encoding="utf-8") as f:
        content = f.read()
    os.remove(temp_md)
    return (part_file, content)

@timeit
def convert_split_and_save_parallel(input_pdf, output_md, parts):
    """Parallel version of split and convert process"""
    part_files = split_pdf(input_pdf, "temp_parts", parts)
    markdown_map = {}

    with ThreadPoolExecutor(max_workers=NB_PROCESSES) as executor:
        future_to_file = {executor.submit(convert_part_to_markdown, f): f for f in part_files}

        for future in as_completed(future_to_file):
            part_file, content = future.result()
            markdown_map[part_file] = content
        executor.shutdown(wait=True)

    # Reorder parts to preserve original PDF order
    ordered_parts = sorted(markdown_map.items(), key=lambda x: int(x[0].split("_")[-1].split(".")[0]))
    merged_markdown = "".join(content for _, content in ordered_parts)

    with open(output_md, "w", encoding="utf-8") as f:
        f.write(merged_markdown)

    print(f"[SUCCESS] Parallel merged {parts} Markdown parts to: {output_md}")

    


if __name__ == "__main__":
    # input_pdf = "input/nba.pdf"
    # md_whole = "output/nba_whole.md"
    # md_split = "output/nba_split.md"
    input_pdf = "input/attention.pdf"
    md_whole = "output/attention_whole.md"
    md_split = "output/attention_split.md"
    convert_whole_and_save(input_pdf, md_whole)
    convert_split_and_save_parallel(input_pdf, md_split, parts=NB_PROCESSES)
    # convert_split_and_save_batch(input_pdf, md_split, parts=NB_PROCESSES)
    compare_markdown_files(md_whole, md_split)
