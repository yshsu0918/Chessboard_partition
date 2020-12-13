
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
sh ask_cgi.sh => 產生 myresult & filelist

myresult: CGI的答案
filelist: goodsgf filename

[need file myresult and filelist]
python3 compare_zero_and_book.py ./QQ/good_sgf ./QQ/

'''


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
    #print('@translate_CGI_coor:', s, type(s))
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
        #print('(;' +  color + '[' + coor +']'+ 'C[' + comment +']' + ')')
        return '(;' +  color + '[' + coor +']'+ 'C[' + comment +']' + ')'


alphabet = '!@abcdefghijklmnopqrstuvwxyz#$'
alpha_dict = dict()
for i in range(len(alphabet)):
    alpha_dict[alphabet[i]] = i


def negative(color):
    if color == 'b':
        return 'w'
    return 'b'

def get_fname_from_filelist(fname = 'filelist'):
    f = open(fname, 'r')
    fs = f.readlines()
    return fs

def get_answer_from_result(fname='result'):
    f = open(fname, 'r')
    lines = f.readlines()
    correct_result = []
    for line in lines:
        print(line)
        if 'black' in line or '=' not in line or len(line)<=1:
            continue
        else:
            correct_result.append( line.replace('= ',''))

    return correct_result


if __name__ == '__main__':
    '''
import os
import sys
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script/good_sgf')
sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script/stat')
os.chdir('G:/VM_SYNC/chessboard_partition/切棋譜/gen_askcgi_script')
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

    correct_path = os.path.join(output_path,'correct')
    wrong_path = os.path.join(output_path,'wrong')
    resign_path = os.path.join(output_path,'resign')


    fnames = get_fname_from_filelist('filelist')
    CGI_results = get_answer_from_result('caffe8_sim8000_noresign.txt')

    count = 0
    correct_count = 0
    wrong_count = 0
    resign_count = 0

    if len(CGI_results) != len(fnames):
        print('myresult and filelist not consistent!!\n')
        print(len(CGI_results) , len(fnames))

    for i in range( len(fnames)):
        count += 1
        fname = fnames[i].replace('\n','')
        CGI_result = CGI_results[i].replace('\n','')
        with open( os.path.join( sys.argv[1] ,fname ) , encoding='UTF-8') as f:
            sgf = f.read()
            clean_sgf, answer_step,color = masking(sgf)
            out_sgfname = ''

            moveorder_resultf_comment = 'dcnn_move_order fail in zero' #Need to ask rockman
            try:
                print(fname,color,'Correct answer ' +answer_step +' CGI answer ' + str(CGI_result) + translate_CGI_coor(CGI_result)  )
            except:
                print(fname,color,'Correct answer ' +answer_step +' CGI answer ' + str(CGI_result) + CGI_result)
            if 'resign' in CGI_result or 'PASS' in CGI_result or 'pass' in CGI_result:
                #print('Correct answer ' +answer_step +' CGI answer ' + str(CGI_result) )
                out_sgfname = os.path.join(resign_path, fname)
                output_sgf( out_sgfname, clean_sgf[0:-1]+ 'C[CGI resign or pass]' + branch_str(color.upper(),answer_step)+ ')')
                resign_count += 1
            else:

                #print("@main before enter CGI_result: ", CGI_result)
                #print('Correct answer ' +answer_step +' CGI answer ' + translate_CGI_coor(CGI_result) + ' ' + str(CGI_result) )
                if answer_step == translate_CGI_coor(CGI_result):

                    out_sgfname = os.path.join(correct_path, fname)
                    correct_count += 1
                else:
                    out_sgfname = os.path.join(wrong_path, fname)
                    wrong_count += 1
                output_sgf( out_sgfname , clean_sgf[0:-1] + branch_str(color.upper(),answer_step) + branch_str(color.upper(),translate_CGI_coor(CGI_result), 'CGI ANSWER' + moveorder_resultf_comment) + ')' )

    statistics_file = os.path.join(output_path,'statistics.txt')
    print('\nTotal: '+ str(count) + '\nCorrect: '+str(correct_count)+'\nWrong:'+str(wrong_count)+'\nresign:'+str(resign_count)+'\n'+'Accuracy: '+ str( (correct_count/count)))
    with open(statistics_file,'w') as f:
        f.write('\nTotal: '+ str(count) + '\nCorrect: '+str(correct_count)+'\nWrong:'+str(wrong_count)+'\nresign:'+str(resign_count)+'\n'+'Accuracy: '+ str( (correct_count/count)))
        f.close()