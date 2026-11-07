@echo off
setlocal
cd /d "%~dp0"
if not exist .venv-tests\Scripts\python.exe (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m venv .venv-tests
  ) else (
    py -3 -m venv .venv-tests
  )
  if errorlevel 1 exit /b 1
)
.venv-tests\Scripts\python.exe -c "import selenium" >nul 2>nul
if errorlevel 1 (
  .venv-tests\Scripts\python.exe -m pip install -r tests\requirements.txt
  if errorlevel 1 exit /b 1
)
.venv-tests\Scripts\python.exe tests\test_mail.py %*
exit /b %errorlevel%
