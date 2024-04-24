from pathlib import Path
import json

from preparation import *

in_path = Path('input')
out_path = Path('output')

for f in in_path.glob('*.csv'):
    # parse file
    struct = parse_data_csv(f)

    # export to json
    dump = json.dumps(struct, indent=4, ensure_ascii=False)
    out_file = out_path / f'{f.stem}.json'
    out_file.write_text(dump)

    # export to folder structure
    export_2_folders(struct, out_path)
