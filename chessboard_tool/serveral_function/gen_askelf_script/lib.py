
# run on CGI QQQ

import os
import re
import sys
import statistics
import sys
from os import walk
from os.path import join

def masking(sgf):
    '''
    abs( middle - avgx) > abs (middle - avgy)
    '''
    def find_first_step(sgf):

        Bindex = re.search('[^A]B\[', sgf).span()[0]
        Windex = re.search('[^A]W\[', sgf).span()[0]

        if Bindex < Windex:
            return sgf[ Bindex+3 : Bindex+5] , 'b'
        else:
            return sgf[ Windex+3 : Windex+5] , 'w'

    def parse_ABW(s):
        AB = re.search('AB(\[..\])*', s).group(0)
        AW = re.search('AW(\[..\])*', s).group(0)
        AB = [ x[1:3] for x in re.findall('\[..\]', AB) ]
        AW = [ x[1:3] for x in re.findall('\[..\]', AW) ]
        return AB, AW

    AB, AW = parse_ABW(sgf)
    

    result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'
    result_sgf += 'AB'
    for x in AB:
        result_sgf += '[' + x + ']'

    result_sgf += 'AW'
    for x in AW:
        result_sgf += '[' + x + ']'

    answer_step,color = find_first_step(sgf)
    result_sgf += ')'

    print( result_sgf)
    return result_sgf, answer_step, color, AB, AW


def output_sgf(fname, sgf):
    with open(fname , 'w', encoding='UTF-8') as f:
        f.write(sgf)
        f.close()



alphabet = '!@abcdefghijklmnopqrstuvwxyz#$'
alpha_dict = dict()
for i in range(len(alphabet)):
    alpha_dict[alphabet[i]] = i

def translate_CGI_coor(s):
    # alphabet number => alphabet alphabet
    print('@translate_CGI_coor:', s, type(s))
    x = s[0].lower()
    if(x > 'l'):
        x = alphabet [ alpha_dict[x] - 1 ]
    y = s[1:]
    index = 19 - int(y) + 2
    Q = x+alphabet[index]
    return Q.lower()


