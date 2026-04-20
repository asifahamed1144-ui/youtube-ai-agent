from openai import OpenAI
import os

# Initialize client using API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_script(topic):
    prompt = f"""
    Create a short kids moral story (100 words) about {topic}.
    Use simple English.
    Add a clear moral at the end.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    topic = "honest lion"
    script = generate_script(topic)
    
    print("\n🎬 Generated Story:\n")
    print(script)
