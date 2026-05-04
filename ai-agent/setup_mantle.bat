@echo off
echo ============================================================
echo Setting up Bedrock Mantle API credentials
echo ============================================================
echo.

echo Setting OPENAI_API_KEY...
setx OPENAI_API_KEY "<YOUR_OPENAI_API_KEY>"

echo Setting OPENAI_BASE_URL...
setx OPENAI_BASE_URL "https://bedrock-mantle.eu-north-1.api.aws/v1"

echo.
echo ============================================================
echo ✅ Credentials configured!
echo ============================================================
echo.
echo ⚠️  IMPORTANT: Close this terminal and open a new one!
echo.
echo Next steps:
echo   1. Close this terminal
echo   2. Open a new terminal
echo   3. cd ai-agent
echo   4. pip install -r requirements.txt
echo   5. python main.py
echo.
pause
