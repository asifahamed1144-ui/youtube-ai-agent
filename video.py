from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw

# Story from your agent
story = """Milo was a small monkey who loved bananas. One day, he saw a bunch hanging high in a tree. Big animals tried but failed. Milo used a log, climbed up, got the bananas, and shared them. Moral: Think wisely and share happily."""

# Convert story to voice
tts = gTTS(story)
tts.save("voice.mp3")

# Create simple image
img = Image.new('RGB', (1280, 720), color='green')
draw = ImageDraw.Draw(img)
draw.text((50, 300), "Milo the Clever Monkey 🐵", fill="white")

img.save("scene.png")

# Create video
image_clip = ImageClip("scene.png").set_duration(10)
audio_clip = AudioFileClip("voice.mp3")

video = image_clip.set_audio(audio_clip)
video.write_videofile("output.mp4", fps=24)
