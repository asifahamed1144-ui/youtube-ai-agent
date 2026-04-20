from openai import OpenAI
import requests

client = OpenAI()

def generate_content():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": """
            Create a kids YouTube short with:
            Title, Story, Scenes (5), and Image Prompts.
            Keep it cartoon style.
            """
        }]
    )

    return response.choices[0].message.content


def extract_image_prompts(text):
    lines = text.split("\n")
    prompts = []
    
    capture = False
    for line in lines:
        if "Image Prompts" in line:
            capture = True
            continue
        if capture and line.strip():
            prompts.append(line.strip())

    return prompts


def generate_images(prompts):
    for i, prompt in enumerate(prompts):
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        image_url = result.data[0].url
        img_data = requests.get(image_url).content

        with open(f"scene_{i}.png", "wb") as f:
            f.write(img_data)


if __name__ == "__main__":
    content = generate_content()
    print(content)

    prompts = extract_image_prompts(content)
    generate_images(prompts)

    print("✅ Images created automatically!")
