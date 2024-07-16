from collections import OrderedDict

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


def detect_root_text_syls(root, comt):
    root_syls = parse_text(root)
    root_syls_idx = [r for r, entry in enumerate(root_syls) if entry['clean']]
    comt_syls = parse_text(comt)

    # 0. mark all the syllable of the root text in the commentary, irrelevant of order or duplicates
    for num, r in enumerate(root_syls):
        cur_r_syl = r['clean']
        for i, c in enumerate(comt_syls):
            cur_c_syl = c['clean']
            if cur_c_syl and cur_c_syl == cur_r_syl:
                # add index in comt_syls. todo: check if this should be kept or not
                if 'r_idx' not in c:
                    c['r_idx'] = []
                c['r_idx'].append(num)

    # 1. mark first occurrence in text of each root text syllable. contains loads of false positive
    for root_idx in root_syls_idx:
        found = False
        for num, syl in enumerate(comt_syls):
            if syl['clean'] and 'r_idx' in syl:
                if root_idx in syl['r_idx'] and not found:
                    if 'first_occ' not in syl:
                        syl['first_occ'] = []
                    if not syl['first_occ']:  # ignore syllables where a first occurrence has already been found
                        syl['first_occ'].append(root_idx)
                        found = True

    firsts = []
    i = 0
    prev = None
    cur = None
    next = None
    initiated = False
    while i < len(comt_syls):
        syl = comt_syls[i]
        if 'first_occ' in syl:
            if not initiated:
                if not prev:
                    prev = syl['first_occ'][0]
                elif not cur:
                    cur = syl['first_occ'][0]
                elif not next:
                    next = syl['first_occ'][0]
                    initiated = True
            else:
                firsts.append((prev, cur, next))
                prev = cur
                cur = next
                next = syl['first_occ'][0]
        i += 1
    print('\n'.join([f'{p} {c} {n}' for p, c, n in firsts]))
    print()
    # 2. filtering false positives:

    # 2.a remove all the occurrences of next_syl_idx in span:  from next_syl_idx until cur_syl_idx+1
    #     secondary effect: removes 'first_occ' for some of the syllables.
    cur_first_occ_idx = 0
    cur_first_occ = root_syls_idx[cur_first_occ_idx]
    first_occ_deleted = []
    while cur_first_occ_idx+1 < len(root_syls_idx):
            next_first_occ = root_syls_idx[cur_first_occ_idx+1]

            cur_syl_idx = [i for i, c in enumerate(comt_syls) if 'first_occ' in c and c['first_occ'][0] == cur_first_occ]
            if cur_syl_idx:
                cur_syl_idx = cur_syl_idx[0]
            else:
                cur_first_occ_idx += 1
                continue

            next_syl_idx = [i for i, c in enumerate(comt_syls) if 'first_occ' in c and c['first_occ'][0] == next_first_occ]
            if next_syl_idx:
                next_syl_idx = next_syl_idx[0]
            else:
                cur_first_occ_idx += 1
                continue

            if next_syl_idx < cur_syl_idx:
                for idx in range(next_syl_idx, cur_syl_idx+1):
                    # actual deletion of false positives ###
                    if 'first_occ' in comt_syls[idx] and next_first_occ in comt_syls[idx]['first_occ']:
                        del comt_syls[idx]['first_occ']
                        first_occ_deleted.append(idx)
                    if 'r_idx' in comt_syls[idx] and next_first_occ in comt_syls[idx]['r_idx']:
                        comt_syls[idx]['r_idx'] = [i for i in comt_syls[idx]['r_idx'] if i != next_first_occ]
                    # ######################################
            cur_first_occ_idx += 1

    # 2.b find first occurrence for root syls in first_occ_deleted list. do not try to find their correct location.
    first_occ_deleted = sorted(first_occ_deleted)
    # this is a copy of code in section 1. with modifications on comments
    for root_idx in first_occ_deleted:  # changed from looping over `root_syls_idx`
        found = False
        for num, syl in enumerate(comt_syls):
            if syl['clean'] and 'r_idx' in syl:
                if root_idx in syl['r_idx'] and not found:
                    if 'first_occ' not in syl:
                        syl['first_occ'] = []
                    if not syl['first_occ']:
                        syl['first_occ'].append(root_idx)
                        found = True

    # 2.c flag all first_occ indices that are bigger than the next first_occ.
    #     remove first_occ and all subsequent occurrences

    # ################ initial values ###########################
    first_occ_seq = []

    cur_first_root_idx = 0
    for num, r_syl in enumerate(root_syls):
        if 'clean' in r_syl:
            cur_first_root_idx = num
            break

    cur_first_occ_syl = root_syls[cur_first_root_idx]['clean']
    cur_first_occ_idx = None
    for num, syl in enumerate(comt_syls):
        if 'first_occ' in syl and syl['clean'] == cur_first_occ_syl:
            cur_first_occ_idx = num
            break
    # ###########################################################

    next_first_occ_syl = None
    next_first_root_idx = None
    next_first_occ_idx = None
    on_hold_first_occs = []
    for num, syl in enumerate(comt_syls):
        if 'first_occ' in syl:
            next_first_root_idx = syl['first_occ'][0]
            next_first_occ_syl = root_syls[next_first_root_idx]['clean']
            next_first_occ_idx = num

            if next_first_occ_idx < cur_first_occ_idx:
                print()
                pass

    # 2.d chunk syls in intervals between first occurences and remove all indices that are bigger than the first_occ
    #     at the right boundary of the chunk

    # 2.e remove all occurrences that happen after the right boundary + a maximum value (between 20 and 100 syls)

    # 2.f remove all occurrences of particles except for first_occ

    # remove syllables that come before current index in root text
    # todo: flag particles and allow jumping over them to next syllable in root text
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
                raw = f'««{raw}{c["r_idx"]}»»'
            out.append(raw)

        return ''.join(out)

    return preview(comt_syls)
