"""
文档解析与分块
"""

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config


splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.RAG_CHUNK_SIZE,
    chunk_overlap=config.RAG_CHUNK_OVERLAP,
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "],
)


def parse_file(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = splitter.split_text(content)
    basename = os.path.basename(file_path)
    return [
        {
            "content": chunk,
            "metadata": {
                "source": basename,
                "chunk_index": i,
                "total_chunks": len(chunks),
            },
        }
        for i, chunk in enumerate(chunks)
    ]


def parse_text(text: str, source: str = "user_input") -> list[dict]:
    chunks = splitter.split_text(text)
    return [
        {
            "content": chunk,
            "metadata": {
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks),
            },
        }
        for i, chunk in enumerate(chunks)
    ]
