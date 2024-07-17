from tempfile import NamedTemporaryFile

import colibricore

# A. find trigrams
root_prepped = ''
root_file = NamedTemporaryFile()
root_class_file = NamedTemporaryFile()
root_corpus_file = NamedTemporaryFile()

# write root text file
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
