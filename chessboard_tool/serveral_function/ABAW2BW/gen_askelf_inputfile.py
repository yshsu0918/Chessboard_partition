
# Run on docker elf

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

    result_sgf += ')'
    
    color = 'b'
    if 'WHITE' in sgf:
        color = 'w'
    
    return result_sgf, color, AB, AW

def output_sgf(fname, sgf):
    with open(fname , 'w', encoding='UTF-8') as f:
        f.write(sgf)
        f.close()

def negative(color):
    if color == 'b':
        return 'w'
    return 'b'



sgf_eng = 'abcdefghijklmnopqrs'
sgf_dict = dict()
elf_eng = 'abcdefghjklmnopqrst' # no i
elf_dict = dict()
for i in range(len(elf_eng)):
    sgf_dict[sgf_eng[i]] = i
    elf_dict[elf_eng[i]] = i

def translate_coor_sgf2elf(s):
    # alphabet alphabet => alphabet number
    A = elf_eng[ sgf_dict[s[0].lower()] ]
    B = str(sgf_dict[s[1].lower()] +1)
    return A+B

def loadsgf(input_path = None):
    f = open( input_path, encoding='UTF-8')
    sgf = f.read()
    f.close()
    clean_sgf,color,AB,AW = masking(sgf)
    
    seq_AB = []
    seq_AW = []
    for x in AB:
        seq_AB.append( 'B[' + x + '];' )
    for x in AW:
        seq_AW.append( 'W[' + x + '];' )
    
    if len(AB)>len(AW):
        seq_AW.extend(['W[];'] * (len(AB) - len(AW)))
    else:
        seq_AB.extend(['B[];'] * (len(AW) - len(AB)))
    seq =[]
    for i in range(len(seq_AB)):
        seq.append( seq_AB[i] )
        seq.append( seq_AW[i] )
    
    if ( color == 'w'):
        if 'pass' in seq[-1]:
            del seq[-1]
        else:
            seq.append('B[];')
        seq[-1] = seq[-1][:-1]
        seq.append('C[TO_LIVE;WHITE]')
    else:
        seq[-1] = seq[-1][:-1]
        seq.append('C[TO_LIVE;BLACK]')
    
    return clean_sgf,seq

if __name__ == '__main__':
    '''
import os
import sys
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/ABAW2BW/input')
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/ABAW2BW/output')
os.chdir('G:/VM_SYNC/chessboard_partition/切棋譜/ABAW2BW')
    '''     

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    sgfs = []

    for filename in os.listdir(input_path):
        if 'sgf' not in filename:
            continue
        sgfs.append( filename )
    

    
    for fname in sgfs:
        outfile_content = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'
        print(fname)
        cleansgf,seq = loadsgf(os.path.join( input_path ,fname ))
        for x in seq:
            outfile_content += x
        outfile_content += ')'
        print(outfile_content)
        output_sgf(os.path.join(output_path, fname), outfile_content)
        