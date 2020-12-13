
# run on CGI QQQ

import os
import re
import sys
import statistics
import sys
from os import walk
from os.path import join

'''
功能: 過濾棋譜

python3 gen_askcgi_shellscript.py ./QQ/input ./QQ/output
sh ask_cgi.sh
產生myresult[只留下 loadsgf 的回應即 "= black" or "? badsgf" ] 以及filelist

python3 delete_badsgf.py 

會從./QQ/input 挑出不會讓CGI_ZERO噴錯的 SGF 到 ./QQ/good_sgf
python3 gen_askcgi_shellscript.py ./QQ/good_sgf ./QQ/output
sh ask_cgi.sh

'''


#sys.argv[1] = 'G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script/input'
#sys.argv[2] = 'G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script/output'

def masking(sgf):

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
    return result_sgf, answer_step, color

def output_sgf(fname, sgf):
    with open(fname , 'w', encoding='UTF-8') as f:
        f.write(sgf)
        f.close()

def negative(color):
    if color == 'b':
        return 'w'
    return 'b'

if __name__ == '__main__':
    '''
import os
import sys
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script/chao253_tolive84')
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script/noans_sgf')
os.chdir('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script')
    ''' 
    if ( len(sys.argv) == 3 ):
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print('Usage: python3 gen_askcgi_shellscript.py [input_path] [outputfile]')
        print('     : All of the *.sgf* in input_path will ask CGI for next move')
        print('Function: each sgf will be cover by correct mask.')
        sys.exit("Please enter correct command, goodbye!")

    sgfs = []
    
    before = '''
BOARD_SIZE=19
RADIUS_PATTERN_MODE_NUMBER=1
input_radius_pattern=.$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c 8).QQ
'''
    middle = '''\necho \"loadsgf \"{sgf_filename} >> $input_radius_pattern \
\n#echo \"play \"{negative_color}\" pass\" >> $input_radius_pattern \
\n#echo \"dcnn_move_order\" >> $input_radius_pattern \
\necho \"genmove \"{color} >> $input_radius_pattern'''
    #after = '''Release/CGI -conf_file cgi_play_g0_opp.cfg < $input_radius_pattern > myresult 2> /dev/null'''
 
    after = '''Release/CGI -conf_file cgi_play_g0_opp.cfg < $input_radius_pattern | tee myresult '''
    

    for filename in os.listdir(input_path):
        if 'sgf' not in filename:
            continue
        sgfs.append( filename )
    
    outfile = open('./ask_cgi_chao232_tolive84.sh', 'w')
    middle_content = ""
    
    sgf_list_file = open('filelist', 'w')
    filelist_content = ""
    
    for fname in sgfs:
        f = open( os.path.join( input_path ,fname ) , encoding='UTF-8')
        sgf = f.read()
        clean_sgf, answer_step,color = masking(sgf)
        output_sgf( os.path.join(output_path, fname).replace('_mask_','_noans_'), clean_sgf )
        f.close()
        
        sgf_abs_path = os.path.join(output_path, fname).replace('_mask_','_noans_')
        middle_content += middle.format(sgf_filename = sgf_abs_path, negative_color = negative(color), color = color) 
        
        filelist_content += fname + '\n'
            
    outfile.write(before+ '\n'+middle_content+'\n'+after)
    outfile.close()
    sgf_list_file.write(filelist_content[:-1])
    sgf_list_file.close()