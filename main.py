from openai import OpenAI
import os
import json
from datetime import datetime

# =========================
# OPENAI CLIENT
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# MEMORY PATH (IMPORTANT FIX)
# =========================
MEMORY_FILE = "youtube-ai-agent/memory.json"

# =========================
# LOAD MEMORY
# =========================
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"videos": [], "learned_patterns": {}}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

memory = load_memory()

# =========================
# LEARNING ENGINE
# =========================
def get_strategy():
    if not memory["videos"]:
        return "Create emotional, simple, moral kids stories."

    prompt = f"""
Analyze these past videos:

{json.dumps(memory, indent=2)}

Tell me:
- what worked
- what failed
- best storytelling pattern for viral kids shorts
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content

strategy = get_strategy()

# =========================
# GENERATE VIRAL SCRIPT
# =========================
def generate_script(topic):
    prompt = f"""
You are a viral YouTube Kids storyteller.

Use this strategy:
{strategy}

Create a 100-word moral story about: {topic}

Rules:
- very simple English
- emotional
- strong moral lesson
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# =========================
# VIRAL SCORE (AI PREDICTION)
# =========================
def predict_score(script):
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Rate this kids story viral potential 0-100:\n\n{script}\n\nReturn only number."
        }]
    )

    import re
    return int(re.findall(r"\d+", res.choices[0].message.content)[0])

# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":
    topic = "honest lion"

    script = generate_script(topic)
    score = predict_score(script)

    print("\n🎬 Generated Story:\n")
    print(script)

    print("\n📊 Viral Score:", score)

    # =========================
    # SAVE TO MEMORY (SELF-LEARNING)
    # =========================
    memory["videos"].append({
        "topic": topic,
        "script": script,
        "score": score,
        "created_at": str(datetime.now())
    })

    # update learning pattern
    if score > 80:
        memory["learned_patterns"]["winning_style"] = "emotional + simple + moral ending"

    if score < 60:
        memory["learned_patterns"]["fix_needed"] = "improve hook and emotional impact"

    save_memory(memory)

    print("\n💾 Memory updated successfully")
