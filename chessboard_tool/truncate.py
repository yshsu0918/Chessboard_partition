
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


def negative(color):
    if color == 'b':
        return 'w'
    return 'b'

if __name__ == '__main__':
    # sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/truncate_children/input')
    '''
import os
import sys
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/truncate_children/input')
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/truncate_children/output')
os.chdir('G:/VM_SYNC/chessboard_partition/切棋譜/truncate_children')
    '''
    if ( len(sys.argv) == 3 ):
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print('Usage: python3 ask_cgi.py [input_path] [output_path]')
        print('     : All of the *.sgf* in input_path will ask CGI for next move')
        print('Function: each sgf will be cover by correct mask.')
        sys.exit("Please enter correct command, goodbye!")

    sgfs = []

    for filename in os.listdir(input_path):
        if 'sgf' not in filename:
            continue
        sgfs.append( filename )

    for fname in sgfs:
        counter  = 0

        with open( os.path.join( sys.argv[1] ,fname ) , encoding='UTF-8') as f:
            print('#', counter , fname)
            sgf = f.read()
            clean_sgf, answer_step,color = masking(sgf)
            output_sgf( 'temp.sgf' , clean_sgf) #input for CGI
            #output_sgf( os.path.join( output_path, fname).replace('_mask_','_noans_'), clean_sgf )
            output_sgf( os.path.join( output_path, fname), clean_sgf )
            f.close()

