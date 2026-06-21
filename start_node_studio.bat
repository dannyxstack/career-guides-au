@echo off
chcp 65001 >nul
title Career Video Pipeline - Remotion Studio

REM Activate conda env career-video (Node still uses system PATH)
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" career-video
if errorlevel 1 (
    echo [ERROR] Failed to activate conda env career-video
    pause
    exit /b 1
)

cd /d E:\work\career-guides-au\video_pipeline\remotion

echo ============================================
echo  Starting Remotion Studio (template preview)
echo  Open browser: http://localhost:3000
echo  Press Ctrl+C to stop
echo ============================================
call npm run studio

pause
