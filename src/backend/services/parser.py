import os
import re
import fitz  # PyMuPDF
from pathlib import Path
from src.backend.config import UPLOAD_DIR
from src.backend.models.schemas import TextbookDetail, Chapter, ParseStatus


def parse_textbook(file_path: str) -> TextbookDetail:
    ext = Path(file_path).suffix.lower()
    filename = os.path.basename(file_path)
    file_id = f"book_{hash(filename) % 100000:05d}"

    if ext == ".pdf":
        return _parse_pdf(file_path, file_id, filename)
    elif ext == ".md":
        return _parse_markdown(file_path, file_id, filename)
    elif ext == ".txt":
        return _parse_txt(file_path, file_id, filename)
    else:
        raise ValueError(f"不支持的格式: {ext}")


def _parse_pdf(file_path: str, file_id: str, filename: str) -> TextbookDetail:
    doc = fitz.open(file_path)
    chapters = []
    full_text = ""
    current_chapter = None
    chapter_idx = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        full_text += text

        chapter_match = re.match(r'^第[一二三四五六七八九十\d]+章\s+.+', text.strip())

        if chapter_match or page_num == 0:
            if current_chapter:
                current_chapter.page_end = page_num
                current_chapter.content = current_chapter.content.strip()
                current_chapter.char_count = len(current_chapter.content)
                chapters.append(current_chapter)

            chapter_idx += 1
            title = chapter_match.group(0) if chapter_match else "前言/目录"
            current_chapter = Chapter(
                chapter_id=f"ch_{chapter_idx:02d}",
                title=title,
                page_start=page_num + 1,
                page_end=page_num + 1,
                content=text,
                char_count=len(text)
            )
        elif current_chapter:
            current_chapter.content += "\n" + text

    if current_chapter:
        current_chapter.page_end = len(doc)
        current_chapter.content = current_chapter.content.strip()
        current_chapter.char_count = len(current_chapter.content)
        chapters.append(current_chapter)

    doc.close()

    title = filename.replace(".pdf", "").replace(".PDF", "")
    size = os.path.getsize(file_path)

    return TextbookDetail(
        id=file_id,
        filename=filename,
        title=title,
        format="pdf",
        size_bytes=size,
        status=ParseStatus.DONE,
        total_pages=len(doc),
        total_chars=len(full_text),
        chapters=chapters
    )


def _parse_markdown(file_path: str, file_id: str, filename: str) -> TextbookDetail:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chapters = []
    sections = re.split(r'\n(?=## )', content)

    for i, section in enumerate(sections):
        lines = section.strip().split("\n")
        title = lines[0].replace("# ", "").replace("## ", "").strip()
        body = "\n".join(lines[1:]).strip()

        chapters.append(Chapter(
            chapter_id=f"ch_{i+1:02d}",
            title=title,
            page_start=i + 1,
            page_end=i + 1,
            content=body,
            char_count=len(body)
        ))

    title = filename.replace(".md", "")
    size = os.path.getsize(file_path)

    return TextbookDetail(
        id=file_id,
        filename=filename,
        title=title,
        format="md",
        size_bytes=size,
        status=ParseStatus.DONE,
        total_pages=len(chapters),
        total_chars=len(content),
        chapters=chapters
    )


def _parse_txt(file_path: str, file_id: str, filename: str) -> TextbookDetail:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chapters = []
    pages = re.split(r'={2,}\s*第\d+页.*?={2,}', content)

    if len(pages) < 3:
        pages = [content]

    chapter_content = ""
    chapter_idx = 1
    page_start = 1

    for page_text in pages:
        page_text = page_text.strip()
        if not page_text:
            continue
        if "[纯图片页" in page_text:
            continue

        ch_match = re.match(r'^(第[一二三四五六七八九十\d]+章|Chapter\s+\d+)', page_text)
        if ch_match and chapter_content:
            chapters.append(Chapter(
                chapter_id=f"ch_{chapter_idx:02d}",
                title=f"第{chapter_idx}章",
                page_start=page_start,
                page_end=page_start,
                content=chapter_content.strip(),
                char_count=len(chapter_content.strip())
            ))
            chapter_idx += 1
            chapter_content = page_text
        else:
            chapter_content += "\n" + page_text

    if chapter_content.strip():
        chapters.append(Chapter(
            chapter_id=f"ch_{chapter_idx:02d}",
            title=f"第{chapter_idx}章",
            page_start=page_start,
            page_end=page_start + len(pages),
            content=chapter_content.strip(),
            char_count=len(chapter_content.strip())
        ))

    title = filename.replace(".txt", "")
    size = os.path.getsize(file_path)

    return TextbookDetail(
        id=file_id,
        filename=filename,
        title=title,
        format="txt",
        size_bytes=size,
        status=ParseStatus.DONE,
        total_pages=len(chapters),
        total_chars=len(content),
        chapters=chapters
    )
