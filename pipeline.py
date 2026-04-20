import os
import re
import requests
from openai import OpenAI
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# STEP 0: CHAT HISTORY INPUT
# =========================
# 👉 Paste Warp / agent / previous conversation here
CHAT_HISTORY = """
User: make a kids story about space monkey
Assistant: ...
User: make it more emotional and cinematic
Assistant: ...
"""

# =========================
# STEP 1: GENERATE STORY
# =========================
PROMPT = f"""
You are a viral YouTube kids story creator.

Use this chat history:
{CHAT_HISTORY}

Now generate:

Title:
...

Story:
(engaging, emotional, kid-friendly)

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

# =========================
# STEP 2: EXTRACT STORY
# =========================
def extract_block(text, start, end=None):
    part = text.split(start, 1)
    if len(part) < 2:
        raise ValueError(f"{start} not found in AI output")

    result = part[1]
    if end and end in result:
        result = result.split(end, 1)[0]

    return result.strip()

story = extract_block(content, "Story:", "Scenes:")

# =========================
# STEP 3: IMAGE PROMPTS
# =========================
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

if len(image_prompts) < 3:
    raise ValueError("Image prompts not generated properly")

# =========================
# STEP 4: GENERATE IMAGES
# =========================
images = []

for i, prompt in enumerate(image_prompts):
    enhanced_prompt = (
        prompt +
        ", Pixar style, cinematic lighting, ultra detailed, 3D animation, vibrant colors"
    )

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

print("✅ Images generated")

# =========================
# STEP 5: UPSCALE
# =========================
def upscale_to_4k(path):
    img = Image.open(path)
    img = img.resize((3840, 2160))
    img.save(path)

for img in images:
    upscale_to_4k(img)

print("✅ Upscaled")

# =========================
# STEP 6: MAKE VOICE SCRIPT (IMPORTANT UPGRADE)
# =========================
VOICE_PROMPT = f"""
Convert this story into a professional YouTube narration script.

Rules:
- emotional storytelling
- natural speaking rhythm
- pauses like (...)
- very engaging for kids
- cinematic tone

Story:
{story}
"""

voice_script = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": VOICE_PROMPT}]
).choices[0].message.content

# =========================
# STEP 7: OPENAI TTS (BETTER VOICE)
# =========================
speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",   # try: alloy, verse, coral, sage
    input=voice_script
)

with open("voice.mp3", "wb") as f:
    f.write(speech.read())

print("✅ Voice generated (OpenAI TTS)")

# =========================
# STEP 8: CREATE VIDEO
# =========================
audio = AudioFileClip("voice.mp3")
duration = audio.duration / len(images)

clips = [ImageClip(img).set_duration(duration) for img in images]

video = concatenate_videoclips(clips)
video = video.set_audio(audio)

video.write_videofile(
    "final_video.mp4",
    fps=24,
    codec="libx264",
    bitrate="8000k"
)

print("🎬 FINAL VIDEO READY")
