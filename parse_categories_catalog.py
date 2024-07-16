from preparation import DriveManager

dm = DriveManager()
catalog = dm.download_n_parse_catalog()
print(catalog)

# Output Example:

# {
#   'ཁ་འདོན།': {
#       'ཁ་འདོན།data': {
#           'cat_name': {'bo': 'ཁ་འདོན།', 'en': 'Recitations'},
#           'long_desc': {'bo': 'ཆོ་ག་དང་འདོན་ཆ།', 'en': 'Prayers and Liturgies'},
#           'short_desc': {'bo': '', 'en': ''},
#           'works': []
#           },
#       'སྨོན་ལམ།': {
#           'སྨོན་ལམ།data': {
#               'cat_name': {'bo': 'སྨོན་ལམ།', 'en': 'Prayers'},
#               'long_desc': {'bo': 'སྨོན་ལམ་གྱི་རིགས།', 'en': 'All kinds of prayers'},
#               'short_desc': {'bo': '', 'en': ''},
#               'works': [('ཀུན་བཟང་སྨོན་ལམ།', 'edd993a2fa2144aa899ab1d0dc8f1de7')]
#               }
#           }
#       },
#   'གཞུང་།': {
#       'གཞུང་།data': {
#           'cat_name': {'bo': 'གཞུང་།', 'en': 'Treatises'},
#           'long_desc': {'bo': '', 'en': ''},
#           'short_desc': {'bo': '', 'en': ''},
#           'works': [('སྐྱབས་སེམས་འགྲེལ་པ།', 'a392ab847ea342ab8828baf6a6cdd654')]
#           },
#       'ཤེས་བྱ་ཀུན་བཏུས་ཀྱི་གཞུང་།': {
#           'ཤེས་བྱ་ཀུན་བཏུས་ཀྱི་གཞུང་།data': {
#               'cat_name': {'bo': 'ཤེས་བྱ་ཀུན་བཏུས་ཀྱི་གཞུང་།', 'en': 'Encyclopedic Works'},
#               'long_desc': {'bo': '', 'en': ''},
#               'short_desc': {'bo': '', 'en': ''},
#               'works': []
#               }
#           }
#       },
#   'དབུ་མ།': {
#       'དབུ་མ།data': {
#       'cat_name': {'bo': 'དབུ་མ།', 'en': 'Madhyamika'},
#       'long_desc': {'bo': 'དབུ་མའི་གཞུང་།', 'en': 'Middle Way Treatises'},
#       'short_desc': {'bo': '', 'en': ''},
#       'works': []
#       }
#    }
# }
