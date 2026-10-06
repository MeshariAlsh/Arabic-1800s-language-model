from dotenv import load_dotenv
from openai import OpenAI
import json
from argparse import ArgumentParser
import os

load_dotenv()        # reads .env and sets OPENAI_API_KEY for this script

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set in .env")


MODEL = "gpt-6-luna"   # exact model ID from the OpenAI platform
MIN_AVG_WORDS = 12          

SYSTEM_PROMPT = """You turn passages from nineteenth-century Arabic texts into short conversations.

Write a conversation of 2 to 4 exchanges between a curious modern visitor and the author of the passage.

Rules:
1. The visitor's questions must be in Modern Standard Arabic and must lead naturally to the reply that follows.
2. Every reply from the author must be copied exactly from the passage. Do not add, remove, or change any word, letter, or diacritic.
3. You may split the passage into several replies and leave parts of it unused. Each reply must be one continuous stretch of the passage.
4. Do not mention the book, the author's name, or any fact that is not in the passage.
5. Vary the questions. Use direct questions, requests to describe something, and requests for an opinion.
6. Do not reuse distinctive words or phrases from the reply in the question. Ask the way a curious visitor would, in plain words.


Output only JSON in this form:
{"turns": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}"""


def ask_llm(passage: str) -> str:
    """ Arabic: إرسال المقطع إلى النموذج وإرجاع رده نصًّا.
        English: Send a passage to the model and return its reply as text.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": passage},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content

def parse(raw: str) -> list[dict] | None:
    """ Arabic: تحويل رد النموذج إلى قائمة أدوار، أو None إن لم يكن JSON صالحًا.
        English: Turn the model's reply into a list of turns, or None if it is not valid JSON.
    """
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    turns = data.get("turns") if isinstance(data, dict) else data
    return turns if isinstance(turns, list) else None


def norm(s: str) -> str:
    """ Arabic: توحيد المسافات فقط، دون تغيير الحروف أو التشكيل.
        English: Collapse whitespace only. Letters and diacritics are untouched.
    """
    return " ".join(s.split())


def verify(turns: list[dict], passage: str) -> str | None:
    """ Arabic: التحقق من المحادثة، وإرجاع None إن نجحت أو سبب الرفض إن فشلت.
        English: Check the conversation. Return None if it passes, or the reason it failed.
    """
    roles = [t.get("role") for t in turns]
    if len(turns) % 2 != 0 or roles != ["user", "assistant"] * (len(turns) // 2):
        return "roles do not alternate"
    if not 2 <= len(turns) // 2 <= 4:
        return "wrong number of exchanges"
    for t in turns:
        if t.get("role") == "assistant" and norm(t.get("content", "")) not in norm(passage):
            return "assistant reply not verbatim"
    return None

def main():
    parser = ArgumentParser(description="Generate SFT conversations from passages.")
    parser.add_argument("infile", help="Passages file, e.g. data/SFT/passages/passages-book-004.jsonl")
    args = parser.parse_args()

    # اقرأ مقطعًا من وسط الكتاب للتجربة.
    # Read one passage from the middle of the book, as a test.
    with open(args.infile, encoding="utf-8") as f:
        lines = f.readlines()
    sample = json.loads(lines[200])

    print("PASSAGE:\n", sample["passage"], "\n")
    raw = ask_llm(sample["passage"])
    print("REPLY:\n", raw)

    turns = parse(raw)
    print("\nPARSED:", "failed" if turns is None else f"{len(turns)} turns")
    if turns is not None:
        print("VERIFY:", verify(turns, sample["passage"]) or "passed")

        # اختبار مؤقت: غيِّر حرفًا واحدًا وتأكد أن التحقق يرفضه. احذفه بعد التجربة.
        # Temporary test: change one letter and check that verify rejects it. Remove after testing.
        tampered = [dict(t) for t in turns]
        for t in tampered:
            if t["role"] == "assistant":
                t["content"] = t["content"].replace("ا", "أ", 1)   # change one letter
                break
        print("TAMPERED VERIFY:", verify(tampered, sample["passage"]) or "passed")

if __name__ == "__main__":
    main()