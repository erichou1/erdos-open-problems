@echo off
setlocal
set "APPDIR=%~dp0"
set "POINTER=%APPDIR%repo-path.txt"
if exist "%POINTER%" (
  set /p "REPO_ROOT="<"%POINTER%"
) else (
  set "REPO_ROOT=%~dp0"
)
set "PYTHON=%REPO_ROOT%\.venv\Scripts\pythonw.exe"
if not exist "%PYTHON%" set "PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"
set "CONSOLE=%REPO_ROOT%\operator_console.py"
if not exist "%PYTHON%" (
  echo EGMRA virtual environment is missing. Follow AGENT_SETUP.md Phase 1 first.
  pause
  exit /b 1
)
if not exist "%CONSOLE%" (
  echo Cannot find operator_console.py at %REPO_ROOT%
  pause
  exit /b 1
)
start "EGMRA Operator" "%PYTHON%" -u "%CONSOLE%"
endlocal
