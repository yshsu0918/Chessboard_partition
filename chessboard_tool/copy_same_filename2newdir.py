import os
from shutil import copyfile



pathB = './TOMH736/TOMH736_tolive'
pathA = './TOMH736/result/cgi0_TOMH736_automask_bound2/wrong'
pathC = './TOMH736/TOMH736_tolive_automask_wrong'
A = os.listdir(pathA)
B = os.listdir(pathB)

if not os.path.isdir(pathC):
    os.mkdir(pathC)

for a in A:
    for b in B:
        if a == b:
            print (a,b)
            src = os.path.join(pathA, a)
            dst = os.path.join(pathC, a)
            copyfile(src, dst)
            break