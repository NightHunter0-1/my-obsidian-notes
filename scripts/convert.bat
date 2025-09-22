@echo off
chcp 65001 > nul
title Конвертер Obsidian ссылок

echo 🔗 Конвертер Obsidian -> GitHub ссылок
echo ==========================================

:: Проверяем Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден! Установите Python с python.org
    pause
    exit /b 1
)

echo 🐍 Python найден
echo 🔄 Запускаю преобразование ссылок...

python convert.py

echo.
echo ✅ Преобразование завершено!
echo.
echo 📝 Дальнейшие действия:
echo    1. Вернитесь в Obsidian
echo    2. Дождитесь авто-синхронизации
echo    3. Проверьте статус в правом нижнем углу
echo.

timeout /t 10 /nobreak > nul