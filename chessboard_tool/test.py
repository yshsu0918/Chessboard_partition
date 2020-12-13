from chessboard_tool import *
import os

#T = sgfstr_tool(sgf2str('test1.sgf'))

print('------------init------')
#mask = sgfstr_tool( sgf2str('mask.sgf') )
#mask = sgfstr_tool( sgf2str('mask.sgf') )
#T.show()
#str2sgf( 'test_str2sgf.sgf', T.output() )
#R = union(problem,mask)
#str2sgf( 'test_union.sgf' , R.output() )


maps = generate_isomorphism()
path = './TOMM735/TOMM735'
sgf_str , fnames = sgfs2strs(path)

vwww = sgf2str( 'vwww.sgf' )
vwwb = sgf2str( 'vwwb.sgf' )
vbbw = sgf2str( 'vbbw.sgf' )
vbbb = sgf2str( 'vbbb.sgf' )

ovww = sgf2str( './history/history_mask/vww.sgf' )
ovwb = sgf2str( './history/history_mask/vwb.sgf' )
ovbw = sgf2str( './history/history_mask/vbw.sgf' )
ovbb = sgf2str( './history/history_mask/vbb.sgf' )
'''
old_masks = [ ovww , ovwb , ovbw, ovbb ]
name_QQ = [ 'hww.sgf', 'hwb.sgf', 'hbw.sgf', 'hbb.sgf']
for i, sgf_str in enumerate(old_masks):
    Q = spin( sgf_str ,  maps[ 4 ])
    str2sgf(os.path.join('./history/history_mask', name_QQ[i]), Q)
'''
'''
kovbbb = sgf2str( 'ko_vbbb.sgf' )
kovbbw= sgf2str( 'ko_vbbw.sgf' )
testsample = sgfstr_tool(sgf2str('a.sgf'))
testsample.cut_mask()
str2sgf( 'b.sgf', testsample.sgf_str)
'''
'''黑白交換
str.replace('AB','ZZZ').replace('AW', 'AB').
replace('ZZZ','AW').replace(';B[', '$$$').replace(';W[',';B[').replace('$$$',';W[')
'''
book_answers = []
elfs = []
for i, sgf_str in enumerate(sgf_str,0):
    print('------------------------------------')
    print('         ', i , fnames[i])
    print('------------------------------------')
    problem = sgfstr_tool( sgf_str )
    problem.cut_mask()
    problem.spin_to_init(maps)
    book_answers.append( (fnames[i], problem.answer_step, problem.firststep_color ) )
    str2sgf( os.path.join('./TOMM735/TOMM735_spin', fnames[i] ) , problem.sgf_str )
    mask_dict = {'ww': vwww ,'wb': vwwb , 'bw': vbbw, 'bb': vbbb }
    #old_mask_dict = {'ww': ovww ,'wb': ovwb , 'bw': ovbw, 'bb': ovbb }

    mask = sgfstr_tool( mask_dict[ problem.who_outside_color + problem.firststep_color ] )
    print(problem.who_outside_color + problem.firststep_color)
    R = union(problem, mask) # R is sgfstr_tool


    step_form_sgf = R.None_ABAW_SGF()
    #elfs.append(R.gen_elf_script())
    if step_form_sgf:
        str2sgf( os.path.join('./TOMM735/TOMM735_mask', fnames[i] ) , step_form_sgf )
        elfs.append(R.gen_elf_script())
    else:
        print(fnames[i], 'E@@@R')
        del book_answers[-1]


print(book_answers)
gen_askcgi_script(book_answers, book_answers_path = './TOMM735/TOMM735_mask')
gen_askelf_script(elfs)

#demosample
'''
problem = sgfstr_tool(demosample)
mask1 = sgfstr_tool(kovbbb)
mask2 = sgfstr_tool(kovwww)
R = union(problem, mask1)
str2sgf( os.path.join('./demo/ko', 'a.sgf' ) , R.output(truncate_solution=False) )
R = union(problem, mask2)
str2sgf( os.path.join('./demo/ko', 'b.sgf' ) , R.output(truncate_solution=False) )
'''

#str2sgf( 'ko_vwww.sgf' , swap_color_in_sgfstr(kovbbb))
#str2sgf( 'ko_vwwb.sgf' , swap_color_in_sgfstr(kovbbw))


'''
problem = sgfstr_tool(sgf2str('a.sgf'))
str2sgf( 'test_none_abaw.sgf' , problem.None_ABAW_SGF())
'''


