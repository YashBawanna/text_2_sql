from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Reply with just the words: API working!"}
    ]
)

print(message.content[0].text)