import os
import re
from collections.abc import Generator
from typing import Final

MAX_FILE_SIZE: Final[int] = 5 * 1024 * 1024
FILE_TAG_PATTERN: Final[str] = r'@::(.*?)::'


def process_file_tags(text: str) -> str:

    paths = re.findall(FILE_TAG_PATTERN, text)

    for path in paths:
        clean_path = path.strip()

        if not os.path.exists(clean_path):
            print(f'Файл {clean_path} не найден.')
            continue

        if not os.path.isfile(clean_path):
            print(f'{clean_path} не является файлом.')
            continue

        if os.path.getsize(clean_path) > MAX_FILE_SIZE:
            print(f'Файл {clean_path} слишком большой. Максимум 5 MB.')
            continue

        with open(clean_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        text = text.replace(
            f'@::{path}::',
            f'\n\n--- Содержимое файла {clean_path} ---\n{content}\n--- Конец файла ---\n\n',
        )

    return text


def chunk_by_len(content: str, value: int) -> Generator[str]:
    for start in range(0, len(content), value):
        yield content[start : start + value]


def chunk_by_paragraph(content: str, value: int) -> Generator[str]:
    paragraphs = content.split('\n\n')

    for start in range(0, len(paragraphs), value):
        chunk = '\n\n'.join(paragraphs[start : start + value]).strip()

        if chunk:
            yield chunk


def chunk_by_line(content: str) -> Generator[str]:
    for line in content.splitlines():
        clean_line = line.strip()

        if clean_line:
            yield clean_line


def get_chunks(path: str, mode: str, value: int) -> Generator[str]:

    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()

    if mode == 'len':
        yield from chunk_by_len(content, value)
    elif mode == 'paragraph':
        yield from chunk_by_paragraph(content, value)
    else:
        yield from chunk_by_line(content)
