from openai import OpenAI
from moviepy.editor import *
import requests
import os
import json
import time
import traceback

# ---------------- CONFIG ----------------
OUTPUT_DIR = "generated_story_video"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- RETRY FUNCTION ----------------
def retry(func, retries=3, delay=3):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed:", e)
            time.sleep(delay)
    print("❌ All retries failed")
    exit()

# ---------------- SAFE JSON PARSER ----------------
def safe_json_parse(text):
    text = text.strip().replace("```json", "").replace("```", "")
    try:
        return json.loads(text)
    except Exception as e:
        print("❌ JSON ERROR:", e)
        print(text)
        exit()

# ---------------- MAIN PIPELINE ----------------
try:
    print("🚀 Starting pipeline...")

    # ---------------- STEP 1: GENERATE STORY ----------------
    def generate_story():
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": """
Return ONLY valid JSON. No explanation.

{
  "title": "string",
  "story": "string",
  "scenes": ["scene1", "scene2", "scene3", "scene4", "scene5"]
}

Create a kids story with moral.
"""
            }]
        )
        return response.choices[0].message.content

    content = retry(generate_story)
    data = safe_json_parse(content)

    title = data["title"]
    story = data["story"]
    scenes = data["scenes"]

    print("✅ TITLE:", title)
    print("✅ STORY:", story)

    # Save story
    with open(f"{OUTPUT_DIR}/story.txt", "w") as f:
        f.write(story)

    # ---------------- STEP 2: GENERATE VOICE ----------------
    def generate_voice():
        audio = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=story
        )

        path = f"{OUTPUT_DIR}/voice.mp3"
        with open(path, "wb") as f:
            f.write(audio.content)

        return path

    voice_path = retry(generate_voice)
    print("✅ Voice created")

    # ---------------- STEP 3: GENERATE IMAGES ----------------
    image_paths = []

    for i, scene in enumerate(scenes):

        def generate_image():
            prompt = f"""
            Cute cartoon kids illustration, Pixar style, bright colors, 3D render.
            Scene: {scene}
            Same main character in all scenes.
            """

            image = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )

            url = image.data[0].url
            img_data = requests.get(url).content

            path = f"{OUTPUT_DIR}/scene_{i+1}.png"
            with open(path, "wb") as f:
                f.write(img_data)

            return path

        path = retry(generate_image)
        image_paths.append(path)

    print("✅ Images generated")

    # ---------------- STEP 4: CREATE VIDEO (VERTICAL SHORTS) ----------------
    def create_video():
        clips = []

        for img in image_paths:
            clip = (
                ImageClip(img)
                .resize(height=1920)
                .set_duration(3)
                .set_position("center")
                .on_color(size=(1080, 1920), color=(0, 0, 0))
            )
            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")

        audio = AudioFileClip(voice_path)
        video = video.set_audio(audio)

        output_video = f"{OUTPUT_DIR}/final_shorts.mp4"

        video.write_videofile(
            output_video,
            fps=24,
            codec="libx264",
            bitrate="8000k"
        )

        return output_video

    output_video = retry(create_video)

    # ---------------- FINAL CHECK ----------------
    if os.path.exists(output_video):
        print("🎉 SUCCESS: Video created!")
        print("📂 LOCATION:", os.path.abspath(output_video))
    else:
        print("❌ ERROR: Video not found")

# ---------------- ERROR HANDLING ----------------
except Exception as e:
    print("❌ PIPELINE FAILED:")
    print(e)
    traceback.print_exc()
