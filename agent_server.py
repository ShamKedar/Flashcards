import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from uuid import uuid4
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1",
)

def llm(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a professional assistant for the SUVIDHA Unified Kiosk system."},
            {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@app.route('/process', methods=['POST'])
def process_query():
    data = request.json
    query_text = data.get("text", "")

    def generate_flashcard(query_text):
        full_prompt = (
            f"You are a helpful extension that makes flashcards of hint and answer."
            f"Use the users input to generate the flashcard.\n"
            f"INPUT: {query_text}\n\n"
            f"ANSWER:"
        )

        ai_answer = llm(full_prompt)
        print(ai_answer)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)