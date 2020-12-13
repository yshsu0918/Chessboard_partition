
# run on CGI QQQ

import os
import re
import sys
import statistics
import sys
from os import walk
from os.path import join

def parse_ABW(s):
    AB = re.search('AB(\[..\])*', s).group(0)
    AW = re.search('AW(\[..\])*', s).group(0)
    AB = [ x[1:3] for x in re.findall('\[..\]', AB) ]
    AW = [ x[1:3] for x in re.findall('\[..\]', AW) ]
    return AB, AW
    
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


    AB, AW = parse_ABW(sgf)

    result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'
    result_sgf += 'AB'
    for x in AB:
        result_sgf += '[' + x + ']'

    result_sgf += 'AW'
    for x in AW:
        result_sgf += '[' + x + ']'




    answer_step,color = find_first_step(sgf)

    #result_sgf += '(;' + color.upper() + '[aa]))' #this is dirty QQ
    result_sgf += ')'

    #print( result_sgf)
    return result_sgf, answer_step, color


def output_sgf(fname, sgf):
    with open(fname , 'w', encoding='UTF-8') as f:
        f.write(sgf)
        f.close()
def translate_CGI_coor(s):
    print('@translate_CGI_coor:', s, type(s))
    x = s[0].lower()
    if(x > 'l'):
        x = alphabet [ alpha_dict[x] - 1 ]

    y = s[1:]
    index = 19 - int(y) + 2
    Q = x+alphabet[index]
    return Q.lower()
def branch_str(color,coor,comment=None):
    if comment == None:
        return '(;' +  color + '[' + coor +']'+ ')'
    else:
        print('(;' +  color + '[' + coor +']'+ 'C[' + comment +']' + ')')
        return '(;' +  color + '[' + coor +']'+ 'C[' + comment +']' + ')'


alphabet = '!@abcdefghijklmnopqrstuvwxyz#$'
alpha_dict = dict()
for i in range(len(alphabet)):
    alpha_dict[alphabet[i]] = i


def select_mask(s):
    #calculate distance to tian-yuan
    def distance2center(coor):
        return (alpha_dict['j'] - alpha_dict[coor[0]] )**2 + (alpha_dict['j'] - alpha_dict[coor[1]] )**2
        
    try:
        Bindex = re.search('[^A]B(\[..\])+', s).span()
        Windex = re.search('[^A]W(\[..\])+', s).span()
        who_first = 'W'
        if Bindex[0] < Windex[0]:
            who_first = 'B'
    
    except:
        Bindex = re.search('[^A]B(\[..\])+', s)
        Windex = re.search('[^A]W(\[..\])+', s)
        who_first = 'W'
        if Windex == None:
            who_first = 'B'
    
    B,W = parse_ABW(s)


    distances = []
    for coor in B:
        distances.append( (distance2center(coor) , 'b', coor))
    for coor in W:
        distances.append( (distance2center(coor) , 'w', coor))
    distances.sort()
    who_outside = distances[0][1]
    #print('who_outside', who_outside, 'who_first', who_first)
    return who_outside



def negative(color):
    if color == 'b':
        return 'w'
    return 'b'

if __name__ == '__main__':
    
    good_sgf_path = 'G:/VM_SYNC/chessboard_partition/切棋譜/distinguish_livedeathsgf/chao232'
    nomask_sgf_path = 'G:/VM_SYNC/chessboard_partition/切棋譜/distinguish_livedeathsgf/chao232_noans'
    output_path = 'G:/VM_SYNC/chessboard_partition/切棋譜/distinguish_livedeathsgf/liveordeath'
    
    live_first_content = ''
    death_first_content = ''
    live_first_f = open( os.path.join(output_path+'/tolive', 'live_first.txt') , 'w')
    death_first_f = open( os.path.join(output_path+'/todeath', 'death_first.txt') , 'w')
    
    sgfs = []

    for filename in os.listdir(nomask_sgf_path):
        if 'sgf' not in filename:
            continue
        sgfs.append( filename )
        
    
    print(sgfs)
    
    for fname in sgfs:
        counter  = 0

        good_f = open( os.path.join( good_sgf_path ,fname ) , encoding='UTF-8')
        good_sgf = good_f.read()

        nomask_f = open( os.path.join( nomask_sgf_path ,fname ) , encoding='UTF-8')
        nomask_sgf = nomask_f.read()
        
        clean_sgf, answer_step,color = masking(good_sgf)
        who_outside = select_mask(nomask_sgf)
        print(nomask_sgf)
        output_sgf( 'temp.sgf' , clean_sgf) #input for CGI
        
        print(fname, color ,who_outside)
        if color != who_outside:
            output_sgf( os.path.join(output_path+'/tolive', fname) , nomask_sgf)
            output_sgf( os.path.join(output_path+'/tolive_ans', fname), good_sgf)
            live_first_content += fname + ' ' + color + '\n'
        else:
            output_sgf( os.path.join(output_path+'/todeath', fname) , nomask_sgf)
            output_sgf( os.path.join(output_path+'/todeath_ans', fname), good_sgf)
            death_first_content += fname + ' ' + color + '\n'
            
        good_f.close()
        nomask_f.close()
    live_first_f.write(live_first_content)
    death_first_f.write(death_first_content)
    live_first_f.close()
    death_first_f.close()

