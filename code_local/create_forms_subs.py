basic_form = set()
form = {}
ignore_set = set(['a','the','of'])

for line in open('form_in_basic_form.txt'):
    basic_form.add(line.strip().replace(';','').decode('utf8'))

for w in basic_form:
    print w

files = ['form_no.txt', 'form_one.txt', 'form_many.txt'] 

n_unproc = 0
lines_unproc = ''
for f in files:
    for line in open(f):
        words = line.split(';')
        if len(words) == 2:
            w = words[0].decode('utf8')
            bf = words[1].strip().decode('utf8')
            if not ',' in bf and bf:
                bf = bf.strip()
                form[w] = bf
            else:
                n_unproc += 1
                lines_unproc += line
        else:
            n_unproc += 1
            lines_unproc += line

print 'unprocessed lines: ', n_unproc
print lines_unproc

def to_basic_form(w):
    if w in basic_form:
        return w
    else:
        return form.get(w,'')

from string import punctuation
f = open('words_str.txt','w')
for line in open('text.txt'):
    line_words = sorted(
                    set(
                    map(
                        to_basic_form,
                        (unicode.lower(word.strip(punctuation).decode('utf8')) for word in line.split())
                        )
                    )
                    )
    print line[:-1]
    for w in line_words:
        if w in ignore_set:
            line_words.remove(w)
    words_str = ' '.join(line_words).strip().replace(' ','; ')
    print words_str
    print '-'*40

    f.write("%s\n" % words_str.encode('utf8'))
