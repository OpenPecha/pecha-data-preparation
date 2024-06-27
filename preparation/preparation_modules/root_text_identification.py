from botok import TokChunks, ChunkTokenizer


def parse_text(string):
    ignore_chars = ['༵', '༷', ]
    tc = TokChunks(string, ignore_chars=ignore_chars)
    tc.serve_syls_to_trie()

    syls = []
    for syl, idx in tc.chunks:
        if syl:
            c = ''.join([tc.bs.string[i] for i in syl])
        else:
            c = None
        r = tc.get_readable([idx])[0][1]
        syls.append({'clean': c, 'raw': r})
    return syls


def move_to_next_syl(idx, syls):
    while idx < len(syls):
        cur = syls[idx][0]
        if cur:
            syl = cur
            break
        else:
            idx += 1
    else:
        return idx, None
    return idx, syl


def identify_roottext_citations(root, comt):
    root_syls = parse_text(root)
    comt_syls = parse_text(comt)

    # mark all the syllable of the root text in the commentary, irrelevant of order or duplicates
    for num, r in enumerate(root_syls):
        cur_r_syl = r['clean']
        for i, c in enumerate(comt_syls):
            cur_c_syl = c['clean']
            if cur_c_syl and cur_c_syl == cur_r_syl:
                if 'r_idx' not in c:
                    c['r_idx'] = []
                c['r_idx'].append(num)

    # remove syllables that come before current index in root text
    r_indexes = [i for i, r in enumerate(root_syls) if r['clean']]
    r_idx = r_indexes.pop(0)
    cur_pos = {}  # roughly estimated value
    for num, c in enumerate(comt_syls):
        if num == 175:
            print()
        if 'r_idx' in c:
            c['r_idx'] = [i for i in c['r_idx'] if r_idx >= i]
            if not c['r_idx'] or (len(c['r_idx']) == 1 and c['r_idx'][0] in cur_pos and num >= cur_pos[c['r_idx'][0]]+20):
                c.pop('r_idx')
            if 'r_idx' in c and r_idx in c['r_idx']:
                if r_idx not in cur_pos:
                    cur_pos[r_idx] = num
                r_idx = r_indexes.pop(0)

    print()

    def preview(comt):
        out = []
        for c in comt:
            raw = c['raw']
            if 'r_idx' in c:
                raw = f'««{raw}»»'
            out.append(raw)

        return ''.join(out)

    return preview(comt_syls)
