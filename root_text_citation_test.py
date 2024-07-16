from pathlib import Path

from preparation import detect_root_text_citations

root = Path('input/root_text_identification/root_text.txt')
com = Path('input/root_text_identification/commentary.txt')

detect_root_text_citations(root, com)
