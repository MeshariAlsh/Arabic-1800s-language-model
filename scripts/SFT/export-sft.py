import json
import random
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

# التعليمات التي يراها النموذج المدرَّب في بداية كل محادثة، ويجب أن تطابق تعليمات العرض التجريبي.
# The persona prompt the trained model sees at the start of every conversation. Use the same text in the demo.
PERSONA_PROMPT = (
    "أنت كاتب عربي من القرن التاسع عشر. تجيب بلغة عصرك وأسلوبه، "
    "ولا تعرف شيئًا مما حدث بعد زمانك."
)

# مصادر سردية تبقى في التدريب المسبق المستمر وتُستبعد من بيانات الضبط الدقيق.
# Narrative sources kept for continued pretraining but excluded from SFT.
EXCLUDED_SOURCES = {"book-008", "book-009"}

VAL_FRACTION = 0.1   # share of conversations held out for validation
SEED = 42


def to_messages(record: dict) -> list[dict]:
    """ Arabic: تحويل المحادثة إلى رسائل، مع إضافة تعليمات الشخصية في البداية.
        English: Turn a conversation into messages, with the persona prompt added first.
    """
    messages = [{"role": "system", "content": PERSONA_PROMPT}]
    for t in record["turns"]:
        messages.append({"role": t["role"], "content": t["content"]})
    return messages


def write_jsonl(path: Path, rows: list[dict]) -> None:
    """ Arabic: حفظ القائمة في ملف، كل عنصر في سطر مستقل.
        English: Save a list to a file, one item per line.
    """
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    """ Arabic: واجهة سطر الأوامر لهذه الوحدة البرمجية.
        English: Command-line interface to the module.
    """
    parser = ArgumentParser(description="Export verified conversations as SFT train and validation files.")
    parser.add_argument("infile", help="Verified conversations, e.g. data/SFT/conversations/conversations.jsonl")
    parser.add_argument("outdir", help="Folder for the output files, e.g. data/SFT")
    args = parser.parse_args()

    try:
        # اقرأ المحادثات الناجحة.
        # Read the verified conversations.
        with open(args.infile, encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        # استبعد المصادر السردية.
        # Drop the narrative sources.
        kept = [r for r in records if r["source"] not in EXCLUDED_SOURCES]
        dropped = len(records) - len(kept)
        if not kept:
            raise ValueError("No conversations left after excluding sources")

        # اخلط المحادثات بترتيب ثابت ثم قسّمها.
        # Shuffle with a fixed seed, then split.
        random.Random(SEED).shuffle(kept)
        n_val = max(1, int(len(kept) * VAL_FRACTION))
        val, train = kept[:n_val], kept[n_val:]

        # احفظ الرسائل فقط، دون الحقول الإضافية.
        # Save only the messages, without the extra fields.
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        write_jsonl(outdir / "sft_train.jsonl", [{"messages": to_messages(r)} for r in train])
        write_jsonl(outdir / "sft_val.jsonl", [{"messages": to_messages(r)} for r in val])

        # اطبع الأعداد ومصدر كل محادثة للتحقق.
        # Print the counts and where conversations came from, as a check.
        print(f"Read {len(records)} conversations, excluded {dropped} from {sorted(EXCLUDED_SOURCES)}")
        print(f"Train {len(train)}, validation {len(val)}")
        for source, n in sorted(Counter(r["source"] for r in kept).items()):
            print(f"  {source}: {n}")

    except (OSError, UnicodeError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()