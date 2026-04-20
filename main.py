import openai

def generate_script(topic):
    prompt = f"Create a short kids moral story about {topic} in 100 words."

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']


if __name__ == "__main__":
    topic = "honest lion"
    script = generate_script(topic)
    print(script)
