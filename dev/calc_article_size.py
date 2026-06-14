"""
读取 nowbase.json 中每篇文章的 filePath，提取文件名后到 articles/ 下搜索对应 PDF，
获取文件大小和全文字数（字符数），并将 size 字段写入 nowbase.json。

size 字段格式：[文件大小(字节), 全文字数(字符)]
"""

import json
import os
import urllib.parse
import fitz  # PyMuPDF

# 路径配置
NOWBASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "database", "data", "nowbase.json")
ARTICLES_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "articles")


def extract_filename_from_url(url: str) -> str:
    """从 filePath URL 中提取文件名（最后一个斜杠后的部分）并 URL 解码"""
    raw_name = url.rstrip("/").rsplit("/", 1)[-1]
    return urllib.parse.unquote(raw_name)


def search_pdf(articles_root: str, filename: str):
    """在 articles 目录下递归搜索指定文件名的 PDF，返回完整路径或 None"""
    for dirpath, _, filenames in os.walk(articles_root):
        for fname in filenames:
            if fname == filename:
                return os.path.join(dirpath, fname)
    return None


def get_pdf_word_count(pdf_path: str) -> int:
    """打开 PDF 并提取所有文字，返回总字符数"""
    doc = fitz.open(pdf_path)
    total_chars = 0
    for page in doc:
        text = page.get_text()
        total_chars += len(text)
    doc.close()
    return total_chars


def main():
    # 读取 nowbase.json
    with open(NOWBASE_PATH, "r", encoding="utf-8") as f:
        articles = json.load(f)

    updated_count = 0
    skipped_count = 0
    not_found = []

    for article in articles:
        filepath_url = article.get("filePath", "")
        if not filepath_url:
            print(f"  [跳过] id={article.get('id')}: 无 filePath")
            skipped_count += 1
            continue

        # 提取文件名
        filename = extract_filename_from_url(filepath_url)
        if not filename:
            print(f"  [跳过] id={article.get('id')}: 无法从 URL 提取文件名")
            skipped_count += 1
            continue

        # 搜索 PDF
        pdf_path = search_pdf(ARTICLES_ROOT, filename)
        if pdf_path is None:
            print(f"  [未找到] id={article.get('id')}: {filename}")
            not_found.append((article.get("id"), filename))
            skipped_count += 1
            continue

        # 获取文件大小
        file_size = os.path.getsize(pdf_path)

        # 提取文字获得全文字数
        word_count = get_pdf_word_count(pdf_path)

        # 写入 size 字段
        article["size"] = [file_size, word_count]

        # 显示文件大小（智能单位）
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"

        print(f"  [OK] id={article.get('id')}: {filename}")
        print(f"        大小: {size_str}  |  字数: {word_count}")

        updated_count += 1

    # 写回 nowbase.json
    with open(NOWBASE_PATH, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"处理完成！")
    print(f"  更新: {updated_count} 篇")
    print(f"  跳过: {skipped_count} 篇")
    if not_found:
        print(f"  未找到 PDF 的文章:")
        for aid, fn in not_found:
            print(f"    id={aid}: {fn}")


if __name__ == "__main__":
    main()
