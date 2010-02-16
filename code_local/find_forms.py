# http://antoniocangiano.com/2008/03/18/use-python-to-detect-the-most-frequent-words-in-a-file/
from string import punctuation

N = 20
words = []

words_gen = (unicode.lower(word.strip(punctuation).decode('utf8')) for line in open("text.txt")
                                             for word in line.split())

for word in words_gen:
    if not word in words:
        words.append(word)

words.sort()

import pymorphy
morph = pymorphy.get_shelve_morph('en')
#morph = pymorphy.get_shelve_morph('ru')

import os,stat,time,shutil

def make_backup(file_name):
    time_last = float(open('time_find_forms.txt').readline())
    timestamp = time.strftime('%Y%m%d%H%M%S')
    time_modified = os.stat(file_name)[stat.ST_MTIME]
    if abs( time_modified - time_last ) > 5:
        shutil.copyfile(file_name, 'backup/'+file_name+'_'+timestamp)

files = ['form_in_basic_form.txt', 'form_no.txt',
         'form_one.txt','form_many.txt'] 

for f in files:
    make_backup(f)

f_basic = open('form_in_basic_form.txt','w')
f_no = open('form_no.txt','w')
f_one = open('form_one.txt','w')
f_many = open('form_many.txt','w')

n_basic = 0
n_no = 0
n_one = 0
n_many = 0

for word in words:
    forms = morph.normalize(word.upper())
    if len(forms) == 1:
        form = forms.pop().lower()
        if word == form:
            f_basic.write("%s;\n" % word.encode('utf8'))
            n_basic += 1
        else:
            f_one.write("%s; %s\n" % (word.encode('utf8'), form.encode('utf8')))
            n_one += 1
    elif len(forms) == 0:
        f_no.write("%s;\n" % word.encode('utf8'))
        n_no += 1
    else:
        f_many.write("%s; %s\n" % (word.encode('utf8'), ', '.join(forms).lower().encode('utf8')))
        n_many += 1

print 'in basic form: ',n_basic
print 'no form: ',n_no
print 'one form',n_one
print 'many forms',n_many

f_time = open('time_find_forms.txt','w')
f_time.write(str(time.time()))

#    print word, ' '.join(morph.normalize(word.upper()))
#f = open('out.txt','w')
#for word, frequency in sorted_words:
#    f.write("%s: %d\n" % (word.encode('utf8'), frequency))
