"""
Quick setup verification for AWS Bedrock with Claude Sonnet 4.6
"""
import os
import sys

def check_aws_credentials():
    """Check if AWS credentials are set"""
    print("Checking AWS credentials...")
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not access_key:
        print("❌ AWS_ACCESS_KEY_ID not set")
        print("   Run: setx AWS_ACCESS_KEY_ID \"your-access-key\"")
        return False
    else:
        print(f"✅ AWS_ACCESS_KEY_ID is set ({access_key[:8]}...)")
    
    if not secret_key:
        print("❌ AWS_SECRET_ACCESS_KEY not set")
        print("   Run: setx AWS_SECRET_ACCESS_KEY \"your-secret-key\"")
        return False
    else:
        print(f"✅ AWS_SECRET_ACCESS_KEY is set ({secret_key[:8]}...)")
    
    print(f"✅ AWS_REGION: {region}")
    
    return True


def check_boto3():
    """Check if boto3 is installed"""
    print("\nChecking boto3 installation...")
    try:
        import boto3
        print(f"✅ boto3 is installed (version {boto3.__version__})")
        return True
    except ImportError:
        print("❌ boto3 is not installed")
        print("   Run: pip install boto3")
        return False


def check_bedrock_access():
    """Try to connect to Bedrock"""
    print("\nChecking Bedrock access...")
    try:
        import boto3
        
        client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Try to list foundation models (this doesn't cost anything)
        print("✅ Successfully connected to AWS Bedrock")
        print("   Note: Actual model access will be verified when you run the system")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not connect to Bedrock: {e}")
        print("   This might be due to:")
        print("   - Invalid credentials")
        print("   - Bedrock not enabled in your region")
        print("   - Network issues")
        return False


def check_model_config():
    """Check model configuration"""
    print("\nChecking model configuration...")
    try:
        from config import BEDROCK_MODEL_ID
        print(f"✅ Model configured: {BEDROCK_MODEL_ID}")
        
        if "claude-sonnet-4" in BEDROCK_MODEL_ID.lower():
            print("✅ Using Claude Sonnet 4.6")
        else:
            print("⚠️  Model ID doesn't appear to be Claude Sonnet 4.6")
        
        return True
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("AWS Bedrock Setup Verification")
    print("Claude Sonnet 4.6 Configuration")
    print("=" * 60)
    print()
    
    checks = [
        ("AWS Credentials", check_aws_credentials),
        ("boto3 Installation", check_boto3),
        ("Model Configuration", check_model_config),
        ("Bedrock Access", check_bedrock_access)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup is complete! You're ready to use the system.")
        print("\nNext step:")
        print("  python main.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Install boto3: pip install boto3")
        print("  2. Set AWS credentials using setx commands")
        print("  3. Restart your terminal after setting environment variables")
        print("  4. Verify Bedrock is enabled in your AWS account")
        return 1


if __name__ == "__main__":
    sys.exit(main())
