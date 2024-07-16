from pathlib import Path

from preparation import detect_root_text_citations

root = Path('input/root_text_identification/root_text.txt')
com = Path('input/root_text_identification/commentary.txt')

out = detect_root_text_citations(root, com)
Path('output/root_text_citations_preview.txt').write_text(out)
