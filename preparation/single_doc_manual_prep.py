import copy
import re
from pathlib import Path

from docx import Document  # package name: python-docx

from .constants import *


def adjust_punct(segments):
    prev_run = None
    for line in segments:
        for par in line:
            for run in par.runs:
                if prev_run and run.text.strip():
                    punct = ''
                    while run.text and run.text[0] in PUNCT:
                        punct += run.text[0]
                        run.text = run.text[1:]
                    prev_run.text += punct

                prev_run = run


def find_segments(doc):
    segments = []
    cur_seg = []
    for line in doc.paragraphs:
        if not line.text:
            if cur_seg:
                segments.append(cur_seg)
                cur_seg = []
        else:
            cur_seg.append(line)
    if cur_seg:
        segments.append(cur_seg)
    return segments


def find_bckgd(run):
    regex = ' w\:fill\=\"([^\"]+)\" '
    xml = str(run._element.xml)
    found = re.findall(regex, xml)
    if found:
        found = found[0]
    else:
        found = None
    return found


def find_attrs(segs):
    with_attrs = []
    for seg in segs:
        cur = []
        state = {i: None for i in [ITALIC, COLOR, BOLD]}
        for num, par in enumerate(seg):
            for run in par.runs:
                italic = run.font.italic
                color = run.font.color.rgb  # hex color string
                if color:
                    color = str(color)
                bold = run.font.bold
                bckg = find_bckgd(run)
                if cur and state[ITALIC] == italic and state[COLOR] == color and state[BOLD] == bold:
                    cur[-1][TEXT] += run.text
                else:
                    cur.append({TEXT: run.text, ITALIC: italic, COLOR: color, BOLD: bold})

                if bckg:
                    if BACKGD in cur[-1].keys():
                        cur[-1][BACKGD] = cur[-1][BACKGD] + ' ' + str(bckg)
                    else:
                        cur[-1][BACKGD] = str(bckg)

                state[ITALIC], state[COLOR], state[BOLD] = italic, color, bold

            if num <= len(seg)-2:
                cur[-1][TEXT] += '\n'

        with_attrs.append(cur)
    return with_attrs


def find_types(with_attrs):
    for num, seg in enumerate(with_attrs):
        for run in seg:
            if not run[COLOR]:
                # bold + italic -> verses
                if run[ITALIC] and run[BOLD]:
                    run[ANN] = VERSE
                # bold -> root syllables
                elif not run[ITALIC] and run[BOLD]:
                    run[ANN] = ROOT_SYL
                # no bold + italic -> title
                elif run[ITALIC] and not run[BOLD] and not run[COLOR]:
                    run[ANN] = TITLE
            elif run[COLOR]:
                c = run[COLOR]
                if c == colors[SAPCHE]:
                    run[ANN] = SAPCHE
                elif c == colors[ROOT_BIGEND]:
                    run[ANN] = ROOT_BIGEND
                elif c == colors[ROOT_BODY]:
                    run[ANN] = ROOT_BODY
                elif c == colors[CIT_BIGEND]:
                    run[ANN] = CIT_BIGEND
                elif c == colors[CIT_BODY]:
                    run[ANN] = CIT_BODY
                else:
                    print(run, 'has unexpected color:', c)
    # identify citation beginnings and ends
    for seg in with_attrs:
        for num, run in enumerate(seg):
            if ANN in run and run[ANN] == ROOT_BIGEND:
                if num >= 1 and ANN in seg[num - 1]:
                    if seg[num-1][ANN] == ROOT_BODY:
                        run[ANN] = ROOT_END
                    else:
                        print('something is wrong with current annotation', run)
                elif len(seg) > num+1 and ANN in seg[num + 1]:
                    if seg[num+1][ANN] == ROOT_BODY:
                        run[ANN] = ROOT_ORIG
                    else:
                        print('something is wrong with current annotation', run)
                elif len(seg) > num+2 and ANN in seg[num + 2]:
                    if seg[num+2][ANN] == ROOT_BODY:
                        run[ANN] = ROOT_ORIG
                    else:
                        print('something is wrong with current annotation', run)
                else:
                    print('something is wrong with current annotation', run)
            elif ANN in run and run[ANN] == CIT_BIGEND:
                if num >= 1 and ANN in seg[num - 1]:
                    if seg[num-1][ANN] == CIT_BODY:
                        run[ANN] = CIT_END
                    else:
                        print('something is wrong with current annotation', run)
                elif len(seg) > num+1 and ANN in seg[num + 1]:
                    if seg[num+1][ANN] == CIT_BODY:
                        run[ANN] = CIT_ORIG
                    else:
                        print('something is wrong with current annotation', run)
                elif len(seg) > num+2 and ANN in seg[num + 2]:
                    if seg[num+2][ANN] == CIT_BODY:
                        run[ANN] = CIT_ORIG
                    else:
                        print('something is wrong with current annotation', run)
                else:
                    print('something is wrong with current annotation', run)


