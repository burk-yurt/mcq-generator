# Deployed version for Render with OpenAI v1.0+ support and full debug logging
import os
import sys
import json
import openai
from flask import Flask, request, jsonify

# Force print() logs to show up in Render
sys.stdout.reconfigure(line_buffering=True)

# Initialize OpenAI client (v1.0+ syntax)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/generate-mcqs", methods=["POST"])
def generate_mcqs():
    print("🔥 Received POST to /generate-mcqs")

    data = request.json
    print("📦 Request data:", data)

    learning_objectives = data.get("learningObjectives", [])
    print("🎯 Number of objectives:", len(learning_objectives))

    valid_objectives = [lo for lo in learning_objectives if lo["bloomLevel"] in [1, 2, 3]]
    all_activities = []

    for lo in valid_objectives:
        print("📝 Processing:", lo["id"])
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
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an instructional assistant who creates multiple choice questions from course objectives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            content = response.choices[0].message.content
            print("🧠 GPT raw response:\n", content)

            try:
                cleaned = content.replace("```json", "").replace("```", "").strip()
                activities = json.loads(cleaned)
                all_activities.extend(activities)
                print(f"✅ Parsed {len(activities)} activities")
            except Exception as parse_err:
                print("❌ Failed to parse GPT response:", parse_err)
                print("📦 Unparsed GPT content:\n", content)

        except Exception as gpt_err:
            print("❌ GPT call failed:", gpt_err)

    print(f"📤 Returning {len(all_activities)} activities to client")
    return jsonify({"activities": all_activities})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
