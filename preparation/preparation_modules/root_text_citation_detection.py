import io
from tempfile import NamedTemporaryFile

import colibricore

from .root_text_syllable_detection import parse_text


def detect_root_text_citations(root_text, commentary):
    """
    A. Generates trigrams from the root text,
    B. tags all occurences of trigrams in commentary and
    C. discard all matches that don't have a trailing citation end.

    note: arbitrarily chose trigrams as minimal unit.
    :param root_text:
    :param commentary:
    :return:
    """
    def gen_syl_separated_text(in_file):
        text = parse_text(in_file.read_text())
        syls = [r['clean'] for r in text if r['clean']]  # avoid all punctuation to get maximum of matches
        return ' '.join(syls) + '\n'  # hack: trailing \n required by encoder.

    # A. find trigrams
    root_file = NamedTemporaryFile()
    root_class_file = NamedTemporaryFile()
    root_corpus_file = NamedTemporaryFile()

    # write root text file
    root_prepped = gen_syl_separated_text(root_text)
    root_file.write(bytes(root_prepped, 'utf-8'))

    # create class file + encoder
    class_encoder = colibricore.ClassEncoder()
    class_encoder.build(root_file.name)
    class_encoder.save(root_class_file.name)

    class_encoder.encodefile(root_file.name, root_corpus_file.name)

    # class decoder
    class_decoder = colibricore.ClassDecoder(root_class_file.name)

    # trigrams
    trigrams = []
    root_data = colibricore.IndexedCorpus(root_corpus_file.name)
    for sentence in root_data.sentences():
        for trigram in sentence.ngrams(3):
            trigrams.append(trigram.tostring(class_decoder).split(' '))

    # B. Tag all occurences in commentary
    comm = parse_text(commentary.read_text())
    for tri in trigrams:
        for i in range(0, len(comm)-3):
            cur_window = [comm[n]['clean'] for n in range(i, i+3)]
            if tri == cur_window:
                for n in range(i, i+3):
                    comm[n]['match'] = True

    # find beginning and ends of matches
    for i in range(0, len(comm)-2):
        if 'match' not in comm[i] and 'match' in comm[i+1]:
            comm[i+1]['match'] = 'start'
        if 'match' in comm[i] and 'match' not in comm[i+1]:
            comm[i]['match'] = 'end'

    # C. find matches ending with citation end (loops backwards from the end to the beginning)
    ends = ['ཅེས', 'ཤེས', 'ཞེས', 'སོགས', 'གསུངས']
    i = len(comm)-1
    to_avoid = True
    while i >= 1:
        llast = comm[i-1]['clean']
        last = comm[i]['clean']
        if 'match' in comm[i-1] and 'match' not in comm[i] and comm[i]['clean'] in ends:
            to_avoid = False
        elif 'match' in comm[i-1]:
            i -= 1
            while 'match' in comm[i] and to_avoid:
                llast = comm[i - 1]['clean']
                last = comm[i]['clean']
                del comm[i]['match']
                i -= 1
            to_avoid = True
        i -= 1

    # formatting for output
    out = []
    for c in comm:
        if 'match' in c and c['match'] == 'start':
            out.append('««')
            out.append(c['raw'])
        elif 'match' in c and c['match'] == 'end':
            out.append(c['raw'])
            out.append("»»")
        else:
            out.append(c['raw'])
    return ''.join(out)

