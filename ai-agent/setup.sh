#!/bin/bash

# Setup script for Multi-Agent AI Coding System

echo "=================================================="
echo "Multi-Agent AI Coding System - Setup"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for .env file
echo ""
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  .env file not found"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your AWS credentials"
fi

# Run system tests
echo ""
echo "Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ Setup Complete!"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "1. Edit .env with your AWS credentials (if not done)"
    echo "2. Run: python main.py"
    echo "3. Start chatting with the AI agents!"
    echo ""
    echo "Documentation:"
    echo "  - README.md - Full documentation"
    echo "  - QUICKSTART.md - Quick start guide"
    echo "  - ARCHITECTURE.md - Technical details"
    echo ""
else
    echo ""
    echo "⚠️  Some tests failed. Please check the output above."
    echo "You may need to set AWS credentials."
fi
