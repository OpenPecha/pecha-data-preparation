import yaml
from pathlib import Path

from preparation import parse_text_metadata

path = 'input/drive/files'

out = parse_text_metadata(path)
out = yaml.dump(out, allow_unicode=True)
out_file = Path('output/metadata_test.yaml')
out_file.write_text(out)
