
:VULKAN
echo.
echo Comprobando dispositivos disponibles...
.\llama-server.exe --list-devices
echo.
pause

echo Iniciando GLM-OCR con CPU + Vulkan...
start "" cmd /c "timeout /t 10 /nobreak >nul & start "" http://127.0.0.1:8080/"

.\llama-server.exe ^
  -m ".\models\GLM-OCR.f16.gguf" ^
  --mmproj ".\models\GLM-OCR.mmproj-f16.gguf" ^
  --host 127.0.0.1 ^
  --port 8080 ^
  --ctx-size 8192 ^
  --parallel 1 ^
  --threads 6 ^
  --n-gpu-layers all ^
  --temp 0.1 ^
  --flash-attn off ^
  -fit off

goto FIN
