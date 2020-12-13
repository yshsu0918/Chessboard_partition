# from chessboard_tool import *
# import os

# path = './e.sgf'
# problem =  sgfstr_tool(sgf2str(path))

# problem.dynamic_mask()

from chessboard_tool import *
import os

# parameters

## input path
path = './chao_vol1/chao_vol1_tolive37/side_ch2_tolive_23.sgf'

sgf_str = sgf2str(path)
print(sgf_str)
problem = sgfstr_tool( sgf_str )    
#print(problem.sgf_str)

#book_answers.append( (fnames[i], problem.answer_step, problem.firststep_color ) )
print('QQ',( problem.answer_step, problem.firststep_color ))
step_form_sgf = problem.dynamic_mask(box_width = 3)
print(step_form_sgf)