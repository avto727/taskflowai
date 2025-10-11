#!/usr/bin/env python3
"""Очистка markdown от HTML и ссылок"""
import re

input_file = "Правило семи мешков с золотом.md"
output_file = "Правило семи мешков с золотом.md"

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Убрать первую строку с [[...]]
content = re.sub(r'^\[\[.*?\]\]\n\n', '', content)

# Убрать HTML теги
content = re.sub(r'<img[^>]*>', '', content)
content = re.sub(r'<span[^>]*>.*?</span>', '', content, flags=re.DOTALL)
content = re.sub(r'<div[^>]*>.*?</div>', '', content, flags=re.DOTALL)

# Убрать ссылки [^X_Y]
content = re.sub(r'\[\^[0-9]+_[0-9]+\]', '', content)

# Убрать блоки ссылок
content = re.sub(r'\n\[\^[0-9]+_[0-9]+\]:.*', '', content)

# Убрать множественные пустые строки
content = re.sub(r'\n{3,}', '\n\n', content)

# Убрать пробелы в конце строк
content = re.sub(r' +\n', '\n', content)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content.strip() + '\n')

print(f'✅ Файл очищен: {output_file}')
