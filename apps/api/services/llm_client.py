"""
LLM client - OpenAI-compatible client for llama.cpp/vLLM
"""
from openai import OpenAI
import os

class LLMClient:
    """Client for LLM inference using OpenAI-compatible API"""

    def __init__(self):
        vllm_url = os.getenv("VLLM_URL", "http://localhost:8000")
        # Use OpenAI client with custom base URL
        self.client = OpenAI(
            base_url=f"{vllm_url}/v1",
            api_key="not-needed"  # llama.cpp doesn't require API key
        )
        self.model = "basirah-llm"
        print(f"✓ LLM client initialized: {vllm_url}")

    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.3
    ) -> str:
        """
        Generate completion from LLM

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stop=None
        )

        return response.choices[0].message.content
