


def split_train_test(text: str) -> str:
    pass


def main():
    """ Arabic: واجهة سطر الأوامر لهذه الوحدة البرمجية.
    
        English: Command-Line interface to the module
    """

    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser(description='Takes cleaned historical Arabic texts and output a 95% train/ 5% test split'
                           "تقسيم النص العربي التاريخي النظَّيف إلى ٩٥٪ للتدريب و٥٪ للاختبار.")
    
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
