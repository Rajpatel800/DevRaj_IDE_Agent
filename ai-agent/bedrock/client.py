"""
Simplified Bedrock Client for Claude Opus 4.7 (No Tool Calling)
With Streaming Support
"""
from openai import OpenAI
import os
from typing import List, Dict, Any, Iterator
from config import (
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    BEDROCK_MODEL_ID,
    MAX_TOKENS,
    TEMPERATURE
)
import boto3
import time


class BedrockClient:
    """Client for interacting with AWS Bedrock using Converse API (Claude Opus 4.7)"""
    
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.model_id = BEDROCK_MODEL_ID
    
    def call_ai(
        self,
        prompt: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE
    ) -> str:
        """
        Simple AI call - returns text response
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Text response from the model
        """
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature
                }
            )
            
            # Extract text from response
            output_text = response["output"]["message"]["content"][0]["text"]
            return output_text
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            raise
    
    def call_ai_stream(
        self,
        prompt: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE
    ) -> Iterator[str]:
        """
        Stream AI response (simulated streaming for Bedrock)
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they become available
        """
        try:
            # Get full response from Bedrock
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature
                }
            )
            
            # Extract text
            full_text = response["output"]["message"]["content"][0]["text"]
            
            # Simulate streaming by yielding word by word
            words = full_text.split()
            for i, word in enumerate(words):
                if i < len(words) - 1:
                    yield word + " "
                else:
                    yield word
                
                # Small delay to simulate streaming
                time.sleep(0.02)
            
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def call_with_system_prompt(
        self,
        user_message: str,
        system_prompt: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE
    ) -> str:
        """
        Call AI with system prompt
        
        Args:
            user_message: User's message
            system_prompt: System prompt for the agent
            max_tokens: Maximum tokens
            temperature: Temperature
            
        Returns:
            Text response
        """
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": user_message}]
                    }
                ],
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature
                }
            )
            
            output_text = response["output"]["message"]["content"][0]["text"]
            return output_text
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            raise
    
    def call_with_system_prompt_stream(
        self,
        user_message: str,
        system_prompt: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE
    ) -> Iterator[str]:
        """
        Stream AI response with system prompt
        
        Args:
            user_message: User's message
            system_prompt: System prompt
            max_tokens: Max tokens
            temperature: Temperature
            
        Yields:
            Text chunks
        """
        try:
            # Add strict format enforcement to system prompt
            enhanced_system_prompt = f"""{system_prompt}

CRITICAL: You ONLY output structured code files. No explanations. No markdown. No extra text.
START YOUR RESPONSE WITH: ### FILENAME:"""
            
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": user_message}]
                    }
                ],
                system=[{"text": enhanced_system_prompt}],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature
                }
            )
            
            full_text = response["output"]["message"]["content"][0]["text"]
            
            # Simulate streaming
            words = full_text.split()
            for i, word in enumerate(words):
                if i < len(words) - 1:
                    yield word + " "
                else:
                    yield word
                time.sleep(0.02)
            
        except Exception as e:
            yield f"Error: {str(e)}"


