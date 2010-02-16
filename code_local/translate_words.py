# -*- coding: utf8 -*-
import dictclient #John Goerzen's GPL'd dictclient.py

class RuDict:
    def __init__(self):
        self.conn = dictclient.Connection('dictd.xdsl.by')
    def get_translation_all(self,word):
        # defs = self.conn.define('slovnyk_ru-en',word.encode('utf8'))
        defs = self.conn.define('ru-en',word.encode('utf8'))
        translation = ''
        ld = len(defs)
        print 'definitions: ',ld
        if ld > 0:
            for d in defs:
                ws = d.getdefstr().split('\n')
                for w in ws[1:]:
                    word = unicode(w,'utf8')
                    word = unicode.lower(word)
                    word = word.replace('"','')
                    translation += word + ', '
                translation = translation[:-2] + '; '
            return translation[:-2].encode('utf8')
        else:
            return ''

ft = open('words_translation.txt','r')
words_translated = {}
# read words that are already translated
for l in ft:
    p = l.find(';')
    if p > 0:
        w = l[:p].strip().decode('utf')
        d = l[p+1:].strip().decode('utf')
        if w and not d == 'None':
            words_translated[w] = d
ft.close()

print 'words already translated:', len(words_translated)

fw = open('words_alphabetic.txt','r')
d = RuDict()
w_counter = 0
w_none = 0

for l in fw:
    w_counter += 1
    print 'word: ', w_counter

    w = l.split()[0].decode('utf')

    if w in words_translated:
        print 'already translated'
    else:
        t = d.get_translation_all(w)
        if t=='':
            w_none += 1
            words_translated[w] = 'None'
        else:
            words_translated[w] = t

fw.close()    

ft = open('words_translation.txt','w')
for w in sorted(words_translated):
    ft.write(w.encode('utf8')+'; ')
    ft.write(words_translated[w])
    ft.write('\n')
ft.close()    

print '\n'
print 'words : ', w_counter
print 'no def: ', w_none
