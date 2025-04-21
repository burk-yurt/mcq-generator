from flask import Flask, request, jsonify
import openai
import os
import json

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/generate-mcqs", methods=["POST"])
def generate_mcqs():
    data = request.json
    learning_objectives = data.get("learningObjectives", [])
    valid_objectives = [lo for lo in learning_objectives if lo["bloomLevel"] in [1, 2, 3]]

    all_activities = []

    for lo in valid_objectives:
        prompt = f"""
Generate 3 to 5 multiple choice questions aligned with this learning objective:

ID: {lo['id']}
Title: {lo['title']}
Bloom Level: {lo['bloomLevel']}
Knowledge Type: {lo['knowledgeType']}

Each question should:
- Be multiple choice (4–5 options)
- Have one correct answer
- Be appropriate for the Bloom level and knowledge type
- Output only a JSON array of activities. Each object must include:
  - activityId
  - title
  - type = "multiple-choice"
  - duration = "1 min"
  - linkedLOs (array with the objective ID)
  - question
  - choices
  - correctAnswer

Return ONLY a JSON array of activities. No commentary.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an instructional assistant who creates multiple choice questions from course objectives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            content = response.choices[0].message["content"]
            print("🧠 GPT raw response:", content)

            try:
                cleaned = content.replace("```json", "").replace("```", "").strip()
                activities = json.loads(cleaned)
                all_activities.extend(activities)
            except Exception as e:
                print("❌ Failed to parse GPT content:", e)
                print("📦 GPT response before parsing:", content)

        except Exception as e:
            print("❌ GPT call failed completely:", e)

    return jsonify({"activities": all_activities})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
