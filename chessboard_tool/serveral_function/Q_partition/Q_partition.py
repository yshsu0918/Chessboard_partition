# divide sgf file into single
'''
棋譜來源
    01基本死活寶典--死活階梯練習
    02圍棋死活詞典
    03《圍棋死活辭典》-- 趙治勳
    04死活大全（陳版）
    05死活初級
    06死活中級
    07死活高級
    08TOM初級737
    09TOM中級737
    10TOM高級737
分割棋譜
    一個棋譜可能有多題
    轉換成每個sgf只有一題(tree形式)
    每一題轉成多個single path
'''

#TODO find sgf recursively in directory and make a list to store them.

import os
import re
import sys
from os import walk
from os.path import join

#path = 'C:/Users/Samox/Documents/死活問題含解說繁體UTF-8_SingleLine_Merged可正確讀取/死活問題含解說(繁體UTF-8)_SingleLine_Merged(可正確讀取)'
#four_corner = './03《圍棋死活辭典》-- 趙治勳/《圍棋死活辭典》下冊-- 趙治勳/00061__Vs_.sgf'
#branch_two = './03《圍棋死活辭典》-- 趙治勳/趙治勳－圍棋死活辭典（上冊）/第3部 死活之應用/第2章 各種侵入手法/08.sgf'

#字串處理工具 產生巢狀list
def slice_A2B(s,A,B):
    r = list()
    buf = ''
    A_counter = 0 # number of char A duplicate
    for i in range(len(s)):
        if( s[i] == A):
            A_counter += 1
            buf += A
            continue
        elif( s[i] == B):
            A_counter -= 1
            buf += B
            if(A_counter == 0):
                r.append(buf)
                buf = ''
            continue
        if A_counter != 0 : # now is in A...B
            buf += s[i]
    return r


class board_reader():
    # __init__ ->
    def __init__(self, sgfname,code = 'divide'):
        def clean_squarebracket(str):
            flag = 1
            r = ''
            for i in range(len(str)):
                if( str[i] == '['):
                    flag = 0
                elif (str[i] == ']'):
                    flag = 1
                    r+=' '
                    continue

                if(flag):
                    r = r + str[i]
            return r.replace(' ','')

        def parseintotree(s):
            # recursive structure [ node , [branch1, branch2, ...] ]
            # recursive structure [ [branch1] , [ branch2], ... ]

            r = []
            bracket_at = s.find('(',1)
            if bracket_at == -1:
                return s[1:-1], 0
                #first and last char are '(' and ')'
                #end of branch

            node = s[1:bracket_at]
            r.append(node)
            branchs = slice_A2B( s[bracket_at:-1] , '(', ')')
            r.append(branchs)

            for i in range(len(r[1])):
                #print('before r[1][', i, ']', r[1][i])
                n,b = parseintotree( r[1][i] ) #r[1][i] means branch
                #print('after r[1][', i, ']', r[1][i])
                if b == 0:
                    r[1][i] = [n]
                else:
                    r[1][i] = b

            return node, r

        def gen_revelant_initial_board(s,sgfpath='NULL'):
            #TODO: change the first part of sgf so that everything is revalent.
            #algo: 使用解答的第一手 以一個"閥值"向周圍擴散 直到不能再擴散
            '''
            1. 找出解答的第一手
            2. parse 出 初始盤面
            3. DFS
            '''

            def diffusion(s):
                r = []
                for i in [-2,-1,0,1,2]:
                    for j in [-2,-1,0,-1,2]:
                        if i==0 and j == 0:
                            continue
                        r.append( alphabet[ alpha_dict[s[0]] + i ] + alphabet[ alpha_dict[s[1]]+ j ] )
                return r

            def DFS(ABW,BW):
                result = set()
                f = []
                sABW = set(ABW)
                sBW = set(BW)
                #print(sABW)
                #print(len(sABW),len( sBW), sBW)
                while len(sBW)!=0:
                    Q = []
                    while len(sBW)!=0:
                        Q.extend( diffusion(sBW.pop() ) )
                    S = set(Q)

                    sBW = (sABW & S)
                    sABW = sABW - sBW
                    #print(len(sABW),len( sBW), sBW)
                    #result = result | sBW

                return sABW
            try: 
                AB = re.search('AB(\[..\])*', s).group(0)
                AW = re.search('AW(\[..\])*', s).group(0)
            except:
                print('@generror', self.output_fname, s)
                return 'error' , 'error'
            
            B = [ x[1:3] for x in re.findall('[^A]B(\[..\])+', s)]
            W = [ x[1:3] for x in re.findall('[^A]W(\[..\])+', s)]
            T = [ AB, AW, B, W]
            alphabet = '!@abcdefghijklmnopqrstuvwxyz#$'
            alpha_dict = dict()
            for i in range(len(alphabet)):
                alpha_dict[alphabet[i]] = i
            ABW = []
            ABW.extend( [ x[1:3] for x in re.findall('\[..\]', AB) ])
            ABW.extend( [ x[1:3] for x in re.findall('\[..\]', AW) ])
            BW = []
            BW.extend(B)
            BW.extend(W)

            #print( ABW, BW)
            r = DFS(ABW,BW)
            #print(r)
            while len(r) !=0:
                Q = r.pop()
                Z = re.search( Q, s).group(0)
                #print(Z)
                s = s.replace( '['+Z+']' , '')
            #print('@@@', s)
            '''
            if sgfpath != 'NULL':
                with open( self.output_fname + '_clear' , 'w', encoding='UTF-8') as f:
                    f.write( s )
                    f.close()
            '''
            return s,ABW


        self.input_fname = os.path.join( sys.argv[1] , sgfname)
        self.output_fname = os.path.join( sys.argv[2] , sgfname)

        print('@init ', sgfname, self.input_fname, self.output_fname)

        with open(self.input_fname,encoding = 'UTF-8') as f:
            self.tree = f.read()
            buf = self.tree
            
            for x in re.finditer('(C\[[^\]\(\)]*(\([^\]]*\))[^\]\(\)]*\])',self.tree):
                print('--------------')
                print('@branch in bracelet bug: ', x.span(), self.output_fname)
                print(x.group(0))
                print(x.group(1))
                buf = buf.replace(x.group(1), '')
            self.tree = buf
            f.close()

        if code == 'divide':
            self.sgf_formats = []
            def tree2sgf_formats(nowsf, tree):
                #根據遞迴結構 dfs 產生每一種棋譜
                #終止條件: tree 中只有一個元素
                if len(tree) == 1:
                    self.sgf_formats.append(nowsf+ tree[0] )
                else:
                    if( type(tree[0]) == type( list())):
                        for x in tree:
                            tree2sgf_formats(nowsf, x)
                    else:

                        tree2sgf_formats(nowsf+tree[0], tree[1])
            #print(clean_squarebracket(self.tree))
            x , self.sgftree = parseintotree( self.tree )
            if (self.sgftree == 0):
                if( x[-1] == ')'):
                    self.sgftree = [x[:-1]]
                else:
                    print('#')
                    print(self.sgfpath)
                    self.sgftree = [x]

            #print(self.sgftree)

            tree2sgf_formats( '' ,self.sgftree )

            cleans = []
            for s in self.sgf_formats:
                Q , QQ = gen_revelant_initial_board(s)
                cleans.append(Q)

            print('@init @divide number of output ', len(cleans))

            c = 0
            for x in cleans:
                #print()
                with open( self.output_fname + '_' + str(c)  , 'w', encoding = 'UTF-8') as f:
                    f.write( '('+x+')')
                    f.close()
                c += 1

        elif code == 'divide_by_question':
            #TODO
            '''
            version 1.
            1.slice_A2B 得到第一層tree所形成的list
            2.取每一棵tree的BW資料 送進 gen_revelant_initial_board 得到 初始盤面list
            3.依據初始盤面分群
            4.蒐集相同初始盤面的BW資料以及初始盤面 產生 具有相同初始盤面(我相信這就代表同一題)的sgf

            '''

            first_level = slice_A2B(self.tree[1:-1],'(',')')
            #print(first_level, len(first_level))

            init_board = self.tree[0: self.tree[1:-1].find('(')+1] # 少最後一個 ')'
            sabws = []
            cleans = []
            for x in first_level:
                #print(x)
                s = init_board + x + ')'
                clean, sabw = gen_revelant_initial_board(s)
                if clean == 'error':
                    return None
                cleans.append(clean[ 0: clean[1:-1].find('(') + 1]) # 少最後一個 ')'

            cleans_set = set(cleans) #去除重複項

            #print( len(cleans_set) )

            self.sgfs = []
            c = 0
            for e in cleans_set:
                sgf = e
                for i in range( len(first_level)) :
                    if e == cleans[i]:
                        sgf += first_level[i]
                sgf += ')'
                #print(os.path.split(os.path.abspath(self.sgfpath))[1])
                
                self.sgfs.append(sgf)

                c += 1


        else:# Mean: not divide
            gen_revelant_initial_board(self.tree,self.sgfpath)

