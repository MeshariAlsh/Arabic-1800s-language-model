MIN_WORDS = 100   # smallest passage size
MAX_WORDS = 300   # largest passage size


def split_book(text: str) -> list[str]:
    """ Arabic: تقسيم نص التدريب إلى مقاطع من ١٠٠ إلى ٣٠٠ كلمة عند حدود الأسطر.
        English: Split a training text into passages of 100 to 300 words at line boundaries.
    """

    passages = []
    buffer = []    # lines collected for the current passage
    count = 0      # words in the buffer

    # قسِّم النص إلى أسطر غير فارغة.
    # Split the text into non-empty lines.
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        raise ValueError("No text found in the input file")

    for line in lines:
        words = len(line.split())

        # تجاوز السطر الأطول من الحد الأقصى، وابدأ مقطعًا جديدًا.
        # Skip a line longer than the maximum, and start a new passage.
        if words > MAX_WORDS:
            buffer = []
            count = 0
            continue

        # إن تجاوز المقطع الحد الأقصى بإضافة هذا السطر، فابدأ من جديد.
        # If adding this line would pass the maximum, start again.
        if count + words > MAX_WORDS:
            buffer = []
            count = 0

        # أضف السطر إلى المقطع الحالي.
        # Add the line to the current passage.
        buffer.append(line)
        count += words

        # احفظ المقطع حين يبلغ الحد الأدنى، وابدأ مقطعًا جديدًا.
        # Save the passage once it reaches the minimum, and start a new one.
        if count >= MIN_WORDS:
            passages.append("\n".join(buffer))
            buffer = []
            count = 0

    return passages


def main():
    """ Arabic: واجهة سطر الأوامر لهذه الوحدة البرمجية.
        English: Command-line interface to the module.
    """

    import json
    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser(
        description="Split a training text into passages of 100 to 300 words for SFT. "
                    "تقسيم نص التدريب إلى مقاطع من ١٠٠ إلى ٣٠٠ كلمة لبيانات الضبط الدقيق."
    )
    parser.add_argument("infile", help="Training text file, e.g. data/splits/train-clean-book-004.txt")
    parser.add_argument("outdir", help="Folder for the passages file, e.g. data/SFT")
    args = parser.parse_args()

    try:
        # اقرأ نص التدريب.
        # Read the training text.
        with open(args.infile, "r", encoding="utf-8") as infile:
            text = infile.read()

        # قسِّم النص إلى مقاطع عند حدود الأسطر.
        # Split the text into passages at line boundaries.
        passages = split_book(text)

        # استخرج رقم الكتاب من اسم الملف.
        # Get the book ID from the file name.
        book_id = Path(args.infile).stem.removeprefix("train-").removeprefix("clean-")

        # أنشئ مجلد الإخراج إن لم يكن موجودًا.
        # Create the output folder if it does not exist.
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        # احفظ كل مقطع في سطر مستقل مع معرِّف خاص به.
        # Save each passage on its own line with its own ID.
        with open(outdir / f"passages-{book_id}.jsonl", "w", encoding="utf-8") as outfile:
            for n, passage in enumerate(passages):
                record = {"id": f"{book_id}-{n:04d}", "source": book_id, "passage": passage}
                outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

        # اطبع عدد المقاطع وأصغر وأكبر عدد كلمات للتحقق.
        # Print the passage count and the smallest and largest word counts as a check.
        word_counts = [len(p.split()) for p in passages]
        print(f"{book_id}: {len(passages)} passages")
        if word_counts:
            print(f"Words per passage: min {min(word_counts)}, max {max(word_counts)}")

    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()