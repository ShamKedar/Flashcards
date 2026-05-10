import os
import pymysql
from flask import Flask, request, json, jsonify
from flask_cors import CORS
from uuid import uuid4
from openai import OpenAI

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1",
)

def llm(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful flashcard generator. You must always format your output strictly as 'HINT: [your hint text here] ||| ANSWER: [your answer text here]'. Do not include any other conversational filler text."
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

@app.route('/process', methods=['POST'])
def process_query():
    data = request.json
    query_text = data.get("text", "")

    full_prompt = (
        f"Create a flashcard with a concise hint and an answer based on this input text:\n{query_text}"
    )

    ai_answer = llm(full_prompt)
    return jsonify({"response": ai_answer})

# ROUTE 2: Saves to Aiven ONLY when the user clicks 'Save'
@app.route('/save', methods=['POST'])
def save_card():
    data = request.json
    query_text = data.get("text", "")
    ai_answer = data.get("flashcard", "")

    try:
        if "|||" in ai_answer:
            hint_part, answer_part = ai_answer.split("|||")
            hint = hint_part.replace("HINT:", "").strip()
            answer = answer_part.replace("ANSWER:", "").strip()
        else:
            # Fallback if AI skips formatting rules
            hint = "Review Input"
            answer = ai_answer.strip()
            
    except Exception as parse_error:
        return jsonify({"status": "error", "message": f"Parsing failed: {str(parse_error)}"}), 400

    # Insert separated values into Aiven
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO flashcards (user_input, hint, answer) VALUES (%s, %s, %s)"
            cursor.execute(sql, (query_text, hint, answer))
        connection.commit()
        connection.close()
        return jsonify({"status": "success", "message": "Saved into structured columns!"})
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)