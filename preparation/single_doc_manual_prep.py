import re
from pathlib import Path

from docx import Document  # package name: python-docx


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
        state = {i: None for i in ['italic', 'color', 'bold']}
        for num, par in enumerate(seg):
            for run in par.runs:
                italic = run.font.italic
                color = run.font.color.rgb  # hex color string
                if color:
                    color = str(color)
                bold = run.font.bold
                bckg = find_bckgd(run)
                if cur and state['italic'] == italic and state['color'] == color and state['bold'] == bold:
                    cur[-1]['text'] += run.text
                else:
                    cur.append({'text': run.text, 'italic': italic, 'color': color, 'bold': bold})

                if bckg:
                    if 'background' in state.keys():
                        cur[-1]['background'] = cur[-1]['background'] + ' ' + str(bckg)
                    else:
                        cur[-1]['background'] = str(bckg)

                state['italic'], state['color'], state['bold'] = italic, color, bold

            if num <= len(seg)-2:
                cur[-1]['text'] += '\n'

        with_attrs.append(cur)
    return with_attrs


def parse_doc(in_file):
    doc = Document(in_file)

    segments = find_segments(doc)

    with_attrs = find_attrs(segments)

    print()
