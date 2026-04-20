from openai import OpenAI
from gtts import gTTS
from moviepy.editor import *
import requests

client = OpenAI()

# STEP 1: Generate content
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Create a kids story with scenes and image prompts"
    }]
)

content = response.choices[0].message.content
print(content)

# STEP 2: Dummy prompts (replace with parsed output later)
scenes = [
    "cute monkey in jungle cartoon",
    "monkey climbing tree",
    "monkey thinking",
    "monkey grabbing banana",
    "monkey sharing happily"
]

# STEP 3: Generate images
images = []
for i, prompt in enumerate(scenes):
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
    
    url = result.data[0].url
    img_data = requests.get(url).content
    
    filename = f"scene_{i}.png"
    with open(filename, "wb") as f:
        f.write(img_data)
    
    images.append(filename)

# STEP 4: Voice
tts = gTTS("This is a kids story")
tts.save("voice.mp3")

# STEP 5: Video
clips = [ImageClip(img).set_duration(3) for img in images]
video = concatenate_videoclips(clips)

audio = AudioFileClip("voice.mp3")
video = video.set_audio(audio)

video.write_videofile("final_video.mp4", fps=24)
