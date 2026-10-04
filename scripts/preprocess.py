import os 
import re 

BOOK_RULES = {
    "book-001": {
        "start": ["المقدمة"],
        "end": ["تعليق"],
        "remove_footnote_lines": True,
    },
    "newspaper-001": {
        "start": ["فاتحة الجريدة"],
        "end": ["(تمت كلمات «العروة الوثقى» بفضل الله.)"],
        "remove_footnote_lines": True,
    },

    "book-004": {
        "start": ["خُطبة الكتاب"],
        "end": [],
        "remove_footnote_lines": False,
    },

    "book-005": {
            "start": ["حال الكون"],
            "end": [],
            "remove_footnote_lines": True,
        },

    "book-006": {
                "start": ["بسم الله الرحمن الرحيم"],
                "end": [],
                "remove_footnote_lines": False,
            },

    "book-007": {
                    "start": ["الفاتحة"],
                    "end": [],
                    "remove_footnote_lines": False,
                    "remove_volume_page_lines": True,
                },

    "book-008": {
                        "start": [],
                        "start_prefix": ["إنني بينما كنت ذات ليلة ضاربًا في أودية"],
                        "end": ["حول هذه النسخة الرقمية"],
                        "remove_footnote_lines": False,
                        "remove_volume_page_lines": True,
                    },
}

def clean_book(text: str, book_id: str ) -> str:
    START_MARKERS = BOOK_RULES[book_id].get("start", [])
    END_MARKERS = BOOK_RULES[book_id].get("end", [])
    REMOVE_FOOTNOTE_LINES =  BOOK_RULES[book_id].get("remove_footnote_lines", False)
    REMOVE_VOLUME_PAGE_LINES = BOOK_RULES[book_id].get("remove_volume_page_lines", False)
    START_PREFIXES = BOOK_RULES[book_id].get("start_prefix", [])

    PAGE_NUMBER_PATTERN = r"\(ص\s*[\u0660-\u0669]+(?:\s*،\s*[\u0660-\u0669]+)*\s*\)"
    FOOTNOTE_MARKER_PATTERN = r"(?<=[ء-يً-ْٰ.،؛:!?؟»)])[\u0660-\u0669]+"
    FOOTNOTE_LINE_PATTERN = r"^[\u0660-\u0669]+\s+"
    BIDIRECTIONAL_CONTROL_PATTERN = r"[\u061C\u200E\u200F\u202A-\u202E\u2066-\u2069]"
    VOLUME_PAGE_LINE_PATTERN = r"^الجزء:\s*\d+\s*¦\s*الصفحة:\s*\d+\s*$"

    
    lines = text.splitlines()
    output = []
    started = False


    for line in lines:
        line = re.sub(BIDIRECTIONAL_CONTROL_PATTERN, "", line)
        line = line.strip()
        
        # تجاوز الأسطر حتى تصل إلى أحد عناوين البداية.
        # Skip lines until a start heading is found.
        if not started:
            if (
                line in START_MARKERS
                or any(line.startswith(prefix) for prefix in START_PREFIXES)
                ):
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

        # تجاوز الأسطر التي تحتوي على بيانات الجزء والصفحة فقط.
        # Skip volume/page metadata.
        if REMOVE_VOLUME_PAGE_LINES and re.fullmatch(VOLUME_PAGE_LINE_PATTERN, line):
            continue

        # تجاوز الأسطر التي تبدأ بأرقام عربية متبوعة بمسافة بيضاء.
        # Skip lines starting with Arabic digits followed by whitespace.
        if REMOVE_FOOTNOTE_LINES and re.search(FOOTNOTE_LINE_PATTERN, line):
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
        raise ValueError(
            f"Could not find a start marker for {book_id}: "
            f"headings={START_MARKERS}, prefixes={START_PREFIXES}"
        )

    clean_text = "\n".join(output)

    return clean_text




def main():
    """ Arabic: واجهة سطر الأوامر لهذه الوحدة البرمجية.
    
        English: Command-Line interface to the module
    """

    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser(description='Clean historical Arabic texts using document-specific rules'
                             'تنظيف النصوص العربية التاريخية باستخدام قواعد مخصصة لكل وثيقة" ')
    
    parser.add_argument('infile', help="Input text file")
    parser.add_argument('outfile', help="Output text file")
    args = parser.parse_args()

    try:
        with open (args.infile, "r", encoding='utf-8') as infile: 
            text = infile.read()
            book_id = Path(args.infile).stem
            clean_text = clean_book(text, book_id)
            print(f"Word count: {len(clean_text.split()):,}")
        
        with open(args.outfile, "w", encoding="utf-8") as outfile:
            outfile.write(clean_text)

    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

if __name__ == "__main__":
    main()
