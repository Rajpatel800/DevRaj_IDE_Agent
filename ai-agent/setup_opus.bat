@echo off
echo ============================================================
echo Configuring AWS for Claude Opus 4.7
echo ============================================================
echo.

echo Setting AWS_REGION to us-east-1...
setx AWS_REGION "us-east-1"

echo.
echo ============================================================
echo ✅ Region configured for Claude Opus 4.7!
echo ============================================================
echo.
echo ⚠️  IMPORTANT: Close this terminal and open a new one!
echo.
echo Next steps:
echo   1. Close this terminal
echo   2. Open a new terminal
echo   3. cd ai-agent
echo   4. python main.py
echo.
echo Model: Claude Opus 4.7 (us.anthropic.claude-opus-4.7)
echo Region: us-east-1
echo.
pause
