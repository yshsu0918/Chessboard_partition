
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

    print( result_sgf)
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
            output_sgf( os.path.join('./QQ/no_ans_sgf/', fname) , clean_sgf)

            os.system('sh ./mmm.sh temp.sgf ' + color + ' ' + negative(color) )

            CGI_result = ''
            with open('myresult', 'r') as myresultf: # get output from CGI
                r = myresultf.readlines()
                print('@main r = ', r, type(r))
                if 'bad sgf' in r[1]:
                    print("================", "bag sgf:", fname,"============= ")
                    myresultf.close()
                    f.close()
                    continue

                CGI_result = r[15][2:].replace('\n','') #dirty
                print("@main first CGI_result: ", CGI_result)
                myresultf.close()

            moveorder_resultf_comment = ''
            with open('moveorder_result','r') as moveorder_resultf:
                moveorder_resultf_comment = moveorder_resultf.read()
                moveorder_resultf.close()

            print('@main', CGI_result, type(CGI_result) , len(CGI_result))

            out_sgfname = ''
            correct_path = os.path.join(output_path,'correct')
            wrong_path = os.path.join(output_path,'wrong')
            resign_path = os.path.join(output_path,'resign')

            if 'resign' in CGI_result or 'PASS' in CGI_result or 'pass' in CGI_result:
                print('Correct answer ' +answer_step +' CGI answer ' + str(CGI_result) )
                out_sgfname = os.path.join(resign_path, fname)
                output_sgf( out_sgfname, clean_sgf[0:-1]+ 'C[CGI resign or pass]' + branch_str(color.upper(),answer_step)+ ')')
            else:
                print("@main before enter CGI_result: ", CGI_result)
                print('Correct answer ' +answer_step +' CGI answer ' + translate_CGI_coor(CGI_result) + ' ' + str(CGI_result) )
                if answer_step == translate_CGI_coor(CGI_result):
                    out_sgfname = os.path.join(correct_path, fname)
                else:
                    out_sgfname = os.path.join(wrong_path, fname)
                output_sgf( out_sgfname , clean_sgf[0:-1] + branch_str(color.upper(),answer_step) + branch_str(color.upper(),translate_CGI_coor(CGI_result), 'CGI ANSWER' + moveorder_resultf_comment) + ')' )



            counter += 1
            f.close()
