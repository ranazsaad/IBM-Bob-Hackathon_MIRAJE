"""IBM watsonx.ai client for Granite models"""

import requests
import json
from typing import List, Dict, Any, Optional
from app.config import settings


class IBMWatsonxClient:
    """Client for IBM watsonx.ai API using Granite models"""
    
    def __init__(self):
        self.api_key = settings.IBM_CLOUD_API_KEY
        self.project_id = settings.WATSONX_PROJECT_ID
        self.url = settings.WATSONX_URL
        self.model_id = settings.WATSONX_MODEL_ID
        self._access_token: Optional[str] = None
    
    def _get_access_token(self) -> str:
        """Get IBM Cloud IAM access token"""
        if self._access_token is not None:
            return self._access_token
        
        token_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        self._access_token = response.json()["access_token"]
        return self._access_token
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
    ) -> str:
        """Generate text using Granite model"""
        
        access_token = self._get_access_token()
        
        # Construct API endpoint
        endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Build parameters
        parameters = {
            "max_new_tokens": max_tokens or settings.MAX_TOKENS,
            "temperature": temperature or settings.TEMPERATURE,
            "top_p": top_p or settings.TOP_P,
            "top_k": top_k or settings.TOP_K,
            "repetition_penalty": repetition_penalty or settings.REPETITION_PENALTY,
            "stop_sequences": ["\nUser:", "User:", "\nSystem:", "System:"]
        }
        
        # Build request body
        body = {
            "input": prompt,
            "parameters": parameters,
            "model_id": self.model_id,
            "project_id": self.project_id
        }
        
        # Make request
        response = requests.post(endpoint, headers=headers, json=body)
        response.raise_for_status()
        
        # Extract generated text
        result = response.json()
        generated_text = result["results"][0]["generated_text"]
        
        return generated_text
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Chat completion using Granite model
        Converts messages to prompt format
        """
        
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        # Generate response
        response = self.generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to Granite prompt format"""
        
        prompt_parts = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        # Add final assistant prompt
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using IBM Slate model"""
        
        access_token = self._get_access_token()
        
        # Construct API endpoint
        endpoint = f"{self.url}/ml/v1/text/embeddings?version=2023-05-29"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Build request body
        body = {
            "inputs": texts,
            "model_id": settings.WATSONX_EMBEDDING_MODEL,
            "project_id": self.project_id
        }
        
        # Make request
        response = requests.post(endpoint, headers=headers, json=body)
        response.raise_for_status()
        
        # Extract embeddings
        result = response.json()
        embeddings = [item["embedding"] for item in result["results"]]
        
        return embeddings


# Async wrapper for compatibility with existing code
class ChatCompletions:
    """Chat completions interface (OpenAI-compatible)"""
    
    def __init__(self, client: 'AsyncIBMWatsonxClient'):
        self.client = client
    
    async def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Any:
        """Create chat completion (OpenAI-compatible interface)"""
        return await self.client._chat_completions_create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )


class Chat:
    """Chat interface (OpenAI-compatible)"""
    
    def __init__(self, client: 'AsyncIBMWatsonxClient'):
        self.completions = ChatCompletions(client)


class AsyncIBMWatsonxClient:
    """Async wrapper for IBM watsonx client (OpenAI-compatible interface)"""
    
    def __init__(self):
        self.client = IBMWatsonxClient()
        self.chat = Chat(self)
    
    async def _chat_completions_create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Any:
        """
        Internal chat completion method
        Returns response in OpenAI-compatible format
        """
        
        # Generate response using sync client
        # In production, use aiohttp for true async
        response_text = self.client.chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Create response object with OpenAI-compatible structure
        class Message:
            def __init__(self, content: str):
                self.content = content
                self.role = "assistant"
        
        class Choice:
            def __init__(self, message: Message):
                self.message = message
                self.finish_reason = "stop"
        
        class Response:
            def __init__(self, content: str, model: str):
                self.choices = [Choice(Message(content))]
                self.model = model
                self.usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
        
        return Response(response_text, model)


# Factory function to create client
def create_watsonx_client() -> IBMWatsonxClient:
    """Create IBM watsonx client"""
    if not settings.watsonx_available:
        raise ValueError(
            "IBM watsonx.ai credentials not configured. "
            "Please set IBM_CLOUD_API_KEY and WATSONX_PROJECT_ID in .env"
        )
    return IBMWatsonxClient()


def create_async_watsonx_client() -> AsyncIBMWatsonxClient:
    """Create async IBM watsonx client"""
    if not settings.watsonx_available:
        raise ValueError(
            "IBM watsonx.ai credentials not configured. "
            "Please set IBM_CLOUD_API_KEY and WATSONX_PROJECT_ID in .env"
        )
    return AsyncIBMWatsonxClient()

# Made with Bob
