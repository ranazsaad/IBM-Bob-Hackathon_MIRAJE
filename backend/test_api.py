"""Quick test script to verify Bob API connection"""
import asyncio
import sys
import os
from openai import AsyncOpenAI

async def test_bob_api():
    """Test Bob API connection"""
    print("=" * 60)
    print("Testing Bob API Connection")
    print("=" * 60)
    
    # Load from .env file directly
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.cline.bot/v1")
    model = os.getenv("OPENAI_MODEL", "claude-3-5-sonnet-20241022")
    
    print(f"\n[OK] API Key: {api_key[:20] if api_key else 'NOT SET'}...")
    print(f"[OK] API Base: {api_base}")
    print(f"[OK] Model: {model}")
    
    if not api_key or api_key == "PUT_YOUR_BOB_API_KEY_HERE":
        print("\n[ERROR] API key not set in .env file!")
        print("Please update OPENAI_API_KEY in backend/.env")
        return False
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
        print("\n[OK] OpenAI client created successfully")
        
        print("\n[...] Sending test request to Bob API...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'Hello from DevPilot AI!' in one sentence."}
            ],
            max_tokens=50
        )
        
        print("\n[SUCCESS] Bob API is working!")
        print(f"\n[Response] {response.choices[0].message.content}")
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        return False

if __name__ == "__main__":
    asyncio.run(test_bob_api())

# Made with Bob
