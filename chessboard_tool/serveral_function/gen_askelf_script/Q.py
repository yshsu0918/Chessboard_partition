f = open('elfinput.txt', 'r')


last = ''

count =0
for x in f.readlines():
    if 'genmove' in x:
        if x[8] != last[5]:
            count+=1
    last = x
f.close()