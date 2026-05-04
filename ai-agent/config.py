"""
Configuration for the AI Agent System
"""
import os

# AWS Bedrock Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Model Configuration - Claude Opus 4.7 via Bedrock
BEDROCK_MODEL_ID = "arn:aws:bedrock:us-east-1:934812479449:inference-profile/us.anthropic.claude-opus-4.7"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Agent Configuration
DEFAULT_AGENT = "developer"
AVAILABLE_AGENTS = ["planner", "developer", "debugger", "tester"]

# Tool Configuration
MAX_RETRIES = 3
COMMAND_TIMEOUT = 30  # seconds
