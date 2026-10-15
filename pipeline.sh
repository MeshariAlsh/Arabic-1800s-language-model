#!/bin/bash
# Pipeline for arabic-1800s-language-model.
# Author: MeshariAlsh
# Run from the project root:  ./pipeline.sh splits   or   ./pipeline.sh all(later)

set -e        
PYTHON=python3
 
# --- Stage 0: raw -> clean -------------------------------------------------
# Disabled until every book in data/raw/ has an entry in BOOK_RULES.
# clean_text() {
#     mkdir -p data/clean
#     for f in data/raw/*.txt; do
#         $PYTHON scripts/preprocess.py "$f" "data/clean/clean-$(basename "$f")"
#     done
# }
 
# --- Stage 1: clean -> train / heldout ---------------------------------------
splits() {
    for f in data/clean/*.txt; do
        $PYTHON scripts/make-splits.py "$f" data/splits
    done
}
 
# --- Stage 2: train -> passages ----------------------------------------------
passages() {
    for f in data/splits/train/*.txt; do
           $PYTHON scripts/SFT/make-passages.py "$f" data/SFT/passages
    done
}
 
# --- Stage 3: passages -> conversations ---------------------

conversations() {
    for f in data/SFT/passages/*.jsonl; do
           $PYTHON scripts/SFT/generate-conversations.py "$f" data/SFT/conversations --n 60
    done
}

# --- Stage 4: conversations -> SFT train / validation files ---
export_sft() {
    $PYTHON scripts/SFT/export-sft.py data/SFT/conversations/conversations.jsonl data/SFT/sft_training
}


case "$1" in
    splits)    splits ;;
    passages)  passages ;;
    conversations)  conversations ;;
    export)          export_sft ;;
    *)
        echo "Usage: ./pipeline.sh {splits|passages}"
        exit 1
        ;;
esac