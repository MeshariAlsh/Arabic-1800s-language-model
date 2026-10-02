# Data Curation

<!-- Enable when README.ar.md is available: [اقرأ بالعربي 🇸🇦](README.ar.md) -->

This directory contains the initial historical Arabic corpus for a project adapting a  language model to nineteenth-century writing and perspectives. Curation is part of the research. Which texts are included, whose voices they represent, and what is removed can all affect the resulting model.

The collection is a small, deliberately selected starting point. It is not a representative sample of all Arabic writing or Arabic-speaking communities in the nineteenth century.

## Current corpus

| File in `clean/` | Work | Author or credited contributors | Original publication | Cleaned words |
| --- | --- | --- | --- | ---: |
| `clean-book-001.txt` | تخليص الإبريز في تلخيص باريز | رفاعة رافع الطهطاوي | 1834 | ~62,000 |
| `clean-book-002.txt` | فحول البلاغة | محمد توفيق البكري | 1895 | 47,873 |
| `clean-book-003.txt` | كشف المخبا عن فنون أوربا | أحمد فارس الشدياق | Verification pending | 102,506 |
| `clean-newspaper-001.txt` | العروة الوثقى | جمال الدين الأفغاني ومحمد عبده | 1884 | 95,822 |

**Current Total: approximately 308,201 words.** Counts are whitespace-separated words, not model tokens. The first count is approximate; the others are reported outputs from the project's counting or preprocessing scripts. They have not all been independently recounted from the complete files.

## Why these texts?

- **تخليص الإبريز في تلخيص باريز:** travel writing and observations of another society provide material about education, customs, religion, and social comparison.
- **فحول البلاغة:** literary selection and explanation provide a different register from travel writing. Much of the quoted poetry and prose predates the nineteenth century. These are classical texts that readers enjoyed them throughout history and stilldo today such they were kept.
- **كشف المخبا عن فنون أوربا:** descriptions of European life, trade, technologies, and institutions broaden the subject matter. Historical edition notes also introduce material from a later point than the initial composition.
- **العروة الوثقى:** journalism adds political argument, current affairs, and editorial positions to a collection otherwise dominated by books.

These selections support comparison between genres and sources. Their accessibility as digital text also influenced selection and is itself a source of bias.

## Scope and selection policy

The primary target is Arabic composed during 1800–1899. A later digital edition may supply that text, but its publication date is not the date of composition.

## Provenance and attribution

The document-level record is [`metadata.csv`](metadata.csv). It should identify the title, author, original publication year, edition year, immediate source, source format, word count, rights evidence, cleaning decisions, and review status.

Two texts—فحول البلاغة and كشف المخبا عن فنون أوربا—were obtained through the **Arabic E-Book Corpus**. The other two were obtained as Hindawi EPUBs and converted to text with Calibre. Metadata should preserve this distinction between the original publisher and the immediate acquisition source.

Source corpus citation:

> Hallberg, Andreas (2024). *The Arabic E-Book Corpus* (Version 1) [Dataset]. University of Gothenburg. https://doi.org/10.5878/7rbh-gy93

The source dataset catalogue lists **CC BY 4.0**. Retain its attribution and record this project's selection and cleaning changes. This source-level statement must not be applied automatically to texts acquired elsewhere. Record each document's rights statement and supporting source separately; public access alone is not a rights statement.

Known publisher/source pages:

- [تخليص الإبريز في تلخيص باريز](https://www.safahat.org/books/46205086/)
- [فحول البلاغة](https://www.safahat.org/books/14758020/)
- [العروة الوثقى](https://www.safahat.org/books/68096495/)
- [Arabic E-Book Corpus catalogue](https://researchdata.se/en/catalogue/dataset/2024-145/1)

Provenance records will be extended with retrieval dates, exact source filenames or identifiers, raw and cleaned SHA-256 hashes, and the preprocessing commit used. These fields are planned; they are not yet complete for every document.

## Cleaning methods

The working layout is:

- `raw/`: preserved source text before project cleaning.
- `clean/`: text selected for the initial corpus.
- `metadata.csv`: document-level provenance and processing records.
- [`../scripts/preprocess.py`](../scripts/preprocess.py): document-specific preprocessing.
- [`../scripts/word-count.py`](../scripts/word-count.py): word counting.

Cleaning aims to remove publishing and conversion artifacts while preserving historical language, punctuation, diacritics, and paragraph boundaries. Historical opinions and factual claims are not silently rewritten to match present-day views. Suspected transcription errors require comparison with a source before correction.

## Cleaning decisions by document

**تخليص الإبريز في تلخيص باريز**

Retained the text from «المقدمة» to before the appended «تعليق»
section. Removed page references, footnote markers, and numbered
footnote lines. Standardized spacing and blank lines.

**فحول البلاغة**

Retained the supplied text after reviewing samples. Kept the
compiler’s explanations alongside the poetry because they are
part of the work.

**كشف المخبا عن فنون أوربا**

Removed invisible U+200F formatting characters. Otherwise retained
the text, including its historical notes, dates, and statistics.

**العروة الوثقى**

Retained the newspaper articles beginning with «فاتحة الجريدة»
and ending with the final «الحق» section. Excluded the introductory
biographies and publishing material. Removed footnote markers,
numbered footnote lines, and decorative separators, and standardized
spacing.

### Review

Reviewed the beginnings, endings, and selected passages of the
texts. Cleaning decisions were made separately for each document
because their formatting and editorial material differ.

### Known limitations

The regex rules are source-specific heuristics:

- A line beginning with Arabic-Indic digits and whitespace may be a numbered list rather than a footnote.
- Multiline footnotes can leave unnumbered continuation lines behind.
- Digits adjacent to words or punctuation are not always footnote references.
- Exact start and end matches depend on the converted file's spelling and layout.
- Plain-text conversion can lose poetry layout or join words; whitespace cleanup cannot reconstruct missing boundaries reliably.

Beginning, ending, and selected internal samples have been reviewed. This is not a complete audit of every file. Review both retained text and removed material before treating a release as quality-checked.

## Representation and expansion

The initial collection is dominated by male, educated elite voices associated with Egypt and the Levant. Travel writing and reformist political or intellectual discussion are prominent. These are specific perspectives, not a single nineteenth-century Arabic personality.

Expansion will seek sources from the Arabian Peninsula, Iraq, the Maghreb, Sudan, and other underrepresented settings, alongside a broader range of genres and social positions. Candidate material includes local newspapers, advertisements, correspondence, petitions, contracts, educational texts, and writing by women where dated, accessible sources can be established.

Geographical diversity alone is insufficient. Another elite author from another region does not necessarily broaden class, gender, or occupational representation. Track author background, place of composition or publication, genre, intended readership, and date separately where evidence permits.

Newspaper scans will first undergo a small extraction and quality-review pilot. More text is not automatically better if transcription errors or uncertain provenance outweigh its contribution.

## Evaluation integrity

Corpus-wide deduplication and train/validation/test splits are pending. 

## Release status and limitations

This is an initial curated collection for exploratory experiments. Training and evaluation results are not yet available. 
