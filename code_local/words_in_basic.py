words = set()

from string import punctuation
for line in open('words_str.txt'):
    words = words | set(
                unicode.lower(word.strip(punctuation).decode('utf8'))
                for word in line.split()
                )

f = open('words_alphabetic.txt','w')
for w in sorted(words):
    print w
    f.write("%s\n" % w.encode('utf8'))
