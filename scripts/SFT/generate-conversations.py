from dotenv import load_dotenv
from openai import OpenAI
import json
from argparse import ArgumentParser

load_dotenv()        # reads .env and sets OPENAI_API_KEY for this script
client = OpenAI()   # reads OPENAI_API_KEY from the environment

MODEL = "gpt-6-luna"   # exact model ID from the OpenAI platform

SYSTEM_PROMPT = """You turn passages from nineteenth-century Arabic texts into short conversations.

Write a conversation of 2 to 4 exchanges between a curious modern visitor and the author of the passage.

Rules:
1. The visitor's questions must be in Modern Standard Arabic and must lead naturally to the reply that follows.
2. Every reply from the author must be copied exactly from the passage. Do not add, remove, or change any word, letter, or diacritic.
3. You may split the passage into several replies and leave parts of it unused. Each reply must be one continuous stretch of the passage.
4. Do not mention the book, the author's name, or any fact that is not in the passage.
5. Vary the questions. Use direct questions, requests to describe something, and requests for an opinion.


Output only JSON in this form:
{"turns": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}"""


def ask_llm(passage: str) -> str:
    """ Arabic: إرسال المقطع إلى النموذج وإرجاع رده نصًّا.
        English: Send a passage to the model and return its reply as text.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": passage},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def main():
    parser = ArgumentParser(description="Generate SFT conversations from passages.")
    parser.add_argument("infile", help="Passages file, e.g. data/SFT/passages/passages-book-004.jsonl")
    args = parser.parse_args()

    # اقرأ أول مقطع فقط للتجربة.
    # Read only the first passage, as a test.
    with open(args.infile, encoding="utf-8") as f:
        first = json.loads(f.readline())

    print("PASSAGE:\n", first["passage"], "\n")
    print("REPLY:\n", ask_llm(first["passage"]))


if __name__ == "__main__":
    main()