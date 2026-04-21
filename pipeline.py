from openai import OpenAI
from moviepy.editor import *
import requests
import os
import json
from PIL import Image, ImageDraw

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_DIR = "generated_story_video"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- STEP 1: GENERATE STORY + HOOK + SCENES ----------------
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": """
        Find a trending kids topic and generate:

        1. Title
        2. Hook (very engaging first 2 seconds)
        3. Story (60-100 words, simple English, moral)
        4. 5 short scenes (1 line each)

        Return JSON:
        {
          "title": "...",
          "hook": "...",
          "story": "...",
          "scenes": ["...", "...", "..."]
        }
        """
    }]
)

content = response.choices[0].message.content
content = content.strip().replace("```json", "").replace("```", "")
data = json.loads(content)

title = data["title"]
hook = data["hook"]
story = data["story"]
scenes = data["scenes"]

print("TITLE:", title)
print("HOOK:", hook)
print("STORY:", story)

# ---------------- SAVE STORY ----------------
with open(f"{OUTPUT_DIR}/story.txt", "w") as f:
    f.write(story)

# ---------------- STEP 2: BETTER VOICE ----------------
audio_response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=story
)

voice_path = f"{OUTPUT_DIR}/voice.mp3"
with open(voice_path, "wb") as f:
    f.write(audio_response.content)

# ---------------- STEP 3: GENERATE IMAGES ----------------
image_paths = []

for i, scene in enumerate(scenes):
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

    image_paths.append(path)

print("✅ Images created")

# ---------------- STEP 4: CREATE HOOK SCREEN ----------------
hook_img = Image.new("RGB", (1080, 1920), color="black")
draw = ImageDraw.Draw(hook_img)

draw.text((100, 900), hook, fill="white")

hook_path = f"{OUTPUT_DIR}/hook.png"
hook_img.save(hook_path)

# ---------------- STEP 5: CREATE VIDEO (VERTICAL SHORTS) ----------------
clips = []

# Hook first
hook_clip = ImageClip(hook_path).set_duration(2)
clips.append(hook_clip)

# Scene clips
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

print("🎬 VIDEO CREATED:", output_video)
