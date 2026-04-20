import os
import re
import requests
from openai import OpenAI
from gtts import gTTS
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- STEP 1: GENERATE CONTENT ----------------
PROMPT = """
Respond immediately.

Find a trending kids topic and generate:

Title:
...

Story:
...

Scenes:
1. ...
2. ...
3. ...
4. ...
5. ...

Image Prompts:
1. ...
2. ...
3. ...
4. ...
5. ...

Thumbnail Idea:
...
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": PROMPT}]
)

content = response.choices[0].message.content
print("\n=== AI OUTPUT ===\n", content)

# ---------------- STEP 2: EXTRACT STORY ----------------
def extract_block(text, start, end=None):
    part = text.split(start, 1)
    if len(part) < 2:
        raise ValueError(f"{start} not found in AI output")

    result = part[1]
    if end and end in result:
        result = result.split(end, 1)[0]

    return result.strip()

story = extract_block(content, "Story:", "Scenes:")

# ---------------- STEP 3: EXTRACT IMAGE PROMPTS ----------------
def extract_list(text, header):
    block = extract_block(text, header)
    lines = block.split("\n")

    prompts = []
    for line in lines:
        line = line.strip()
        if line:
            clean = re.sub(r"^\d+[\.\)]\s*", "", line)
            prompts.append(clean)

    return prompts

image_prompts = extract_list(content, "Image Prompts:")

# 🚨 Strict validation (no fallback now)
if len(image_prompts) < 3:
    raise ValueError("Image prompts not generated properly. Fix your agent output format.")

# ---------------- STEP 4: GENERATE IMAGES ----------------
images = []

for i, prompt in enumerate(image_prompts):
    enhanced_prompt = prompt + ", consistent character, Pixar style, 3D, cinematic lighting, bright colors, high detail"

    result = client.images.generate(
        model="gpt-image-1",
        prompt=enhanced_prompt,
        size="1024x1024"
    )

    image_url = result.data[0].url
    img_data = requests.get(image_url).content

    filename = f"scene_{i}.png"
    with open(filename, "wb") as f:
        f.write(img_data)

    images.append(filename)

print("✅ Images generated from AI prompts")

# ---------------- STEP 5: UPSCALE TO 4K ----------------
def upscale_to_4k(path):
    img = Image.open(path)
    img = img.resize((3840, 2160))
    img.save(path)

for img in images:
    upscale_to_4k(img)

print("✅ Upscaled to 4K")

# ---------------- STEP 6: VOICE FROM STORY ----------------
tts = gTTS(story, slow=False)
tts.save("voice.mp3")

print("✅ Voice generated from story")

# ---------------- STEP 7: CREATE VIDEO ----------------
audio = AudioFileClip("voice.mp3")

duration = audio.duration / len(images)

clips = [
    ImageClip(img).set_duration(duration)
    for img in images
]

video = concatenate_videoclips(clips)
video = video.set_audio(audio)

video.write_videofile(
    "final_video.mp4",
    fps=24,
    codec="libx264",
    bitrate="8000k"
)

print("🎬 FINAL VIDEO CREATED")
