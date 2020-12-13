import os

path = './high171/high171'
QQ = os.listdir(path)

for x in QQ:
    filepath1 = os.path.join(path,x)
    if '.sgf' in x:
        newfilename = "%03d"%int(x.replace('.sgf',''))+'.sgf'
        filepath2 = os.path.join(path,newfilename)
        os.rename(filepath1,filepath2)
    else:
        print('not exist', x)