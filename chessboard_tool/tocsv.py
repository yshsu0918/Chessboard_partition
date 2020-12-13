import os

#hyper
problem_path = './high171/high171'
result_path = './high171/result'

fnames = os.listdir(result_path)
sgfs = os.listdir(problem_path)


result_dirs = []
for x in fnames:
    if 'result' in x and '.' not in x:
        result_dirs.append( os.path.join(result_path,x) )

csv = open(os.path.join( result_path,'stat.csv' ), 'w')
firstline = 'sgf_filename'
for result in result_dirs:
    firstline += ',' + result.replace('\\','/')
firstline+='\n'

print(result_dirs)
print(sgfs)
content = ''
for sgf in sgfs: 
    if '.sgf' not in sgf:
        continue
    content += sgf  
    for result in result_dirs:
        print(result,sgf)
        if sgf in os.listdir( os.path.join( result , 'correct' ) ):
            content += ', 1' 
        else:
            content += ', 0'
    content+='\n'

csv.write(firstline + content)