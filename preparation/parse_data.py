import csv
import copy
from collections import defaultdict


META = 'Metadata'
CATS = 'Categories'
TEXT = 'Text'


def rows_to_sections(rows):
    # split rows in 3: categories, metadata and text
    headings = [META, CATS, TEXT]
    sections = {h: [] for h in headings}
    cur_section = ''
    for r in rows:
        if r[0] in headings and not cur_section:
            cur_section = r[0]
            sections[cur_section].append(r)
        elif cur_section and [cell for cell in r if cell]:
            sections[cur_section].append(r)
        elif not [cell for cell in r if cell]:
            cur_section = ''
        else:
            print('unexpected situation while splitting rows!')

    # strip trailing empty elements (leave empty strings for empty cells)
    for s, rows in sections.items():
        if s != TEXT:
            max = len([r for r in rows[0] if r])
            for r in rows:
                while len(r) > max and not r[-1]:
                    r.pop()
                else:
                    print('unexpected situation while stripping empty els!\n\t', r)
        else:
            for r in rows:
                while not r[-1]:
                    r.pop()

    return sections


def parse_meta(rows):
    meta = defaultdict(dict)
    cols = rows[0][1:]
    for r in rows[1:]:
        key, values = r[0], r[1:]
        meta[key] = defaultdict(dict)
        for i in range(len(cols)):
            meta[key][cols[i]] = values[i]
    return meta


def parse_cats(rows):
    keys = {'cat_bo': 'bo', 'cat_en': 'en'}

    cats = defaultdict(dict)
    cols = rows[0][1:]
    for n, col in enumerate(cols):
        if not cats[col]:
            cats[col] = defaultdict(dict)
        for r in rows[1:]:
            key, values = r[0], r[1:]
            cats[col][keys[key]] = values[n]
    return cats


def fill_paths(rows):
    # add level_numbers so that dicts are always ordered
    longest = 0
    for r in rows[1:]:
        if len(r) > longest:
            longest = len(r)

    for cur_level in range(longest-1):
        cur_num = 1
        for row in rows[1:]:
            if cur_level == len(row)-2:
                row[len(row)-2] = f'{cur_num}_{row[len(row)-2]}'
                cur_num += 1

    # fill paths
    struct = []
    cur_pos = []
    cur_level = 1
    for row in rows[1:]:  # skip row containing section name
        path, content = row[:-1], row[-1]

        # update path
        # 1. remove trailing els in current position
        if cur_pos and len(cur_pos) >= len(path):
            cur_pos = cur_pos[:len(path) - 1]

        # 2. add new part in path
        for n, p in enumerate(path):
            if not cur_pos:
                cur_pos.append(p)
            elif p and len(cur_pos) > n:
                cur_pos.append(p)
            elif p and len(cur_pos) <= n:
                cur_pos.append(p)
            elif p:
                cur_pos[n] = p
            else:
                continue

        struct.append([copy.deepcopy(cur_pos), [cur_level, content]])
        cur_level += 1
    return struct


# from https://stackoverflow.com/a/40401983
def build_tree(tree_list):
    if tree_list:
        return {tree_list[0]: build_tree(tree_list[1:])}
    return {}


# https://stackoverflow.com/a/7205107
def merge(a: dict, b: dict, path=[]):
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] != b[key]:
                raise Exception('Conflict at ' + '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def parse_text(rows):
    struct = fill_paths(rows)

    dicts = {}
    for path, data in struct:
        cur = build_tree(path)
        merge(dicts, cur)

    for branch in struct:
        path, data = branch
        command = 'dicts' + ''.join([f'["{str(p)}"]' for p in path]) + '["data"] = data'
        try:
            exec(command)
        except:
            print('unexpected situation!')
            exit('Error!')
    return dicts


def parse_data_csv(in_path):
    rows = None
    with open(in_path, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    sections = rows_to_sections(rows)
    structure = {
        'meta': parse_meta(sections[META]),
        'cats': parse_cats(sections[CATS]),
        'text': parse_text(sections[TEXT])
    }
    return structure
