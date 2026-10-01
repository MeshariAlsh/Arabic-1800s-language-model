import os 
import re 

BOOK_RULES = {
    "book_001": {
        "start": ["المقدمة"],
        "end": ["تعليق"],
    },
    "newspaper-001": {
        "start": ["فاتحة الجريدة"],
        "end": ["(تمت كلمات «العروة الوثقى» بفضل الله.)"],
    },
}

def clean_book(text: str, book_id: str ) -> str:
    START_MARKERS = BOOK_RULES[book_id]["start"]
    END_MARKERS = BOOK_RULES[book_id]["end"]

    PAGE_NUMBER_PATTERN = r"\(ص\s*[\u0660-\u0669]+(?:\s*،\s*[\u0660-\u0669]+)*\s*\)"
    FOOTNOTE_MARKER_PATTERN = r"(?<=[ء-يً-ْٰ.،؛:!?؟»)])[\u0660-\u0669]+"
    FOOTNOTE_LINE_PATTERN = r"^[\u0660-\u0669]+\s+"

    
    lines = text.splitlines()
    output = []
    started = False


    for line in lines:
        line = line.strip()

        
        # تجاوز الأسطر حتى تصل إلى أحد عناوين البداية.
        # Skip lines until a start heading is found.
        if not started: 
            if line in START_MARKERS:
                started = True
            else: 
                continue

        # توقّف عند الوصول إلى إحدى علامات النهاية.
        # Stop at an end marker.
        if line in END_MARKERS:
            break
        
        # تجاوز الأسطر الزخرفية المستقلة.
        # Skip standalone decorative lines.
        if line in {"•••", "* * *"}:
            continue

        # تجاوز الأسطر التي تبدأ بأرقام عربية متبوعة بمسافة بيضاء.
        # Skip lines starting with Arabic digits followed by whitespace.
        if re.search(FOOTNOTE_LINE_PATTERN, line):
            continue

        # أزل الأنماط غير المرغوبة من داخل السطر الحالي.
        # Clean fragments inside the current line.
        line = re.sub(PAGE_NUMBER_PATTERN, "", line)
        line = re.sub(FOOTNOTE_MARKER_PATTERN, "", line)

        # اختزل المسافات وعلامات الجدولة المتتابعة إلى مسافة واحدة.
        # Collapse repeated spaces and tabs.
        line = re.sub(r"[ \t]+", " ", line).strip()

        # أبقِ سطرًا فارغًا واحدًا كحد أقصى بين الفقرات.
        # Keep at most one blank line between paragraphs.
        if line == "" and (not output or output[-1] == ""):
            continue

        # الاحتفاظ بالسطر بعد تنظيفه.
        # Keep the cleaned line.
        output.append(line)

    if not started:
        raise ValueError(f"Could not find a start heading: {START_MARKERS}")

    clean_text = "\n".join(output)

    return clean_text




def main():
    """ Arabic: واجهة سطر الأوامر لهذه الوحدة البرمجية.
    
        English: Command-Line interface to the module
    """

    from argparse import ArgumentParser

    parser = ArgumentParser(description='Clean historical Arabic texts using document-specific rules'
                             'تخليص الإبريز في تلخيص باريز ')
    
    parser.add_argument('infile', help="Input text file")
    parser.add_argument('outfile', help="Output text file")
    args = parser.parse_args()

    try:
        with open (args.infile, "r", encoding='utf-8') as infile: 
            text = infile.read()
            clean_text = clean_book(text, "newspaper-001")
            print(f"Word count: {len(clean_text.split()):,}")
        
        with open(args.outfile, "w", encoding="utf-8") as outfile:
            outfile.write(clean_text)

    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

if __name__ == "__main__":
    main()
