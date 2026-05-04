"""
Test different model IDs to find which one works
"""
import boto3
import os

client = boto3.client(
    'bedrock-runtime',
    region_name='eu-north-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Try different model IDs
model_ids = [
    "eu.anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "eu.anthropic.claude-3-5-sonnet-20241022-v2:0",
]

print("Testing model IDs...\n")

for model_id in model_ids:
    try:
        print(f"Testing: {model_id}")
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Say hi"}]
                }
            ],
            inferenceConfig={
                "maxTokens": 100,
                "temperature": 0.7
            }
        )
        output = response["output"]["message"]["content"][0]["text"]
        print(f"✅ SUCCESS! Model works: {model_id}")
        print(f"   Response: {output}\n")
        break
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}\n")
