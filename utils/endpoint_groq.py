
from groq import Groq, InternalServerError
import time
from rich.console import Console


def call_groq_api(client: Groq, prompt: str, model_name: str) -> str:
    """Call the Groq API to generate a quantum program with error handling."""
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                max_tokens=1024,
                temperature=0,
            )
            return chat_completion.choices[0].message.content
        except InternalServerError as e:
            if attempt < retry_attempts - 1:
                console = Console()
                console.log(
                    f"[yellow]InternalServerError: {e}. Retrying in 30 seconds...[/yellow]")
                time.sleep(30)
            else:
                raise


def call_groq_api_json(client: Groq, prompt: str, model_name: str) -> str:
    """Call the Groq API to generate a quantum program with error handling."""
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                max_tokens=1024,
                temperature=0,
                # Streaming is not supported in JSON mode
                stream=False,
                # Enable JSON mode by setting the response format
                response_format={"type": "json_object"},
            )
            return chat_completion.choices[0].message.content
        except InternalServerError as e:
            if attempt < retry_attempts - 1:
                console = Console()
                console.log(
                    f"[yellow]InternalServerError: {e}. Retrying in 30 seconds...[/yellow]")
                time.sleep(30)
            else:
                raise
