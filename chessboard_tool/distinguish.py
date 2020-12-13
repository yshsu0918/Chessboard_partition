from chessboard_tool import *
import os

# parameters

## input path
path = './chao/第2部 邊上的死活/第3章 四線型'

## output path
output_path_tolive = './chao/side_ch3_tolive'
output_path_tokill = './chao/side_ch3_tokill'
output_path_boundingbox_error = './TOMH736/bounderror'

outputs = [ output_path_tolive , output_path_tokill]

for x in outputs:
    if not os.path.isdir(x) :
        os.mkdir(x)

sgf_str,fnames = sgfs2strs(path)


for i, sgf_str in enumerate(sgf_str,0):
    
    print('------------------------------------')
    print('         ', i , fnames[i])
    print('------------------------------------')
    try:
        problem = sgfstr_tool( sgf_str )
        problem.has_spin = True
        problem.find_bounding_box()
        chosen_path = ''
        print(problem.who_outside_color ,problem.firststep_color)
        if False:
        #if problem.Is_boundingbox_overmiddleline():
            chosen_path = output_path_boundingbox_error
        elif ( problem.who_outside_color == problem.firststep_color):
            chosen_path = output_path_tokill
        else:
            chosen_path = output_path_tolive
        
        str2sgf( os.path.join(chosen_path, fnames[i]), problem.sgf_str)
    except:
        print('error')