def split_root_nums(line):
    l = copy.deepcopy(line)
    num = ''
    while l and l[0] in NUMS:
        num += l[0]
        l = l[1:]
    return num, l


def expand_root_number(num):
    total = []
    num = re.sub('\s', '', num)
    num = num.split(',')
    for n in num:
        if '-' in n:
            begin, end = n.split('-')
            begin, end = int(begin), int(end)
            span = list(range(begin, end+1))
            total.extend(span)
        else:
            total.append(int(n))
    return total


def parse_root_numbers(with_attrs):
    for seg in with_attrs:
        for run in seg:
            num, l = split_root_nums(run[TEXT])
            if l and num.strip():
                run[TEXT] = l
                run[ROOT_NUM] = expand_root_number(num)


def del_empty_runs(with_attrs):
    # remove empty runs
    for seg in with_attrs:
        to_del = []
        for num, line in enumerate(seg):
            if not line[TEXT].strip():
                to_del.append(num)
        for d in sorted(to_del, reverse=True):
            del seg[d]


def join_lone_root_numbers(with_attrs):
    for j, seg in enumerate(with_attrs):
        to_merge_with_next = []
        for n, line in enumerate(seg):
            is_lone_num = True
            i = 0
            while i < len(line[TEXT]):
                if line[TEXT][i] not in NUMS:
                    is_lone_num = False
                    break
                i += 1
            if is_lone_num:
                to_merge_with_next.append(n)

        if to_merge_with_next:
            for t in sorted(to_merge_with_next, reverse=True):
                seg[t+1][TEXT] = seg[t][TEXT] + seg[t+1][TEXT]
                del seg[t]


def format_output(with_attrs):
    with_tags = [TITLE, SAPCHE, VERSE, CIT_ORIG, CIT_BODY, CIT_END, ROOT_ORIG, ROOT_BODY, ROOT_END, ROOT_SYL]

    out = []
    for seg in with_attrs:
        cur = []
        root_nums = None
        for line in seg:
            if ROOT_NUM in line:
                root_nums = line[ROOT_NUM]
            if ANN in line:
                ann = line[ANN]
                for a in with_tags:
                    if ann == a:
                        c = f'<{a}>{line[TEXT]}</{a}>'
                        cur.append(c)
            else:
                cur.append(line[TEXT])
        cur = ''.join(cur)
        if root_nums:
            o = f'<segment root_text_nums:{root_nums}>{cur}</segment>'
        else:
            o = f'<segment>{cur}</segment>'
        out.append(o.replace('\n', '\\n'))  # so that \n remains two chars in the output

    out = '\n'.join(out)
    return out


def parse_doc(in_file):
    doc = Document(in_file)

    segments = find_segments(doc)

    # tsek or shad that are wrongly marked will be brought back to the syllables they belong to
    adjust_punct(segments)

    with_attrs = find_attrs(segments)

    # delete empty runs left from adjusting punct
    del_empty_runs(with_attrs)

    find_types(with_attrs)

    join_lone_root_numbers(with_attrs)
    parse_root_numbers(with_attrs)

    # TODO: make use of background colors

    out = format_output(with_attrs)

    out_file = Path(in_file).parent / (Path(in_file).stem + '_parsed.txt')
    out_file.write_text(out)
    print()

