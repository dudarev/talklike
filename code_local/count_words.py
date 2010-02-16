# http://antoniocangiano.com/2008/03/18/use-python-to-detect-the-most-frequent-words-in-a-file/
from string import punctuation

N = 20
words = {}

words_gen = (unicode.lower(word.strip(punctuation).decode('utf8')) for line in open("text.txt")
                                             for word in line.split())

for word in words_gen:
    words[word] = words.get(word, 0) + 1

top_words = sorted(words.iteritems(),
                   key=lambda(word, count): (-count, word))[:N] 

sorted_words = sorted(words.iteritems(),
                   key=lambda(word, count): (-count, word))

f = open('out.txt','w')
for word, frequency in sorted_words:
    f.write("%s: %d\n" % (word.encode('utf8'), frequency))
