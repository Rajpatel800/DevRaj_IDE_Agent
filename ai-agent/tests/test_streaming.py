"""
Test script for streaming functionality
"""
import requests
import sys

def test_streaming():
    """Test the streaming endpoint"""
    url = "http://localhost:8000/chat-stream"
    
    payload = {
        "prompt": "Write a simple hello world program in Python",
        "agent": "developer"
    }
    
    print("🧪 Testing streaming endpoint...")
    print(f"📡 URL: {url}")
    print(f"📝 Prompt: {payload['prompt']}")
    print(f"🤖 Agent: {payload['agent']}")
    print("\n" + "="*60)
    print("📥 Streaming response:\n")
    
    try:
        response = requests.post(
            url,
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return False
        
        # Stream the response
        word_count = 0
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                print(chunk, end='', flush=True)
                word_count += len(chunk.split())
        
        print("\n" + "="*60)
        print(f"✅ Streaming test completed!")
        print(f"📊 Total words received: ~{word_count}")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend")
        print("💡 Make sure the backend is running:")
        print("   cd ai-agent && python api_server.py")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_non_streaming():
    """Test the non-streaming endpoint for comparison"""
    url = "http://localhost:8000/chat"
    
    payload = {
        "message": "Write a simple hello world program in Python",
        "agent": "developer"
    }
    
    print("\n\n🧪 Testing non-streaming endpoint (for comparison)...")
    print(f"📡 URL: {url}")
    print("\n" + "="*60)
    print("⏳ Waiting for complete response...\n")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
        
        result = response.json()
        print(result['response'])
        print("\n" + "="*60)
        print("✅ Non-streaming test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 AI Agent Streaming Test Suite\n")
    
    # Test streaming
    streaming_ok = test_streaming()
    
    # Test non-streaming
    non_streaming_ok = test_non_streaming()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Streaming endpoint:     {'✅ PASS' if streaming_ok else '❌ FAIL'}")
    print(f"Non-streaming endpoint: {'✅ PASS' if non_streaming_ok else '❌ FAIL'}")
    print("="*60)
    
    if streaming_ok and non_streaming_ok:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed")
        sys.exit(1)
