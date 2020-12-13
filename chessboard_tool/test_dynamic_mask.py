# from chessboard_tool import *
# import os

# path = './e.sgf'
# problem =  sgfstr_tool(sgf2str(path))

# problem.dynamic_mask()

from chessboard_tool import *
import os

# parameters

## input path
path = './chao70r/chao_vol2_pudding'

## output path
output_mask_path = './chao70r/chao_vol2_pudding_bound3'
script_file_path = './chao70r'
# end parameters

if not os.path.isdir(output_mask_path) :
    os.mkdir(output_mask_path)

maps = generate_isomorphism()
sgf_str , fnames = sgfs2strs(path)
print(sgf2str,fnames)


book_answers = []
elfs = []
goals = []
for i, sgf_str in enumerate(sgf_str,0):
    print('------------------------------------')
    print('         ', i , fnames[i])
    print('------------------------------------')
    problem = sgfstr_tool( sgf_str )    
    #print(problem.sgf_str)
    
    book_answers.append( (fnames[i], problem.answer_step, problem.firststep_color ) )
    print((fnames[i], problem.answer_step, problem.firststep_color ))
    step_form_sgf = problem.dynamic_mask(box_width = 3)


    if step_form_sgf:
        str2sgf( os.path.join(output_mask_path, fnames[i] ) , step_form_sgf )
        elfs.append(problem.gen_elf_script())
    else:
        print(fnames[i], 'E@@@R')
        del book_answers[-1]

print(book_answers)
gtp_input_file = os.path.basename(output_mask_path)+'_gtpinput.txt'
gen_askcgi_script(book_answers, script_file_path = script_file_path ,gtp_input_file = gtp_input_file, book_answers_path = output_mask_path,experiment_name = os.path.basename(output_mask_path) )
gen_askelf_script(elfs, script_file_path = script_file_path , gtp_input_file= gtp_input_file)

for x in goals:
    print(x)