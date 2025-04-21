@app.route("/generate-mcqs", methods=["POST"])
def generate_mcqs():
    data = request.json
    learning_objectives = data.get("learningObjectives", [])
    valid_objectives = [lo for lo in learning_objectives if lo["bloomLevel"] in [1, 2, 3]]

    all_activities = []

    print("🚀 Starting MCQ generation for:", len(valid_objectives), "objectives")

    for lo in valid_objectives:
        print("🎯 Generating for LO:", lo['id'])
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
            print("🧠 GPT raw response:\n", content)

            try:
                cleaned = content.replace("```json", "").replace("```", "").strip()
                activities = json.loads(cleaned)
                all_activities.extend(activities)
            except Exception as parse_err:
                print("❌ Failed to parse GPT content:", parse_err)
                print("📦 GPT response before parsing:\n", content)

        except Exception as gpt_err:
            print("❌ GPT call failed completely:", gpt_err)

    print("✅ Returning", len(all_activities), "activities")
    return jsonify({"activities": all_activities})
