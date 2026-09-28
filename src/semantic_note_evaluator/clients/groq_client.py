from typing import Any

from groq import AsyncGroq

DEFAULT_MODEL: str = "llama-3.3-70b-versatile"


class GroqClient:
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        client: AsyncGroq | None = None,
    ) -> None:
        self.model = model
        self._api_key = api_key
        self._client: AsyncGroq | None = client

    @property
    def client(self) -> AsyncGroq:
        if self._client is None:
            if not self._api_key:
                raise ValueError("GROQ_API_KEY is not configured")
            self._client = AsyncGroq(api_key=self._api_key)
        return self._client

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.5,
    ) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_format,
            temperature=temperature,
        )
        return completion.choices[0].message.content or ""
