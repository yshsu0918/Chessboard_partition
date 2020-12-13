from chessboard_tool import *
import os

# parameters
#\rockmanray_middle51\middle51_spin
# 把 path 中的所有棋譜 套上 mask_path 中合適的mask => AI可以聚焦在局部死活的棋譜 
## input path
path = './chao70r/chao_vol2_pudding'
#mask_path = './live_mask'
mask_path = './oldmask_fix_territory'
script_file_path = './chao_vol1/chao_vol1_tolive'
## output path
output_mask_path = './chao_vol1/chao_vol1_tolive_oldmask'

## output spin path
script_file_path = './chao_vol1/chao_vol1_tolive'
output_spin_path = './chao_vol1/chao_vol1_tolive_spin'
Is_outputspin = False
Is_mask = True
# end parameters



if not os.path.isdir(output_mask_path) :
    os.mkdir(output_mask_path)
if not os.path.isdir(output_spin_path) :
    os.mkdir(output_spin_path)

maps = generate_isomorphism()
sgf_str , fnames = sgfs2strs(path)
print(sgf2str,fnames)


book_answers = []
elfs = []
goals = []

if Is_outputspin:
    for i, sgf_str in enumerate(sgf_str,0):
        print('------------------------------------')
        print('         ', i , fnames[i])
        print('------------------------------------')
        problem = sgfstr_tool( sgf_str )
        problem.spin_to_init(maps)
        print(problem.sgf_str)
        str2sgf( os.path.join(output_spin_path,fnames[i]) ,problem.sgf_str ) # optional


if not Is_mask:
    pass
else:
    for i, sgf_str in enumerate(sgf_str,0):
        print('------------------------------------')
        print('         ', i , fnames[i])
        print('------------------------------------')
        problem = sgfstr_tool( sgf_str )
        
        problem.spin_to_init(maps)
        print(problem.sgf_str)



        book_answers.append( (fnames[i], problem.answer_step, problem.firststep_color ) )
        
        print((fnames[i], problem.answer_step, problem.firststep_color ))
        mask_dict = gen_mask_dict(mask_path)
        mask = sgfstr_tool( mask_dict[ problem.who_outside_color + problem.firststep_color ] )
        print(problem.who_outside_color + problem.firststep_color)
        
        R = union(problem, mask) # R is sgfstr_tool
        R.who_outside_color = problem.who_outside_color
        R.firststep_color = problem.firststep_color
        goals.append( '0' if R.who_outside_color == R.firststep_color else '1')
        step_form_sgf = R.None_ABAW_SGF(target_flag=True, nobw=True, targetblock_flag=True)


        #input('')

        if step_form_sgf:
            str2sgf( os.path.join(output_mask_path, fnames[i] ) , step_form_sgf )
            elfs.append(R.gen_elf_script())
        else:
            print(fnames[i], 'E@@@R')
            del book_answers[-1]




    print(book_answers)
    gtp_input_file = os.path.basename(output_mask_path)+'_gtpinput.txt'
    gen_askcgi_script(book_answers, script_file_path = script_file_path ,gtp_input_file = gtp_input_file, book_answers_path = output_mask_path,experiment_name = os.path.basename(output_mask_path) )
    gen_askelf_script(elfs, script_file_path = script_file_path , gtp_input_file= gtp_input_file)


    print( script_file_path, gtp_input_file, output_mask_path, os.path.basename(output_mask_path) )

    # gen_askcgi_script(book_answers,script_file_path = script_file_path, book_answers_path = output_mask_path)
    # gen_askelf_script(elfs,script_file_path = script_file_path)


    for x in goals:
        print(x)