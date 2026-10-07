@echo off
cd /d "%~dp0"

start "" llama-server.exe -m ".\models\GLM-OCR-f16.gguf" --mmproj ".\models\GLM-OCR.mmproj-f16.gguf" --host 127.0.0.1 --port 8080 --flash-attn off -fit off

timeout /t 3 /nobreak >nul

start "" "http://127.0.0.1:8080"