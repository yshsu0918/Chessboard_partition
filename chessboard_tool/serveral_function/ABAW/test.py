# run on CGI

import os
import re
import sys
import statistics
from os import walk
from os.path import join

def masking(sgf):
    '''
    abs( middle - avgx) > abs (middle - avgy)
    '''
    def find_first_step(sgf):
        former = sgf.find('B[') if sgf.find('B[') < sgf.find('W[') else sgf.find('W[')
        #print ( 'ans', sgf[ former+2 : former + 4] )
        return sgf[ former+2 : former + 4]

    def parse_ABW(s):
        AB = re.search('AB(\[..\])*', s).group(0)
        AW = re.search('AW(\[..\])*', s).group(0)
        AB = [ x[1:3] for x in re.findall('\[..\]', AB) ]
        AW = [ x[1:3] for x in re.findall('\[..\]', AW) ]
        return AB, AW

    AB, AW = parse_ABW(sgf)
    ABW = AB
    ABW.extend(AW)

    #sgf = sgf [0: sgf.find('AB')+2 ] + AB[2:] + sgf [sgf.find('AB')+2: ]
    #sgf = sgf [0: sgf.find('AW')+2 ] + AW[2:] + sgf [sgf.find('AW')+2: ]

    former_index =  sgf.find('AB') if sgf.find('AB') < sgf.find('AW') else sgf.find('AW')
    color = 'B' if former_index == sgf.find('AB') else 'W'

    result_sgf = sgf[ 0 : former_index ]
    result_sgf += 'AB'
    for x in AB:
        result_sgf += '[' + x + ']'
    result_sgf += 'AW'
    for x in AW:
        result_sgf += '[' + x + ']'
    result_sgf += ')'

    answer_step = find_first_step(sgf)
    return result_sgf, answer_step, color

def output_sgf(fname, sgf):
    with open(fname , 'w', encoding='UTF-8') as f:
        f.write(sgf)
        f.close()

if __name__ == '__main__':
    #path = '/media/sf_VM_sync/chessboard_partition/切棋譜/sgf00045'
    path = './QQ/input/sgf00045'

    alphabet = '!@abcdefghijklmnopqrstuvwxyz#$'
    alpha_dict = dict()
    for i in range(len(alphabet)):
        alpha_dict[alphabet[i]] = i

    sgfs = []
    for root, dirs, files in walk(path):
        for f in files:
            if 'sgf' not in f:
                continue
            fullpath = join(root, f)
            sgfs.append(fullpath.replace('\\','/'))

    #four_corner = './03《圍棋死活辭典》-- 趙治勳/《圍棋死活辭典》下冊-- 趙治勳/00061__Vs_.sgf'
    #branch_two = './03《圍棋死活辭典》-- 趙治勳/趙治勳－圍棋死活辭典（上冊）/第3部 死活之應用/第2章 各種侵入手法/08.sgf'

    print(sgfs)

    for fname in sgfs:
        counter  = 0
        print(fname)
        with open(fname,encoding='UTF-8') as f:
            print(fname)
            sgf = f.read()
            sgf, answer_step,color = masking(sgf)
            output_sgf( 'temp.sgf' , sgf)
            os.system('sh ./mmm.sh temp.sgf')
            CGI_result = ''
            with open('myresult', 'r') as f:
                r = f.readlines()
                CGI_result = r[2][2:].replace('\n','')
                f.close()

            def translate_CGI_coor(s):
                x = s[0]
                y = s[1:]
                index = 19 - int(y) + 2
                return x+alphabet[index]

            with open('./QQ/output/log.txt', 'a+') as mylog:
                mylog.write('Correct answer'+answer_step+'CGI answer'+translate_CGI_coor(CGI_result)+ str(CGI_result) )
                mylog.close()

            def branch_str(color,coor):
                return '(;' +  color + '[' + coor +']'+')'


            output_sgf( './QQ/output/'+str(counter)+'cmp', sgf[0:-1]+branch_str(color,answer_step)+branch_str(color,CGI_result)+ ')' )
            counter += 1
            f.close()
