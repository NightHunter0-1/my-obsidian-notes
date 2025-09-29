#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path
import shutil

class RussianPDFConverter:
    def __init__(self):
        self.config = self.load_config()
        self.pdf_dir = self.config['pdf_output_dir']
        
    def load_config(self):
        try:
            with open('.github/pdf-config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Ошибка загрузки конфига: {e}")
            return {
                'pdf_output_dir': '_pdf_export',
                'exclude_patterns': ['.git/', '.github/', '_pdf_export/']
            }
    
    def should_convert(self, file_path):
        """Проверяем, нужно ли конвертировать файл"""
        exclude_patterns = self.config.get('exclude_patterns', [])
        
        for pattern in exclude_patterns:
            if pattern in file_path:
                return False
        
        return file_path.endswith('.md') and not file_path.startswith('./_pdf_export')
    
    def create_mirror_structure(self, md_file):
        """Создает зеркальную структуру папок для PDF"""
        relative_path = str(Path(md_file).relative_to('.'))
        pdf_path = os.path.join(self.pdf_dir, relative_path).replace('.md', '.pdf')
        
        # Создаем директорию если нужно
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        return pdf_path
    
    def convert_md_to_pdf(self, md_file):
        """Конвертирует MD в PDF с поддержкой русского"""
        pdf_file = self.create_mirror_structure(md_file)
        
        print(f"🔄 Конвертируем: {md_file}")
        print(f"📄 В PDF: {pdf_file}")
        
        pandoc_args = [
            'pandoc',
            md_file,
            '-o', pdf_file,
            '--pdf-engine=xelatex',
            '-V', 'mainfont=DejaVu Serif',
            '-V', 'sansfont=DejaVu Sans',
            '-V', 'monofont=DejaVu Sans Mono', 
            '-V', 'geometry:margin=2.5cm',
            '-V', 'lang=russian',
            '--toc',
            '--toc-depth=3',
            '-N',
            '--wrap=auto'
        ]
        
        try:
            # Первая попытка
            result = subprocess.run(pandoc_args, capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                print(f"✅ Успешно: {pdf_file}")
                return True
            else:
                print(f"⚠️  Ошибка: {result.stderr}")
                return self.fallback_convert(md_file, pdf_file)
                
        except Exception as e:
            print(f"❌ Исключение: {e}")
            return self.fallback_convert(md_file, pdf_file)
    
    def fallback_convert(self, md_file, pdf_file):
        """Альтернативный метод конвертации"""
        print(f"🔄 Пробуем альтернативный метод для: {md_file}")
        
        try:
            # Простой метод без сложных настроек
            simple_args = [
                'pandoc',
                md_file,
                '-o', pdf_file,
                '--pdf-engine=xelatex',
                '-V', 'mainfont=Liberation Serif',
                '-V', 'geometry:margin=2cm'
            ]
            
            result = subprocess.run(simple_args, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Альтернативный метод тоже не сработал: {e}")
            return False
    
    def run_conversion(self):
        """Основной метод запуска конвертации"""
        print("🚀 Начинаем конвертацию Markdown в PDF...")
        
        # Создаем основную папку для PDF
        os.makedirs(self.pdf_dir, exist_ok=True)
        
        converted_count = 0
        failed_count = 0
        
        for root, dirs, files in os.walk('.'):
            # Пропускаем скрытые и служебные директории
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '_pdf_export']
            
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    
                    if self.should_convert(file_path):
                        if self.convert_md_to_pdf(file_path):
                            converted_count += 1
                        else:
                            failed_count += 1
        
        print(f"\n📊 Итоги конвертации:")
        print(f"✅ Успешно: {converted_count}")
        print(f"❌ Ошибки: {failed_count}")
        
        return converted_count > 0

if __name__ == '__main__':
    converter = RussianPDFConverter()
    success = converter.run_conversion()
    exit(0 if success else 1)
