import ollama

SYSTEM_PROMPT = """
You are CropDoctor AI.

You are an AI agriculture expert.

Answer ONLY agriculture and plant disease related questions.

Use simple English.

Keep every answer short.

Maximum 100 words.

Use bullet points whenever possible.
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
            ],
            options={
                "num_predict": 100,
                "temperature": 0.2,
                "top_p": 0.8,
                "num_ctx": 1024
            }
        )

        return response["message"]["content"]

    except Exception as e:
        return f"❌ Ollama Error: {str(e)}"