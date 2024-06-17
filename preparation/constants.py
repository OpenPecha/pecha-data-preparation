PUNCT = [
    '།',  # shad
    '་',  # tsek
    '༌',  # non-breaking tsek
    '༎',  # nyishad
    '༏',  # tsek shad
    '༐',  # nyi tsek shad
    '༑',  # rinchen pungshad
    '༔',  # ter shad
    ' ',  # space
    ' ',  # longer space used in Tibetan texts
]

# chars constituting root text numbers
NUMS = [str(i) for i in range(10)] + [' ', ' ', ',', '-']

# Attributes
BACKGD = 'background'
ITALIC = 'italic'
COLOR = 'color'
TEXT = 'text'
BOLD = 'bold'

# Annotations
ANN = 'annotation'
TITLE = 'title'
# citations
CIT_ORIG = 'citation_origin'
CIT_BODY = 'citation_body'
CIT_END = 'citation_end'
CIT_BIGEND = 'citation_begin_end'
# sapche
SAPCHE = 'sapche'
# root text
ROOT_ORIG = 'root_text_origin'
ROOT_BODY = 'root_text_body'
ROOT_END = 'root_text_end'
ROOT_BIGEND = 'root_text_begin_end'
ROOT_SYL = 'root_text_syls'
ROOT_NUM = 'root_text_nums'
# verses
VERSE = 'verse'

colors = {
    SAPCHE: 'FF00FF',
    ROOT_BIGEND: '00FF00',
    ROOT_BODY: '980000',
    CIT_BIGEND: '00FFFF',
    CIT_BODY: 'FF9900',
}
