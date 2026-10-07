from dotenv import load_dotenv
from openai import OpenAI
import json
from argparse import ArgumentParser
import os
import random
from pathlib import Path
from openai import APIError

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
7. Each reply must make sense on its own. Do not start a reply with a word that refers to something you left out, such as a pronoun or a word like "because", "then", or "the first", unless what it refers to is in an earlier reply.


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


REPORTED_SPEECH = ("فقال", "فقالت", "قال", "قالت", "وقال", "وقالت")
END_PUNCTUATION = ".،؛:!؟?"

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
        if t.get("role") != "assistant":
            continue
        content = norm(t.get("content", ""))

        # ارفض الرد الذي ينتهي في منتصف الكلام.
        # Reject a reply that ends mid-sentence.
        if content.endswith(":"):
            return "reply ends mid-sentence"

        # ارفض الرد الذي ينقل كلام غير الكاتب.
        # Reject a reply that reports someone else's speech.
        if content.startswith(REPORTED_SPEECH):
            return "reply is reported speech"

        # تجاهل علامة الترقيم الأخيرة فقط عند المقارنة.
        # Ignore only the final punctuation mark when comparing.
        core = content.rstrip(END_PUNCTUATION + " ")
        if core not in norm(passage):
            return "assistant reply not verbatim"

    return None

def looks_like_list(passage: str) -> bool:
    """ Arabic: هل المقطع قائمة (أسطر قصيرة) لا نصًّا متصلًا؟
        English: Is the passage a list of short lines rather than running text?
    """
    lines = passage.split("\n")
    avg = sum(len(line.split()) for line in lines) / len(lines)
    return avg < MIN_AVG_WORDS

def main():
    parser = ArgumentParser(description="Generate SFT conversations from passages.")
    parser.add_argument("infile", help="Passages file, e.g. data/SFT/passages/passages-book-006.jsonl")
    parser.add_argument("outdir", help="Folder for the results, e.g. data/SFT/conversations")
    parser.add_argument("--n", type=int, default=5, help="How many passages to sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # اقرأ كل المقاطع، واستبعد القوائم، ثم اختر عيّنة ثابتة.
    # Read all passages, drop list-like ones, then pick a fixed sample.
    with open(args.infile, encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    usable = [r for r in records if not looks_like_list(r["passage"])]
    picked = random.Random(args.seed).sample(usable, min(args.n, len(usable)))
    print(f"{len(records)} passages, {len(records) - len(usable)} list-like dropped, {len(picked)} sampled")

    passed = failed = skipped = 0
    for r in picked:
        # اطلب الرد، وإن فشل الاتصال فتجاوز المقطع دون حفظ شيء.
        # Ask for the reply. If the API call fails, skip the passage without saving anything.
        try:
            raw = ask_llm(r["passage"])
        except APIError as e:
            print(f"{r['id']}: API error, skipped ({e})")
            skipped += 1
            continue

        # حوِّل الرد وتحقَّق منه.
        # Parse the reply and verify it.
        turns = parse(raw)
        reason = "invalid JSON" if turns is None else verify(turns, r["passage"])

        # احفظ الناجح والمرفوض كلًّا في ملفه.
        # Save passes and failures to their own files.
        record = {**r, "model": MODEL, "turns": turns, "reason": reason}
        name = "conversations.jsonl" if reason is None else "rejected.jsonl"
        with open(outdir / name, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        if reason is None:
            passed += 1
        else:
            failed += 1
        print(f"{r['id']}: {reason or 'passed'}")

    print(f"\n{passed} passed, {failed} rejected, {skipped} skipped")

if __name__ == "__main__":
    main()