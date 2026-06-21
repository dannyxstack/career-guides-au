@echo off
chcp 65001 >nul
title Career Video Pipeline - Python Web

REM Activate conda env career-video
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" career-video
if errorlevel 1 (
    echo [ERROR] Failed to activate conda env career-video
    pause
    exit /b 1
)

cd /d E:\work\career-guides-au
set PYTHONUTF8=1

echo ============================================
echo  Starting Python Web UI
echo  Open browser: http://127.0.0.1:8000
echo  Press Ctrl+C to stop
echo ============================================
python -m video_pipeline.web.app

pause
