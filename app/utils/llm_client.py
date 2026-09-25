import ollama

SYSTEM_PROMPT = """
You are CropDoctor AI, a local agriculture assistant.

Answer only questions about:
- crops and plant diseases
- symptoms and prevention
- pest management
- irrigation
- fertilizers
- farming practices

Use simple English.
Give short, practical answers useful for farmers.
Do not claim to provide live or current information.
If the question is unrelated to agriculture, politely say you only answer agriculture-related questions.
"""

def run_llm(prompt):
    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        return f"❌ Ollama Error: {str(e)}"