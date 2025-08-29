import os
from openai import OpenAI

key = os.getenv("OPENAI_API_KEY")
print("Cheie setată:", key[:10] + "..." if key else "NU E SETATĂ")

client = OpenAI(api_key=key)
resp = client.embeddings.create(model="text-embedding-3-small", input=["ping"])
print("Totul funcționează, embedding dim:", len(resp.data[0].embedding))
