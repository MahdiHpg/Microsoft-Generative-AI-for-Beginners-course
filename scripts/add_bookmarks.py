# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
active_marker = BASE_DIR / ".active_pdf.txt"
if active_marker.is_file():
    with open(active_marker, "r", encoding="utf-8") as f:
        PDF_PATH = Path(f.read().strip())
else:
    PDF_PATH = BASE_DIR / "Microsoft-Generative-AI-Beginners-FA.pdf"

from build_book import CHAPTERS_META

def inject_bookmarks():
    doc = pymupdf.open(str(PDF_PATH))
    print(f"Loaded PDF with {len(doc)} pages.")

    # Collect destination pages from the TOC internal links on pages 2-5 (0-indexed)
    dest_pages = []
    for p_idx in range(1, 6):
        for l in doc[p_idx].get_links():
            dest = l.get('page')
            if dest is not None:
                dest_pages.append(dest + 1) # 1-based page

    print(f"Discovered {len(dest_pages)} chapter destination pages.")

    toc_entries = [
        [1, "🎨 جلد کتاب و مشخصات اثر", 1],
        [1, "🌱 پیش‌گفتار و سناریوی استارتاپ ما", 2],
        [1, "📑 فهرست مطالب و پیش‌فصل‌ها", 3]
    ]

    for idx, ch in enumerate(CHAPTERS_META):
        if idx < len(dest_pages):
            page_target = dest_pages[idx]
            toc_entries.append([1, f"درس {ch['num']}: {ch['title']}", page_target])
            print(f"  Bookmark: درس {ch['num']} -> Page {page_target}")

    doc.set_toc(toc_entries)
    
    temp_out = BASE_DIR / "temp_bookmarked.pdf"
    doc.save(str(temp_out), garbage=3, deflate=True)
    doc.close()

    temp_out.replace(PDF_PATH)
    print(f"✅ Successfully injected {len(toc_entries)} bookmarks into {PDF_PATH.name}!")

if __name__ == "__main__":
    inject_bookmarks()
