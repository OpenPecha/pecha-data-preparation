from pathlib import Path
from collections import defaultdict

from openpyxl import load_workbook
from uuid import uuid4

from .third_party.leavedonto.leavedonto import LeavedOnto


def parse_text_metadata(local_path):
    #TODO: add sanity check to ensure that the minimal fields are filled.
    current_texts = {}
    local_path = Path(local_path)
    for f in local_path.glob('*.xlsx'):
        cur_root_text = ''
        current = {}
        wb = load_workbook(f)
        for sheet in wb:
            # find type: commentary or root text or independent
            if 'root' in sheet.title:
                type = 'root_text'
            elif 'commentary' in sheet.title:
                type = 'commentary'
            else:
                type = 'independent'
            # read data
            raw_data = []
            for row in sheet.rows:
                row = [r.value for r in row]
                raw_data.append(row)
            # parse data
            name = ''
            parsed = defaultdict(dict)
            parsed['other']['type'] = type
            langs = raw_data[0][1:]
            keys = [r[0] for r in raw_data[1:] if r[0]]
            for num, key in enumerate(keys):
                for i, lang in enumerate(langs):
                    value = raw_data[num+1][i+1]
                    if not name and lang == 'BO' and key == 'usage_title' and value:
                        name = value
                    elif not name and lang == 'BO' and key == 'title_short' and value:
                        name = value
                    parsed[key][lang] = value

            current[name] = parsed
            if type == 'root_text':
                cur_root_text = name
        # add root text name in commentary metadata
        for name, meta in current.items():
            if meta['other']['type'] == 'commentary':
                meta['other']['root_text'] = cur_root_text
        current_texts.update(current)
    return current_texts


class CatalogManager:
    def __init__(self, cat_file, metadata_path):
        self.cat_file = Path(cat_file)
        self.current_texts = parse_text_metadata(metadata_path)
        self.works, self.uncategorized, self.onto = None, [], None
        self.__parse_cat_file()

    def __parse_cat_file(self):
        lo = LeavedOnto(self.cat_file)
        entries = lo.ont.export_all_entries()
        cats_meta = self.__gather_cat_metadata(lo.ont, entries)

        # dict where: key = (text name, uuid), value = [{cat1}, {cat2}, ...]. ("{cat1}" comes from cats_data)
        works = {}
        for cats, data in entries:
            for d in data:
                if d[4]:
                    key = (d[4], d[5])
                    value = []
                    is_uncat = False
                    for c in cats:
                        if c == 'Uncategorized':
                            is_uncat = True
                        if 'data' not in c and c != 'Uncategorized':
                            value.append(cats_meta[c])
                    if is_uncat and key[0]:
                        self.uncategorized.append(key[0])
                    else:
                        works[key] = value
        self.works = works
        self.onto = lo

    @staticmethod
    def __gather_cat_metadata(onto, entries):
        # dict where: key = category name in tibetan, value = all the corresponding metadata
        cats_data = defaultdict(dict)
        legend = onto.legend
        for cats, data in entries:
            if 'Uncategorized' in cats:
                continue
            for c in cats:
                if c not in cats_data and 'data' not in c:
                    langs = [d[0] for d in data if d[0]]
                    elts = {}
                    for num, l in enumerate(langs):
                        elt = {}
                        for i in range(1, 4):
                            elt[legend[i]] = data[num][i]
                        elts[l] = elt
                    cats_data[elts['bo']['cat_name']] = elts
        return cats_data

    # extract text name,
    # generate uuid,
    # keep only those not in self.works
    # add (title, uuid) pairs to "unassigned" in onto,
    # export onto as xlsx,
    # update catalog in Drive
    def include_new_texts(self, local_path):
        # parse metadata of current texts
        existing_texts = [w[0] for w in self.works.keys()]
        unassigned = []
        for cur, _ in self.current_texts.items():
            if cur in existing_texts:
                print('!!!text with same name exists. if it is different, please change the name!!!')
                # todo: add this info to a report for Data Team to process.
            elif cur in self.uncategorized:
                continue
            else:
                entry = cur, uuid4().hex
                unassigned.append(entry)

        # add new texts to onto
        for k, v in unassigned:
            self.onto.ont.head.children['Uncategorized'].data.append(['', '', '', '', k, v])

        # export updated onto file if any unassigned texts found
        if unassigned:
            if self.onto.ont_path.is_file():
                self.onto.ont_path.unlink()
            self.onto.convert2xlsx(self.onto.ont_path.parent)
            return True
        return False
