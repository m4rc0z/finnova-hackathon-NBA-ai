import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def openai():    
    client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    )

    response = client.responses.create(
        model="gpt-5.6-luna",
        input="write a haiku about ai",
        store=True,
    )

print(response.output_text);

def main():
    print("Hello from finnova-hackathon-nba-ai!")


if __name__ == "__main__":
    main()
