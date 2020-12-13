
# run on CGI QQQ

import os
import re
import sys
import statistics
import sys

from chessboard_tool import *

def branch_str(color,coor,comment=None):    
    if comment == None:
        return '(;' +  color + '[' + coor +']'+ ')'
    else:
        return '(;' +  color + '[' + coor +']'+ 'C[' + comment +']' + ')'

def compare2ans(filename,problem_dir,result_dir,bookans):
    
    with open(filename,'r',encoding='UTF-8') as f:
        AIans_ = f.readlines()
        AIans = [ x.replace('= ', '') for x in AIans_]
        f.close()
    #print(bookans)
    print(AIans)
    tool = coor_tool()
    compare = []
    for i, x in enumerate(bookans):
        print(i,x,  AIans[i])
        if 'PASS' in AIans[i]:
            compare.append( ( x[0],x[1], 'PASS' ,x[2]) )
        else:
            compare.append( ( x[0],x[1], tool.charnum2charchar(AIans[i]) ,x[2]) )
    
    correct = os.path.join(result_dir, 'correct')
    wrong = os.path.join(result_dir, 'wrong')
    resign = os.path.join(result_dir, 'resign')
    if not os.path.isdir(result_dir):
        os.mkdir(result_dir)
    if not os.path.isdir(correct):
        os.mkdir(correct)
    if not os.path.isdir(wrong):
        os.mkdir(wrong)
    if not os.path.isdir(resign):
        os.mkdir(resign)

    C,W,R = 0,0,0
    
    for i, (fname,book_ans,cgi_ans,sol_color) in enumerate(compare,0):
        problem = sgfstr_tool(  sgf2str(os.path.join(problem_dir, fname) ) )
        result_sgfstr = problem.sgf_str
        print(fname,book_ans, cgi_ans,problem.answer_step)
        if book_ans == cgi_ans:
            sgf_path = os.path.join(correct, fname)            
            str2sgf( sgf_path, result_sgfstr[0:-1]+ 'C[CGI CORRECT]' + branch_str(sol_color.upper(),book_ans )+ ')')
            C+=1
        elif cgi_ans == 'PASS':
            sgf_path = os.path.join(resign , fname)       
            str2sgf( sgf_path, result_sgfstr[0:-1]+ 'C[CGI PASS]' + branch_str(sol_color.upper(),book_ans )+ ')')
            R+=1
        else:
            sgf_path = os.path.join(wrong , fname) 
            str2sgf( sgf_path, result_sgfstr[0:-1]+ 'C[CGI WRONG]' + 
            branch_str(sol_color.upper(),book_ans )+
            branch_str(sol_color.upper(),cgi_ans )+ ')')
            W+=1
    
    statistics_file = os.path.join(result_dir,'statistics.txt')
    with open(statistics_file,'w') as f:
        f.write('\nTotal: '+ str( len(compare)) + '\nCorrect: '+str(C)+'\nWrong:'+str(W)+'\nresign:'+str(R)+'\n'+'Accuracy: '+ str( (C/len(compare))))
        print(str( (C/len(compare)) ))
        f.close()

if __name__ == '__main__':
    #bookans = load('./chao70r/chao70r_20191217/book_answers.pickle')
    #compare2ans('result_chao70r_20191217.txt','./chao70r/chao70r_20191217','./chao70r/result/result_chao70r_20191217',bookans)
    bookans = load('./chao_vol1/chao_vol1_tolive_spin_automask/book_answers.pickle')
    compare2ans('./chao_vol1/result_chao_vol1_tolive_spin_automask_10000.txt', './chao_vol1/chao_vol1_tolive_spin_automask', './chao_vol1/result/chao_vol1_tolive_spin_10000',bookans)