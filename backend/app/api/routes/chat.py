"""Chat with Bob - Casual conversation endpoint"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from openai import AsyncOpenAI

from app.config import settings

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    conversation_id: Optional[str] = None
    mode: Optional[str] = "casual"
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]


@router.post("/chat", response_model=ChatResponse)
async def chat_with_Bob(request: ChatRequest):
    """
    Have a casual conversation with Bob, your AI assistant.
    Bob can help with coding questions, explain concepts, or just chat!
    """
    try:
        # Initialize OpenAI client
        if settings.watsonx_available:
            try:
                from app.services.ibm_watsonx_client import create_async_watsonx_client
                client = create_async_watsonx_client()
                model = settings.WATSONX_MODEL_ID
            except Exception:
                client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                model = "gpt-4o-mini"
        else:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            model = "gpt-4o-mini"
        
        # Use custom system prompt from frontend, or default casual Bob personality
        if request.system_prompt:
            system_prompt = request.system_prompt
        else:
            system_prompt = """You are Bob, a super friendly, warm, and highly conversational AI assistant. You speak like a real human—casual, empathetic, and engaging. 

CRITICAL INSTRUCTIONS FOR EVERY RESPONSE:
1. Your response MUST be extremely brief (maximum 2 short sentences).
2. You MUST ALWAYS end your response with an engaging question to keep the chat going.
3. NEVER write long explanations. If the user asks a complex question, give a simple 1-sentence summary and ask if they want to know more.
4. Do NOT start your response with greetings like 'Hey' or 'Hello'. Jump straight into the conversation.
5. NEVER include labels like "User:" or "Bob:" or simulate a conversation.
6. NO long paragraphs. Keep it punchy!"""

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 10 messages for context)
        for msg in request.conversation_history[-10:]:
            # Map frontend "Bob" role to standard OpenAI "assistant" role
            role = "assistant" if msg.role == "Bob" else msg.role
            messages.append({"role": role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Get response from AI
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4,  # slightly higher for more conversational tone
            max_tokens=100  # Enforce short responses
        )
        
        assistant_message = response.choices[0].message.content or "I'm here to help! What would you like to know?"
        
        # Clean up any role labels that might have slipped through
        assistant_message = _clean_response(assistant_message)
        
        # Generate contextual suggestions
        suggestions = _generate_suggestions(request.message, assistant_message)
        
        return ChatResponse(
            response=assistant_message,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


def _clean_response(response: str) -> str:
    """Aggressively clean response for voice - remove ALL formatting, lists, code, etc."""
    import re
    
    # CRITICAL: Detect and remove fake Q&A patterns
    # Pattern 1: "Answer. what is X? Answer to X."
    # Pattern 2: "Answer? what is X? Answer to X."
    
    # Find where fake Q&A starts (lowercase question words after punctuation)
    fake_qa_match = re.search(r'[.!?]\s+(what|how|why|when|where|who|can|should|is|are)\s+', response, re.IGNORECASE)
    if fake_qa_match:
        # Cut off everything from the fake question onwards
        response = response[:fake_qa_match.start() + 1]  # Keep the punctuation
    
    # Remove "System:", "Bob's response:", etc.
    response = re.sub(r'System\s*:\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r"Bob'?s?\s+response\s*:\s*", '', response, flags=re.IGNORECASE)
    response = re.sub(r'^\s*(User|Assistant|Bob|Q|A)\s*:\s*', '', response, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove quoted text that looks like fake conversations
    response = re.sub(r'"[^"]*"', '', response)
    
    # Remove ALL code blocks (```...```) and inline code (`...`)
    response = re.sub(r'```[\s\S]*?```', '', response)
    response = re.sub(r'`[^`]*`', '', response)
    
    # Remove ALL emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # extended symbols
        "]+",
        flags=re.UNICODE
    )
    response = emoji_pattern.sub('', response)
    
    # Remove numbered lists (1., 2., 3., etc.)
    response = re.sub(r'^\s*\d+\.\s+', '', response, flags=re.MULTILINE)
    
    # Remove bullet points (-, *, •, ◦, etc.)
    response = re.sub(r'^\s*[-*•◦▪▫]\s+', '', response, flags=re.MULTILINE)
    
    # Remove lines that look like code
    lines = response.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines with heavy indentation (code)
        if re.match(r'^\s{4,}', line):
            continue
        # Skip lines starting with code keywords
        if line.strip().startswith(('def ', 'class ', 'import ', 'from ', 'function ', 'const ', 'let ', 'var ')):
            continue
        # Skip lines that look like system messages or labels
        if re.match(r'^\s*(System|Bob|User|Assistant)\s*:', line, re.IGNORECASE):
            continue
        # Skip lines that start with questions (fake Q&A)
        if re.match(r'^\s*(what|how|why|when|where|who|can|should)\s+', line.strip(), re.IGNORECASE):
            continue
        # Skip empty lines
        if line.strip():
            cleaned_lines.append(line.strip())
    
    # Join with spaces for natural flow
    cleaned_response = ' '.join(cleaned_lines)
    
    # Remove multiple spaces
    cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
    
    # Remove any remaining special characters that sound bad
    cleaned_response = re.sub(r'[*_~`#]', '', cleaned_response)
    
    # If response is too short or empty after cleaning, return original
    if len(cleaned_response.strip()) < 3:
        return response.strip()
    
    return cleaned_response.strip()


def _generate_suggestions(user_message: str, assistant_response: str) -> List[str]:
    """Generate contextual follow-up suggestions"""
    
    # Default suggestions
    default_suggestions = [
        "Can you explain that in simpler terms?",
        "Show me a code example",
        "What are the best practices?",
        "Tell me more about this topic"
    ]
    
    # Context-aware suggestions based on keywords
    message_lower = user_message.lower()
    response_lower = assistant_response.lower()
    
    suggestions = []
    
    # Code-related
    if any(word in message_lower for word in ["code", "function", "class", "implement"]):
        suggestions.extend([
            "Can you show me an example?",
            "How would I test this?",
            "What are common pitfalls?"
        ])
    
    # Learning-related
    elif any(word in message_lower for word in ["learn", "understand", "explain", "what is"]):
        suggestions.extend([
            "Can you give me a real-world example?",
            "What should I learn next?",
            "Are there any resources you recommend?"
        ])
    
    # Problem-solving
    elif any(word in message_lower for word in ["error", "bug", "issue", "problem", "help"]):
        suggestions.extend([
            "How can I debug this?",
            "What's the best way to fix this?",
            "Can you explain why this happens?"
        ])
    
    # Architecture/Design
    elif any(word in message_lower for word in ["architecture", "design", "pattern", "structure"]):
        suggestions.extend([
            "What are the trade-offs?",
            "When should I use this pattern?",
            "Can you show me a diagram?"
        ])
    
    # If no specific context, use defaults
    if not suggestions:
        suggestions = default_suggestions[:3]
    
    # Return top 3 unique suggestions
    return list(dict.fromkeys(suggestions))[:3]


# Made with Bob