@echo off
echo Building System Monitor...
echo.

REM Check if virtual environment is activated
python -c "import sys; print('Virtual env:', hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"

echo Installing build dependencies...
nuitka --standalone --windows-console-mode=disable --windows-icon-from-ico=assets/icon.ico --include-data-dir=assets=assets --output-filename=SystemMonitor.exe --output-dir=C:/temp/build --show-progress --show-memory --remove-output --assume-yes-for-downloads --plugin-enable=tk-inter --include-package=psutil --include-package=gspread --include-package=google --include-package=pystray --include-package=PIL --include-package=superyngo_logger --include-package=schedule --include-package=requests main.py

echo.
echo Starting build process...
python build.py

echo.
echo Build process completed.
pause
