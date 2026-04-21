from openai import OpenAI
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw
import requests
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- STEP 1: GET STORY FROM AGENT ----------------
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": """
        Generate a kids story (50-80 words).
        Use simple English.
        Add a moral at the end.
        """
    }]
)

story = response.choices[0].message.content
print("STORY:\n", story)

# ---------------- STEP 2: VOICE ----------------
tts = gTTS(story)
tts.save("voice.mp3")

# ---------------- STEP 3: GENERATE IMAGE FROM STORY ----------------
img_prompt = f"cute cartoon scene based on: {story}, Pixar style, bright colors"

image = client.images.generate(
    model="gpt-image-1",
    prompt=img_prompt,
    size="1024x1024"
)

image_url = image.data[0].url
img_data = requests.get(image_url).content

with open("scene.png", "wb") as f:
    f.write(img_data)

# ---------------- STEP 4: VIDEO ----------------
image_clip = ImageClip("scene.png").set_duration(10)
audio_clip = AudioFileClip("voice.mp3")

video = image_clip.set_audio(audio_clip)
video.write_videofile("output.mp4", fps=24)

print("🎬 VIDEO CREATED: output.mp4")
