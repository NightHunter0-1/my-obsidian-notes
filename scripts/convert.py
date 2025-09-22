import os
import re
import glob
from pathlib import Path

def convert_obsidian_links(content, current_file_path):
    """
    Преобразует Obsidian ссылки в GitHub-совместимые
    """
    # Регулярное выражение для [[ссылок]] и [[ссылок|текст]]
    pattern = r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]'
    
    def replace_match(match):
        original_link = match.group(1).strip()
        display_text = match.group(2) or original_link
        
        # Обрабатываем якоря [[файл#заголовок]]
        if '#' in original_link:
            file_part, anchor_part = original_link.split('#', 1)
            file_name = file_part.strip()
            anchor = anchor_part.strip()
        else:
            file_name = original_link.strip()
            anchor = None
        
        # Формируем правильный путь к файлу
        if file_name:
            # Заменяем пробелы и специальные символы
            file_name_clean = file_name.replace(' ', '%20')
            link_path = f"{file_name_clean}.md"
            
            # Если текущий файл не в корне, учитываем пути
            current_dir = os.path.dirname(current_file_path)
            if current_dir:
                # Создаем относительный путь
                relative_path = os.path.relpath('.', current_dir)
                link_path = os.path.join(relative_path, link_path)
        else:
            link_path = ""
        
        # Добавляем якорь если есть
        if anchor:
            anchor_clean = anchor.lower().replace(' ', '-')
            link_path += f"#{anchor_clean}"
        
        return f'[{display_text}]({link_path})'
    
    return re.sub(pattern, replace_match, content)

def process_all_files():
    """Обрабатывает все .md файлы в хранилище"""
    base_path = os.getcwd()
    md_files = glob.glob('**/*.md', recursive=True)
    
    converted_count = 0
    
    for file_path in md_files:
        # Пропускаем системные папки
        if any(skip in file_path for skip in ['.obsidian', '.git', 'scripts']):
            continue
            
        try:
            full_path = os.path.join(base_path, file_path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Преобразуем ссылки
            new_content = convert_obsidian_links(content, file_path)
            
            # Если контент изменился, сохраняем
            if new_content != content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Обработан: {file_path}")
                converted_count += 1
            else:
                print(f"➡️  Без изменений: {file_path}")
                
        except Exception as e:
            print(f"❌ Ошибка в {file_path}: {e}")
    
    return converted_count

def main():
    print("🔄 Начинаю преобразование Obsidian ссылок...")
    print("=" * 50)
    
    converted = process_all_files()
    
    print("=" * 50)
    print(f"🎉 Преобразование завершено!")
    print(f"📊 Обработано файлов: {converted}")
    print("\n💡 Теперь можете синхронизировать с GitHub через Obsidian Git")

if __name__ == "__main__":
    main()