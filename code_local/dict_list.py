import dictclient as d
c = d.Connection('dictd.xdsl.by')
dir(c)
l = c.getdbdescs()

for i in l:
    print i
    print l[i]
    print
