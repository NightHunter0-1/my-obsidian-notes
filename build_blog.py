import os
import re
import shutil
import markdown
from pathlib import Path
from slugify import slugify

# === НАСТРОЙКИ ===
VAULT_PATH = "01-Subjects"  # ← Путь к папке с лекциями
OUTPUT_DIR = "blog"
SITE_TITLE = "Мои лекции"

# HTML-шаблон страницы
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} — {site_title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
            color: #333;
            background: #fff;
        }}
        @media (prefers-color-scheme: dark) {{
            body {{
                background: #121212;
                color: #e0e0e0;
            }}
            h1, h2, h3 {{
                color: #bb86fc;
            }}
            a {{
                color: #4da6ff;
            }}
            code {{
                background: #333;
                color: #fff;
            }}
            pre {{
                background: #222;
                color: #fff;
            }}
            hr {{
                border-color: #444;
            }}
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: Consolas, monospace;
        }}
        pre {{
            background: #f8f8f8;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        hr {{
            margin: 40px 0;
            border: 0;
            border-top: 1px solid #eee;
        }}
        .breadcrumb {{
            font-size: 0.95em;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        .breadcrumb a {{
            color: #7f8c8d;
        }}
        @media (prefers-color-scheme: dark) {{
            .breadcrumb a {{
                color: #a0a0a0;
            }}
        }}
    </style>
</head>
<body>
    <div class="breadcrumb">{breadcrumb}</div>
    <h1>{page_title}</h1>
    {content}
    <hr>
    <a href="index.html" class="breadcrumb">← Все лекции</a>
</body>
</html>
"""

def remove_yaml_frontmatter(md_text):
    """Удаляет блок --- ... --- в начале файла"""
    if md_text.strip().startswith("---"):
        parts = md_text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return md_text

def convert_obsidian_links(text):
    """Преобразует [[note]] → <a href="note-slug.html">note</a>"""
    def replace_link(match):
        note_name = match.group(1)
        clean_name = note_name.split('#')[0]  # убираем якорь
        slug = slugify(clean_name)
        return f'<a href="{slug}.html">{note_name}</a>'
    return re.sub(r'\[\[(.*?)\]\]', replace_link, text)

def generate_breadcrumb(relative_path, vault_path):
    """Генерирует хлебные крошки: Главная → Папка → Подпапка"""
    parts = list(relative_path.parts[:-1])  # без имени файла
    crumbs = ['<a href="../index.html">Все лекции</a>']
    current_path = Path(".")

    for i, part in enumerate(parts):
        current_path = current_path / part
        target_index = "../" * (len(parts) - i - 1) + "index.html"
        crumbs.append(f'<a href="{target_index}">{part}</a>')

    return " → ".join(crumbs)

def build_folder_index(output_path, folder_path, vault_path):
    """Создаёт index.html для папки с подпапками и файлами"""
    items = []
    
    # Подпапки — отображаем как ссылки на их index.html
    for d in sorted(folder_path.iterdir()):
        if d.is_dir():
            items.append((d.name + "/", d.name + "/index.html"))

    # Файлы .md → конвертируем в HTML и добавляем в список
    for f in sorted(folder_path.iterdir()):
        if f.is_file() and f.suffix == ".md":
            title = f.stem.replace("-", " ").title()
            slug = slugify(title)
            items.append((title, slug + ".html"))

    content = "<h1>📂 " + (folder_path.name if folder_path != vault_path else SITE_TITLE) + "</h1>\n<ul>\n"
    for name, href in items:
        content += f'  <li><a href="{href}">{name}</a></li>\n'
    content += "</ul>"

    # Хлебные крошки
    rel_path = folder_path.relative_to(vault_path) if folder_path != vault_path else Path(".")
    breadcrumb_parts = ['<a href="../index.html">Все лекции</a>']
    for i, part in enumerate(rel_path.parts):
        path_up = "../" * (len(rel_path.parts) - i - 1)
        breadcrumb_parts.append(f'<a href="{path_up}index.html">{part}</a>')
    breadcrumb = " → ".join(breadcrumb_parts)

    full_html = HTML_TEMPLATE.format(
        page_title=folder_path.name if folder_path != vault_path else "Главная",
        site_title=SITE_TITLE,
        breadcrumb=breadcrumb,
        content=content
    )

    index_file = output_path / folder_path.relative_to(vault_path) / "index.html"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(full_html)

def main():
    vault_path = Path(VAULT_PATH)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    if not vault_path.exists():
        print(f"❌ Папка не найдена: {vault_path}")
        return

    # Копируем изображения
    print("🖼️ Копирую изображения...")
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
    for img_file in vault_path.rglob("*"):
        if img_file.suffix.lower() in image_extensions:
            rel_path = img_file.relative_to(vault_path)
            dest = output_path / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img_file, dest)

    # Собираем все .md файлы рекурсивно
    md_files = list(vault_path.rglob("*.md"))
    if not md_files:
        print("⚠️ Нет .md файлов для обработки!")
        return

    print(f"📄 Найдено {len(md_files)} лекций. Обрабатываю...")

    all_pages = []  # для главной страницы

    for md_file in md_files:
        print(f"  → {md_file.relative_to(vault_path)}")

        with open(md_file, "r", encoding="utf-8") as f:
            md_text = f.read()

        # Удаляем YAML
        md_text = remove_yaml_frontmatter(md_text)

        # Извлекаем заголовок
        lines = md_text.strip().split("\n")
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
            body_md = "\n".join(lines[1:]).strip()
        else:
            title = md_file.stem
            body_md = md_text

        # Обрабатываем ссылки и конвертируем в HTML
        body_md = convert_obsidian_links(body_md)
        html_body = markdown.markdown(
            body_md,
            extensions=["fenced_code", "tables", "nl2br"]
        )

        # Генерируем слаг и путь
        slug = slugify(title)
        rel_dir = md_file.parent.relative_to(vault_path)
        html_file = output_path / rel_dir / f"{slug}.html"
        html_file.parent.mkdir(parents=True, exist_ok=True)

        # Хлебные крошки
        breadcrumb = generate_breadcrumb(md_file.relative_to(vault_path), vault_path)

        # Сохраняем HTML
        full_html = HTML_TEMPLATE.format(
            page_title=title,
            site_title=SITE_TITLE,
            breadcrumb=breadcrumb,
            content=html_body
        )
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(full_html)

        all_pages.append((title, rel_dir / f"{slug}.html"))

    # Генерируем index.html для каждой папки
    print("🗂️ Создаю индексы папок...")
    folders = {vault_path}
    for md_file in md_files:
        folders.add(md_file.parent)

    for folder in sorted(folders):
        build_folder_index(output_path, folder, vault_path)

    print(f"\n✅ Готово! Сайт сохранён в: {output_path.absolute()}")
    print(f"Открой: {output_path.absolute() / 'index.html'}")

if __name__ == "__main__":
    main()
