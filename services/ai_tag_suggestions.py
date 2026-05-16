from openai import AsyncOpenAI
from config import settings
import re
import json
from fastapi import HTTPException, status

client = AsyncOpenAI(
    api_key=settings().NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

async def generate_ai_suggestion(title: str, content: str):
    
    model="mistralai/mistral-medium-3.5-128b"

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a technical blog tag suggester.
                        Analyze the blog post and suggest 3-7 relevant tags.

                        Rules:
                        - Tags must be lowercase
                        - Tags can have hyphens but no spaces (e.g. "machine-learning")
                        - Tags should be specific technical terms
                        - Focus on: programming languages, frameworks, concepts, tools
                        - Do not suggest generic tags like "programming" or "technology"

                        Return ONLY a JSON array of strings.
                        Example: ["python", "fastapi", "async", "postgresql"]
                        No explanation, no markdown, just the JSON array."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}, Content: {content}"
                }
            ],
            max_tokens=100,
            temperature=0.5,
        )

        data = response.choices[0].message.content.strip()

        data = re.sub("```json|```", "", data)

        data = json.loads(data)

        if isinstance(data, list):
            return [tag for tag in data if tag and isinstance(tag, str)]

        return []
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    