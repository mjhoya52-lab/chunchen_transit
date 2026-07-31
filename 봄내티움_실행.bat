@echo off
chcp 65001 > nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [오류] 가상환경을 찾을 수 없습니다.
  echo 먼저 python -m venv .venv 명령을 실행해주세요.
  pause
  exit /b 1
)

echo 봄내티움 최신 Python 서버를 실행합니다.
echo 브라우저 주소: http://127.0.0.1:8080
echo.
".venv\Scripts\python.exe" app.py
pause