'''
TEST DATA

#simple_ex = board_reader('./06死活中級/死活中級/4.sgf')
#recursive_ex = board_reader('./10TOM高級737/gaoji0647.sgf')
#recursive_ex = board_reader('./10TOM高級737/gaoji0647.sgf')
#four_corner = board_reader('./03《圍棋死活辭典》-- 趙治勳/《圍棋死活辭典》下冊-- 趙治勳/00068__Vs_.sgf')
'''


if __name__ == '__main__':
    # sys.argv.append('G:/VM_SYNC/chessboard_partition/切棋譜/Q_partition/input')

    if ( len(sys.argv) == 3 ):
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print('Usage: python3 Q_partition.py [input_path] [output_path]')
        print('     : All of the *.sgf* in input_path will be transformed and output at output_path')
        print('Function: Transform multiple question sgfs into single question')
        sys.exit("Please enter correct command, goodbye!")


    print('input path: ', input_path)
    print('output path: ', output_path)

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    sgfs = [] # store full path of each sgf.
    for filename in os.listdir(input_path):
        if 'sgf' not in filename:
            continue
        sgfs.append( filename )

    #sgfs = [ four_corner ]
    print(sgfs)

    for sgfname in sgfs:
        # try:
        #     sgf = board_reader(sgfname,code='divide_by_question')
        # except Exception as e:
        #     print('@except ', sgfname)
        #     #print(e)
        #     pass
        sgf = board_reader(sgfname,code='divide_by_question')

        for i,sgf_str in enumerate(sgf.sgfs):
            with open( os.path.join(output_path, sgfname.replace('.sgf','')+str(i)+'.sgf'), 'w', encoding = 'UTF-8') as f:
                f.write(sgf_str)
                f.close()


#TODO 有時候單一路徑最後會有多一個括弧 )
#1. 編碼問題?
#2. 從原本的樹 切題目出來?
#3. 先寫bounding box功能?
#4. []中 有() 導致parsing 錯誤
