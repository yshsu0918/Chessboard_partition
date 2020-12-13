
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

    #print( result_sgf)
    return result_sgf, answer_step, color, AB, AW

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
    clean_sgf, answer_step,color,AB,AW = masking(sgf)
    
    seq_AB = []
    seq_AW = []
    for x in AB:
        seq_AB.append( "play b " + translate_coor_sgf2elf(x) )
    for x in AW:
        seq_AW.append( "play w " + translate_coor_sgf2elf(x) )
    
    if len(AB)>len(AW):
        seq_AW.extend(['play w pass'] * (len(AB) - len(AW)))
    else:
        seq_AB.extend(['play b pass'] * (len(AW) - len(AB)))
    seq =[]
    for i in range(len(seq_AB)):
        seq.append( seq_AB[i] )
        seq.append( seq_AW[i] )
    
    if ( color == 'w'):
        if 'pass' in seq[-1]:
            del seq[-1]
        else:
            seq.append('play b pass')
        seq.append('genmove w')
    else:
        seq.append('genmove b')
    
    return clean_sgf,seq

if __name__ == '__main__':
    '''
import os
import sys
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askelf_script/ldm75')
os.chdir('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askelf_script')
    '''     
    input_path = sys.argv[1]
    '''
    if ( len(sys.argv) == 2 ):
        input_path = sys.argv[1]
    else:
        print('Usage: python3 gen_askelf_shellscript.py [input_path]')
        print('     : All of the *.sgf* in input_path will ask ELF for next move')
        print('Function: each sgf will be cover by correct mask.')
        sys.exit("Please enter correct command, goodbye!")'''

    sgfs = []

    for filename in os.listdir(input_path):
        if 'sgf' not in filename:
            continue
        sgfs.append( filename )
    
    outfile = open('elfinput_ldm75.txt', 'w')
    outfile_content = ""
    
    sgf_list_file = open('filelist_ldm75', 'w')
    filelist_content = ""
    
    for fname in sgfs:
        print(fname)
        cleansgf,seq = loadsgf(os.path.join( input_path ,fname ))
        for x in seq:
            outfile_content += x
            outfile_content += '\n'
        outfile_content += 'clear_board\n'
        
        filelist_content += fname + '\n'
        
    outfile_content += 'quit\n'
    
    outfile.write(outfile_content)
    outfile.close()
    sgf_list_file.write(filelist_content[:-1])
    sgf_list_file.close()