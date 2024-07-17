from .root_text_syllable_detection import parse_text


def detect_root_text_citations(root_text, commentary, citation_ends=None):
    """
    A. Generates trigrams from the root text,
    B. tags all occurences of trigrams in commentary and
    C. discard all matches that don't have a trailing citation end.

    note: arbitrarily chose trigrams as minimal unit.
    :param citation_ends:
    :param root_text:
    :param commentary:
    :return:
    """
    if citation_ends is None:
        citation_ends = ['ཅེས', 'ཤེས', 'ཞེས', 'སོགས', 'གསུངས']

    def gen_syl_separated_text(in_file):
        text = parse_text(in_file.read_text())
        syls = [r['clean'] for r in text if r['clean']]  # avoid all punctuation to get maximum of matches
        return syls

    root_prepped = gen_syl_separated_text(root_text)
    trigrams = []
    for i in range(0, len(root_prepped)-2):
        tri = [root_prepped[r] for r in range(i, i+3)]
        trigrams.append(tri)

    # B. Tag all occurences in commentary
    comm = parse_text(commentary.read_text())
    for tri in trigrams:
        for i in range(0, len(comm)-3):
            cur_window = [comm[n]['clean'] for n in range(i, i+3)]
            if tri == cur_window:
                for n in range(i, i+3):
                    comm[n]['match'] = True

    # C. find matches ending with citation end (loops backwards from the end to the beginning)
    start_found = None
    end_found = None
    for i, syl in enumerate(comm):
        # avoid beginning and end of file
        if 0 == i or i >= len(comm)-1:
            continue

        prev = comm[i-1]
        next = comm[i+1]

        # search for beginning and end of root text citation
        if not start_found and 'match' not in prev and 'match' in syl:
            start_found = i
        if not end_found and 'match' in prev and 'match' not in syl:
            end_found = i

        # when beginning and end are found, but the citation is not followed by citation marker, dismiss citation match
        # note: if there is punct, citation marker should be found in next syllable
        if start_found and end_found:
            if syl['clean'] in citation_ends or (not syl['clean'] and next['clean'] in citation_ends):
                start_found = None
                end_found = None
            else:
                for n in range(start_found, end_found):
                    del comm[n]['match']
                start_found = None
                end_found = None

    # find beginning and ends of matches
    for i in range(0, len(comm)-2):
        if 'match' not in comm[i] and 'match' in comm[i+1]:
            comm[i+1]['match'] = 'start'
        if 'match' in comm[i] and 'match' not in comm[i+1]:
            if not comm[i+1]['clean']:  # to include punctuation within citation
                comm[i+1]['match'] = True
            else:
                comm[i]['match'] = 'end'

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

