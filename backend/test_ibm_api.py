"""Test script for IBM watsonx.ai connection"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ibm_watsonx_client import create_watsonx_client
from app.config import settings


def test_ibm_connection():
    """Test IBM watsonx.ai connection"""
    print("=" * 60)
    print("Testing IBM watsonx.ai Connection")
    print("=" * 60)
    
    # Check configuration
    print(f"\n[OK] IBM Cloud API Key: {settings.IBM_CLOUD_API_KEY[:10] if settings.IBM_CLOUD_API_KEY else 'NOT SET'}...")
    print(f"[OK] Project ID: {settings.WATSONX_PROJECT_ID[:8] if settings.WATSONX_PROJECT_ID else 'NOT SET'}...")
    print(f"[OK] watsonx URL: {settings.WATSONX_URL}")
    print(f"[OK] Model: {settings.WATSONX_MODEL_ID}")
    
    # Check if credentials are configured
    if not settings.watsonx_available:
        print("\n[ERROR] IBM watsonx.ai credentials not configured!")
        print("\nPlease set the following in backend/.env:")
        print("  - IBM_CLOUD_API_KEY")
        print("  - WATSONX_PROJECT_ID")
        print("\nSee IBM_CREDENTIALS_GUIDE.md for details.")
        return False
    
    try:
        # Create client
        client = create_watsonx_client()
        print("\n[OK] IBM watsonx client created successfully")
        
        # Get access token
        print("\n[...] Getting IAM access token...")
        token = client._get_access_token()
        print(f"[OK] Access token obtained: {token[:20]}...")
        
        # Test text generation
        print("\n[...] Sending test request to Granite model...")
        response = client.generate_text(
            prompt="Say 'Hello from DevPilot AI!' in one sentence.",
            max_tokens=50
        )
        
        print("\n[SUCCESS] IBM watsonx.ai is working!")
        print(f"\n[Response] {response}")
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("\nTroubleshooting:")
        print("1. Verify IBM Cloud API key is correct")
        print("2. Verify watsonx.ai Project ID is correct")
        print("3. Ensure Watson Machine Learning service is associated with project")
        print("4. Check that you're using the correct region")
        print("\nSee IBM_CREDENTIALS_GUIDE.md for detailed setup instructions.")
        return False


async def test_async_client():
    """Test async IBM watsonx client"""
    print("\n" + "=" * 60)
    print("Testing Async IBM watsonx.ai Client")
    print("=" * 60)
    
    try:
        from app.services.ibm_watsonx_client import create_async_watsonx_client
        
        client = create_async_watsonx_client()
        print("\n[OK] Async client created")
        
        print("\n[...] Testing chat completion interface...")
        response = await client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            max_tokens=50
        )
        
        print("[SUCCESS] Async client working!")
        print(f"[Response] {response.choices[0].message.content}")
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        return False


def main():
    """Run all tests"""
    print("\n🚀 IBM watsonx.ai Connection Test\n")
    
    # Test sync client
    sync_result = test_ibm_connection()
    
    if sync_result:
        # Test async client
        async_result = asyncio.run(test_async_client())
        
        if async_result:
            print("\n✅ All tests passed!")
            print("\nYou're ready to use DevPilot AI with IBM watsonx.ai!")
            print("\nNext steps:")
            print("1. Start backend: uvicorn app.main:app --reload --port 8000")
            print("2. Start frontend: npm run dev")
            print("3. Open http://localhost:3000")
            return 0
        else:
            print("\n❌ Async client test failed")
            return 1
    else:
        print("\n❌ Sync client test failed")
        print("\nPlease fix the errors above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
