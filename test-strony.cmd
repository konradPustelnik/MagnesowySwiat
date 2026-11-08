@echo off
setlocal
cd /d "%~dp0"
set "TEST_INTERACTIVE="
set "TEST_EXIT_CODE=1"
set "TEST_BROWSER=--browser"
if "%~1"=="" set "TEST_INTERACTIVE=1"
if not "%~2"=="" goto usage_error
if "%~1"=="" goto prepare
if /i "%~1"=="--browser" goto prepare
if /i "%~1"=="--static" (
  set "TEST_BROWSER="
  goto prepare
)
if /i "%~1"=="--help" goto help
goto usage_error

:prepare
if exist ".venv-tests\Scripts\python.exe" goto dependencies
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3 -m venv .venv-tests
if errorlevel 1 goto finish
goto dependencies

:python_fallback
where python >nul 2>nul
if errorlevel 1 (
  echo Nie znaleziono Pythona. Zainstaluj Python 3 i uruchom ponownie.
  goto finish
)
python -m venv .venv-tests
if errorlevel 1 goto finish

:dependencies
if not defined TEST_BROWSER goto run
.venv-tests\Scripts\python.exe -c "import selenium" >nul 2>nul
if not errorlevel 1 goto run
echo Instalowanie zaleznosci testow przegladarkowych...
.venv-tests\Scripts\python.exe -m pip install -r tests\requirements.txt
if errorlevel 1 goto finish

:run
echo Testy lokalne. Wiadomosci i zdjecia nie sa wysylane do FormSubmit.
.venv-tests\Scripts\python.exe tests\test_site.py %TEST_BROWSER% -v
set "TEST_EXIT_CODE=%errorlevel%"
if "%TEST_EXIT_CODE%"=="0" (
  echo.
  echo Testy zakonczone powodzeniem. To nie jest potwierdzenie doreczenia e-maila.
) else (
  echo.
  echo Testy wykryly blad. Szczegoly znajduja sie powyzej.
)
goto finish

:usage_error
echo Nieznany argument lub zbyt wiele argumentow.
set "TEST_EXIT_CODE=2"
goto usage

:help
set "TEST_EXIT_CODE=0"

:usage
echo Uzycie:
echo   test-strony.cmd             pelny test w Chrome
echo   test-strony.cmd --browser   pelny test w Chrome
echo   test-strony.cmd --static    szybkie kontrole plikow, bez Chrome

:finish
if defined TEST_INTERACTIVE pause
exit /b %TEST_EXIT_CODE%
