

FIVE_PERCENT_OF_WORDS = 0.05

def split_train_test(text: str) ->  tuple[str, str]:

    """ Arabic: تقسيم النص إلى ٩٥٪ للتدريب و٥٪ للاختبار عند حدود الفقرات.
        English: Split the text into 95% train and 5% test at a paragraph boundary.
    """

    # قسِّم النص إلى فقرات، كل سطر غير فارغ فقرة.
    # Split the text into paragraphs, each non-empty line is one paragraph.
    paragraphs = [line.strip() for line in text.split("\n") if line.strip()]
    if not paragraphs:
        raise ValueError("No text found in the input file")

    # احسب العدد الكلي للكلمات في الكتاب.
    # Count the total number of words in the book.
    total_words = 0
    for paragraph in paragraphs:
        total_words += len(paragraph.split())

    # عدد الكلمات المطلوب لجزء الاختبار.
    # Number of words wanted for the test part.
    target = total_words * FIVE_PERCENT_OF_WORDS

    # امشِ من آخر فقرة إلى أولها حتى يبلغ مجموع الكلمات الهدف.
    # Walk from the last paragraph to the first until the word total reaches the target.
    running = 0
    for i in range(len(paragraphs) - 1, -1, -1):
        running += len(paragraphs[i].split())
        if running >= target:
            break

    # تأكد أن جزء التدريب لن يكون فارغًا.
    # Make sure the train part will not be empty.
    if i == 0:
        raise ValueError("Book too short to split, test would take everything")

     # الفقرة i وما بعدها للاختبار، وما قبلها للتدريب.
    # Paragraph i and everything after it is test, everything before it is train.
    test_paragraphs = paragraphs[i:]     # from position i to the end
    train_paragraphs = paragraphs[:i]    # everything before position i

    # أعد تجميع كل جزء نصًّا واحدًا، فقرة في كل سطر.
    # Join each part back into one text, one paragraph per line.
    test_text = "\n".join(test_paragraphs)
    train_text = "\n".join(train_paragraphs)

    return train_text, test_text

def main():
    """ Arabic: واجهة سطر الأوامر لهذه الوحدة البرمجية.
    
        English: Command-Line interface to the module
    """

    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser(description='Takes cleaned historical Arabic texts and output a 95% train/ 5% test split'
                           "تقسيم النص العربي التاريخي النظيف إلى ٩٥٪ للتدريب و٥٪ للاختبار.")
    
    parser.add_argument('infile', help="Cleaned text file")
    parser.add_argument('outdir', help="Folder for the two output files, e.g. data/splits")
    args = parser.parse_args()

    try:
        # اقرأ النص المنظَّف.
        # Read the cleaned text.
        with open (args.infile, "r", encoding='utf-8') as infile: 
            text = infile.read()

            # قسِّم النص إلى جزء للتدريب وجزء للاختبار عند حدود الفقرات.
            # Split the text into train and test parts at a paragraph boundary.
            train_split, test_split = split_train_test(text)

            # أنشئ مجلد الإخراج إن لم يكن موجودًا.
            # Create the output folder if it does not exist.
            book_id = Path(args.infile).stem
            outdir = Path(args.outdir)
            outdir.mkdir(parents=True, exist_ok=True)

        # احفظ كل جزء في ملف مستقل.
        # Save each part to its own file.
        with open(outdir / f'train-{book_id}.txt', "w", encoding="utf-8") as outfile:
            outfile.write(train_split)
        with open(outdir / f"test-{book_id}.txt", "w", encoding="utf-8") as outfile:
            outfile.write(test_split)

    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

if __name__ == "__main__":
    main()
