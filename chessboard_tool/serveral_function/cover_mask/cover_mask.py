import os
import re
import sys
import statistics

sgfs = ['00045__Vs_.sgf_0']
alphabet = '!@abcdefghijklmnopqrstuvwxyz#$'
alpha_dict = dict()
for i in range(len(alphabet)):
    alpha_dict[alphabet[i]] = i

def find_bounding_box(s):
    AB = re.search('AB(\[..\])*', s).group(0)
    AW = re.search('AW(\[..\])*', s).group(0)
    ABW = []
    ABW.extend( [ x[1:3] for x in re.findall('\[..\]', AB) ])
    ABW.extend( [ x[1:3] for x in re.findall('\[..\]', AW) ])
    B = [ x[1:3] for x in re.findall('[^A]B(\[..\])+', s)]
    W = [ x[1:3] for x in re.findall('[^A]W(\[..\])+', s)]

    pnts =[]
    for x in [ABW,B,W]:
        pnts.extend(x)

    xs = [pnt[0] for pnt in pnts]
    ys = [pnt[1] for pnt in pnts]
    xs.sort()
    ys.sort()

    return [xs[0],xs[-1], ys[0],ys[-1]]




'''
mask 第一個字母代表 horizontal/vertical
mask 第二個字母代表 誰贏
mask 第三個字母代表 (v=>左方 / h=>上方 ) 的顏色

黑先: 黑被包圍 => 黑先活 => 應該給白有利的局面 => w
黑先: 白被包圍 => 黑先殺白 => 應該給黑有利的局面 => b
白先: 白被包圍 => 白先活 => 應該給黑有利的局面  => b
白先: 黑被包圍 => 白先殺黑 => 應該給白有利的局面 => w


包圍用標準差判斷
誰先用sgf的手順判斷
'''
def masking(box, sgf):
    '''
    abs( middle - avgx) > abs (middle - avgy)
    '''
    def parse_ABW(s):
        AB = re.search('AB(\[..\])*', s).group(0)
        AW = re.search('AW(\[..\])*', s).group(0)
        AB = [ x[1:3] for x in re.findall('\[..\]', AB) ]
        AW = [ x[1:3] for x in re.findall('\[..\]', AW) ]
        return AB, AW

    def in_box(x,y,box,value=2):
        if alpha_dict[x] >=  alpha_dict[box[0]]-value \
        and alpha_dict[x] <=  alpha_dict[box[1]]+value\
        and alpha_dict[y] >= alpha_dict[box[2]]-value \
        and alpha_dict[y] <= alpha_dict[box[3]]+value:
            return 1
        return 0
    def replace_coors(s,discard_coors): # r 包含了所有不要的
        while len(discard_coors) !=0:
            Q = discard_coors.pop()
            Z = re.search( Q, s).group(0)
            s = s.replace( '['+Z+']' , '')
        return s

    def select_mask(s):
        #calculate distance to tian-yuan
        def distance2center(coor):
            return (alpha_dict['j'] - alpha_dict[coor[0]] )**2 + (alpha_dict['j'] - alpha_dict[coor[1]] )**2

        Bindex = re.search('[^A]B(\[..\])+', s).span()
        Windex = re.search('[^A]W(\[..\])+', s).span()
        who_first = 'W'
        if Bindex[0] < Windex[0]:
            who_first = 'B'

        B,W = parse_ABW(s)


        distances = []
        for coor in B:
            distances.append( (distance2center(coor) , 'b', coor))
        for coor in W:
            distances.append( (distance2center(coor) , 'w', coor))
        distances.sort()
        who_outside = distances[0][1]
        print('who_outside', who_outside, 'who_first', who_first)

        #third_letter
        print('@@@@',distances[0][2])
        X = 1 if distances[0][2][0] > 'j' else 0
        Y = 1 if distances[0][2][1] > 'j' else 0

        third_letter = ''
        who_outside_bar = 'w' if who_outside=='b' else 'b'


        # (for v, for h)
        if (X,Y) == (1,1):  # I
            third_letter = ( who_outside_bar , who_outside_bar)
        elif (X,Y) == (1,0):# IV
            third_letter = ( who_outside_bar , who_outside)
        elif (X,Y) == (0,1):# II
            third_letter = ( who_outside , who_outside_bar)
        elif (X,Y) == (0,0):# III
            third_letter = ( who_outside , who_outside)


        print('if vertical   third_letter = ',third_letter[0])
        print('if horizontal third_letter = ',third_letter[1])


        return who_outside, third_letter


    x1 = abs(alpha_dict['j'] - alpha_dict[box[0]] )
    x2 = abs(alpha_dict['j'] - alpha_dict[box[1]] )
    disy = x2 if x1 > x2 else x1
    print('box', box)
    print('distance to y', disy, x1,x2)
    y1 = abs(alpha_dict['j'] - alpha_dict[box[2]] )
    y2 = abs(alpha_dict['j'] - alpha_dict[box[3]] )
    disx = y2 if y1 > y2 else y1
    print('distance to x', disx, y1,y2)
    #print ('final distance to y' , disy ,  'final distance to x', disx)
    first_letter = 'v' if disx < disy  else 'h'

    second_letter,third_letters = select_mask(sgf)

    third_letter = third_letters[0] if first_letter == 'v'else third_letters[1]

    mask = first_letter + second_letter + third_letter + '.sgf'

    print ( mask )

    with open(mask,encoding='UTF-8') as f:
        mask_sgf = f.read()

    s = mask_sgf
    AB, AW = parse_ABW(s)
    ABW = AB
    ABW.extend(AW)

    discard_coors= []
    for xy in ABW:
        if in_box(xy[0],xy[1],box):
            if first_letter == 'v' and abs(alpha_dict['j'] - alpha_dict[xy[0]]) <=1:
                pass
            elif first_letter == 'h' and abs(alpha_dict['j'] - alpha_dict[xy[1]]) <=1:
                pass
            else:
                discard_coors.append(xy)

    s = replace_coors(s,discard_coors)

    AB = re.search('AB(\[..\])*', s).group(0)
    AW = re.search('AW(\[..\])*', s).group(0)

    sgf = sgf [0: sgf.find('AB')+2 ] + AB[2:] + sgf [sgf.find('AB')+2: ]
    sgf = sgf [0: sgf.find('AW')+2 ] + AW[2:] + sgf [sgf.find('AW')+2: ]

    return sgf


def output_sgf(fname, sgf):
    with open(fname , 'w', encoding='UTF-8') as f:
        f.write(sgf)
        f.close()

if __name__ == '__main__':
    #sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/cover_mask/output')
    #os.chdir('G:/VM_SYNC/chessboard_partition/切棋譜/cover_mask')
    if ( len(sys.argv) == 3 ):
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print('Usage: python3 cover_mask.py [input_path] [output_path]')
        print('     : All of the *.sgf* in input_path will be transformed and output at output_path')
        print('Function: each sgf will be cover by correct mask.')
        sys.exit("Please enter correct command, goodbye!")


    print('input path: ', input_path)
    print('output path: ', output_path)

    sgfs = [] # store full path of each sgf.
    for filename in os.listdir(input_path):
        if 'sgf' not in filename:
            pass
        sgfs.append( filename )

    for fname in sgfs:
        try:
            with open( os.path.join(input_path, fname) ,encoding='UTF-8') as f:
                sgf = f.read()
                box = find_bounding_box(sgf)
                output_sgf( os.path.join( output_path, fname), masking(box,sgf) )
        except:
            pass
