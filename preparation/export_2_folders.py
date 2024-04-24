from pathlib import Path


def format_meta(meta):
    # generates the yaml string corresponding to the content of meta.yaml
    pass


def format_content(text):
    # formats the text corresponding to this file.
    # adds the header as required ("direction: ltr", etc.)
    pass


def recursive_walk(struct, cur_path):
    # recursive function that walks through struct and does three things at each level:

    # 1. create the nested folder structure. uses cur_path argument

    # 2. calls format_meta() and writes the output to meta.yaml
    format_meta(struct['meta'])

    # 3. calls format_content() and writes the output to bo.md
    format_content(struct['text'])

    pass


def export_2_folders(struct, out_path):
    meta = struct['meta']
    cats = struct['cats']

    # create root folder
    root_folder = Path(out_path / meta['title']['BO'][:250])  # truncate at 250 chars for folder name length limitation
    root_folder.mkdir(exist_ok=True)

    # recursive function that walks through struct and
    recursive_walk(struct, root_folder)
    print()
