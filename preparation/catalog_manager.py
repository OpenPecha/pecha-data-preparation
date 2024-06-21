from pathlib import Path
from collections import defaultdict

from .third_party.leavedonto.leavedonto import LeavedOnto


class CatalogManager:
    def __init__(self, cat_file):
        self.cat_file = Path(cat_file)
        self.works, self.onto = self.parse_cat_file()

    def parse_cat_file(self):
        lo = LeavedOnto(self.cat_file)
        entries = lo.ont.export_all_entries()
        cats_meta = self.__gather_cat_metadata(lo.ont, entries)

        # dict where: key = (text name, uuid), value = [{cat1}, {cat2}, ...]. ("{cat1}" comes from cats_data)
        works = {}
        for cats, data in entries:
            for d in data:
                if d[-2]:
                    key = (d[-2], d[-1])
                    value = []
                    for c in cats:
                        if 'data' not in c:
                            value.append(cats_meta[c])
                    works[key] = value
        return works, lo

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

    def include_new_texts(self, local_path):
        local_path = Path(local_path)
        for f in local_path.glob('*.xlsx'):
            #todo: read with openyxl,
            # extract text name,
            # generate uuid,
            # keep only those not in self.works
            # add (title, uuid) pairs to "unassigned" in onto,
            # export onto as xlsx,
            # update catalog in Drive
            print()
        pass
