from chessboard_tool import *
import os


'''
Generating masked files by JSON:
* Category: 題目來源/書名/章節/.....
* Raw Sgf filename: 原題(without mask)
* Output Sgf masked filename: 
* Sgf content: 
* Sgf content after masked: 
* 本題SearchGoal: 活棋, 殺棋, 劫活, 雙活
* 是哪一方要活棋還是殺棋: Black, White
* 活棋/殺棋的位置 ap&ap, sa
* 打劫規則: allowko, disallowko
* answer_sequence: (could be a tree)
* answer_first_move: 
* Mask Rule: maskA|maskB|maskC
* Mask: ac, as, .....
* Additional mask: +sc|-de 
* Date:
'''

config_dict = ['']



## input path
path = './chao70r/chao70_spin'
mask_path = './oldmask_fix_territory'

## output config path 
output_config_path = './chao70r/chao70r_config'
output_json_path = './chao70r/chao70r_json'

if not os.path.isdir(output_config_path) :
    os.mkdir(output_config_path)

if not os.path.isdir(output_json_path) :
    os.mkdir(output_json_path)


maps = generate_isomorphism()
sgf_strs , fnames = sgfs2strs(path)


for i, sgf_str in enumerate(sgf_strs):
    problem = sgfstr_tool( sgf_str )
    mask_dict = gen_mask_dict(mask_path)
    mask = sgfstr_tool( mask_dict[ problem.who_outside_color + problem.firststep_color ] )
    print(problem.who_outside_color + problem.firststep_color)
    
    config_dict = dict()


    R = union(problem, mask) # R is sgfstr_tool
    R.who_outside_color = problem.who_outside_color
    R.firststep_color = problem.firststep_color
    step_form_sgf = R.None_ABAW_SGF(target_flag=True, nobw=True, targetblock_flag=True)

    if step_form_sgf:
        str2sgf( os.path.join(output_mask_path, fnames[i] ) , step_form_sgf )
        elfs.append(R.gen_elf_script())
    else:
        print(fnames[i], 'E@@@R')
        del book_answers[-1]
