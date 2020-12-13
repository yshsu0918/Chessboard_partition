from functools import cmp_to_key
import numpy as np
import re
import datetime
import os
import time


def gen_mask_dict(path):
    vwww = sgf2str( os.path.join(path,'vwww.sgf') )
    vwwb = sgf2str( os.path.join(path,'vwwb.sgf') )
    vbbw = sgf2str( os.path.join(path,'vbbw.sgf') )
    vbbb = sgf2str( os.path.join(path,'vbbb.sgf') )
    return {'ww': vwww ,'wb': vwwb , 'bw': vbbw, 'bb': vbbb }

class coor_tool:
    def __init__(self , mode = 'sgf'):
        self.alphabet = 'abcdefghijklmnopqrs'
        self.sgf_eng = 'abcdefghijklmnopqrs'
        self.sgf_dict = dict()
        self.elf_eng = 'abcdefghjklmnopqrst' # no i
        self.elf_dict = dict()
        for i in range(len(self.elf_eng)):
            self.sgf_dict[self.sgf_eng[i]] = i
            self.elf_dict[self.elf_eng[i]] = i
        
        self.mode = mode        

    def charnum2charchar(self, ch):
        return ch[0].lower()+ self.num2char( 19-int(ch[1:]) )

    def charchar2charnum(self, ch):
        return ch[0].upper()+ str(19 - self.char2num(ch[1]))

    def char2num(self, ch):
    
        if self.mode == 'elf':
            if(ch == 'i'):
                print('Error, char i shouldnt appear')
            return self.elf_dict[ch]
        else:
            return self.sgf_dict[ch]

    def num2char(self, num):
        if self.mode == 'elf':
            return self.elf_eng[num]
        else:
            return self.sgf_eng[num]

def sgfcc2elfcn(charchar):
    A = coor_tool(mode = 'sgf')
    B = coor_tool(mode = 'elf')
    X = charchar[0]
    Y = charchar[1]
    return B.num2char(A.char2num(X)) + str(19 - A.char2num(Y))
    



ct_sgf = coor_tool('sgf')
def coor_type_casting( alphabet_pairs ):                    
    return [ ( ct_sgf.char2num(x[1]) , ct_sgf.char2num(x[0]) ) for x in alphabet_pairs  ]

class sgfstr_tool:
    def __init__(self, sgf_str):
        if len(sgf_str) == 0:
            return
        #print(sgf_str)
        self.sgf_str = sgf_str
        self.calculate_attribute_by_sgfstr()
        self.has_spin = True
        #self.quadrant_value
        #self.hv
        #self.bounding_box
        #self.who_outside_color

    def calculate_attribute_by_sgfstr(self):
        self.has_spin = True
        AB = re.search('AB(\[..\])*', self.sgf_str)
        self.section_AB = [ x[1:3].lower() for x in re.findall('\[..\]', AB.group(0)) ] if AB else []
        AW = re.search('AW(\[..\])*', self.sgf_str)
        self.section_AW = [ x[1:3].lower() for x in re.findall('\[..\]', AW.group(0)) ] if AW else []
        self.section_B = [ x[1:3].lower() for x in re.findall('[^A]B(\[..\])+', self.sgf_str)]
        self.section_W = [ x[1:3].lower() for x in re.findall('[^A]W(\[..\])+', self.sgf_str)]
        self.sections  = [self.section_AB,self.section_AW, self.section_B,self.section_W]
        self.calculate_coor_by_section()
    
    def calculate_coor_by_section(self, union_flag = False):
        self.coor_AB = coor_type_casting( self.section_AB )
        self.coor_AW = coor_type_casting( self.section_AW )
        self.coor_B  = coor_type_casting( self.section_B )
        self.coor_W  = coor_type_casting( self.section_W )
        self.coors   = [ self.coor_AB , self.coor_AW , self.coor_B , self.coor_W ]
        
        tool = coor_tool()
        # for  x in self.sections:
        #     for y in x:        
        #         print(y,end=" ,")
        #     print()

        #self.show()
        if ( (len(self.section_B) ==0 and len(self.section_W) == 0)):
            self.firststep_color = 'None'
        elif union_flag:
            pass
        else:
            self.answer_step , self.firststep_color = self.find_first_step()

        
        if self.section_AB or self.section_AW:
            
            self.find_bounding_box()
            self.get_location()
        if self.section_B and self.section_W:
            self.who_outside()
        
        #self.show()    
    def spin_to_init(self, maps): # 轉到右上角水平 #要把答案也轉上去
        
        idx = self.quadrant_value
        print('idx:' , idx)
        #ABAW = self.section_AB.copy()
        #ABAW.extend(self.section_AW)
        #sgf_str = self.output(truncate_solution=True)
        self.sgf_str = spin( self.sgf_str ,  maps[ idx ])

        self.calculate_attribute_by_sgfstr()
        if self.hv :
            self.sgf_str = spin( self.sgf_str ,  maps[ 4 ])
        self.calculate_attribute_by_sgfstr()
    def init_by_AWABBW(self, AB, AW, B , W, firststep_color ):
        self.section_AB = AB
        self.section_AW = AW
        self.section_B = B
        self.section_W = W
        self.sections = [self.section_AB,self.section_AW, self.section_B,self.section_W]  
        self.firststep_color = firststep_color
        self.sgf_str = self.output()
        self.calculate_coor_by_section()
    
    def inbox( self, coor ):
        
        X = 0 #padding = 0
        bounding_box = self.bounding_box
        #print(outside_bounding_box ,coor, (coor[0] > bounding_box[0]-X) and (coor[0] < bounding_box[1]+X) and (coor[1] > bounding_box[2]-X) and (coor[1] < bounding_box[3]+X) )    
        if (coor[0] > bounding_box[0]-X) and (coor[0] < bounding_box[1]+X) and (coor[1] > bounding_box[2]-X) and (coor[1] < bounding_box[3]+X) :
            return True
        return False

    def find_maxblock(self, target = 'tolive', datasource = 'section_BW'):
        def surrounding( xy ):
            tool = coor_tool()
            x = tool.char2num(xy[0])
            y = tool.char2num(xy[1])
            r = []
            for delta_x,delta_y in [ (1,0),(0,1),(0,-1), (-1,0) ]:
                try:
                    r.append(  tool.num2char( x+delta_x ) +  tool.num2char( y+delta_y) )
                except:
                    pass
            return r
        

        if target == 'tolive':            
            blocks = []
            #choose data source
            if datasource == 'section_BW':
                chess_onboard = self.section_B.copy() if self.firststep_color == 'b' else self.section_W.copy()
            elif datasource == 'mix':
                chess_onboard = self.section_B.copy() if self.firststep_color == 'b' else self.section_W.copy()
                chess_onboard.extend( self.section_AB.copy() if self.firststep_color == 'b' else self.section_AW.copy() )
            elif datasource == 'oneeye_dataset':
                chess_onboard = self.section_AB.copy()
            while len(chess_onboard) != 0:
                current_block = []
                need2check = [ chess_onboard.pop() ]
                while len(need2check) != 0:
                    cur = need2check.pop()
                    current_block.append(cur)
                    for n in surrounding(cur):
                        if n in chess_onboard and n not in current_block:
                            need2check.append(n)
                            chess_onboard.remove(n)
                if len(current_block) < 20: #若block大小大於20則表示是中線.
                    blocks.append( current_block )
                    print( 'current blen',len(current_block))
        
        max_block_size = 0
        max_block = []
        for block in blocks:
            if len(block) > max_block_size:
                max_block = block
                max_block_size = len(block)
        for x in blocks:
            print(len(x), x)

        return max_block[0]
        
    def cut_mask(self):
        print(self.bounding_box)
        self.sgf_str = gen_revelant_initial_board(self.sgf_str)
        self.calculate_attribute_by_sgfstr()


    def show(self):
        print(self.__dict__)
    
    def get_location(self, method = 'bounding_box'):
        #print('getlocation')
        if method == 'bounding_box':
            x = self.bounding_box[0] + self.bounding_box[1]
            y = self.bounding_box[2] + self.bounding_box[3]


            #print('hv:', self.hv)
        elif method == 'answer_step':
            tool = coor_tool()
            x = tool.char2num( self.answer_step[0] )
            y = tool.char2num( self.answer_step[1] )

        d = {'lt': 0, 'rt': 1, 'ld':3, 'rd': 2}
        X = 'r' if y>18 else 'l'
        Y = 'd' if x>18 else 't'  
        print(self.bounding_box)
        #print(x,y)
        #print(X+Y)
        self.quadrant_value = d[X+Y]
        print('qv', self.quadrant_value)
        print(self.bounding_box)
        print(X+Y)
        d = {'horizontal': 0, 'vertical': 1}
        self.hv = 1 if abs(x-18) > abs(y-18) else 0
            




    def find_first_step(self):
        Bindex = re.search('[^AL]B\[', self.sgf_str).span()[0]
        Windex = re.search('[^AL]W\[', self.sgf_str).span()[0]
        if Bindex < Windex:
            return self.sgf_str[ Bindex+3 : Bindex+5] , 'b'
        else:
            return self.sgf_str[ Windex+3 : Windex+5] , 'w'

    def BW2str(self):
        #print( '解答中黑白各有幾手: ', len(self.section_B) , len(self.section_W))
        #若白先走, 則先取一個白. 其他按照黑先白後之順序
        result_sgf = ''
        flag_first_step = 0

        if abs( len(self.section_B) - len(self.section_W) ) > 1:
            print('BW 數量可能有問題')

        if self.firststep_color == 'w':
            flag_first_step = 1
        for i in range(  len(self.section_B) + len(self.section_W) ):
            if i % 2 == flag_first_step:
                result_sgf += ';B[' + self.section_B[ int(i/2) ] + ']'
            else:                
                result_sgf += ';W[' + self.section_W[ int(i/2) ] + ']'


        return result_sgf

    def make_info_dict(self,input_dict):
        A = input_dict.copy()
        #self.targetblock = 

        
        A['category'] = ''
        A['rawsgf'] = self.sgf_str
        A['origin_sgf'] = self.None_ABAW_SGF()
        A['winning_color'] = self.firststep_color
        A['target_block' ] = self.find_maxblock(datasource='mix') 
        A['date'] = datetime.date.today().__str__()
        A['answer_firstmove'] = self.answer_step
        A['ko_rule'] = ''
        A['mask_rule'] = ''
        A['additional_mask'] = ''
        A['search_goal'] = ''
        A['mask_filename'] = ''
        A['masked_sgf'] = ''
        A['mask'] = 'automask'


    def check_ABAWBW_error_occur(self): #if there are same coor => error
        for x in self.sections:
            for y in self.sections:
                if x == y :
                    break
                for a in x:
                    if a in y:
                        return 'INVALID'
        return 'OK'

    def gen_elf_script(self):
        elf_tool = coor_tool(mode='elf')
        elf_script = 'clear_board\n'
        for i in range( max(len(self.section_AB) , len(self.section_AW) ) ):
            try:
                elf_script += 'play b ' + sgfcc2elfcn(self.section_AB[i]) + '\n'
            except:
                elf_script += 'play b pass\n'
            try:
                elf_script += 'play w ' + sgfcc2elfcn(self.section_AW[i]) + '\n'
            except:
                elf_script += 'play w pass\n'
        flag_first_step = 0 
        if self.firststep_color == 'w':
            elf_script += 'play b pass\n'
            flag_first_step = 1
        for i in range(  len(self.section_B) + len(self.section_W) ):
            if i % 2 == flag_first_step:
                elf_script += 'play b ' + sgfcc2elfcn(self.section_B[ int(i/2) ]) + '\n'
            else:                
                elf_script += 'play w ' + sgfcc2elfcn(self.section_W[ int(i/2) ]) + '\n'   
        
        elf_script += 'genmove '+ self.firststep_color + '\n'
        return elf_script.replace('play b pass\nplay w pass\n','').replace('play w pass\nplay b pass\n','')
    

    def Is_boundingbox_overmiddleline(self):
        if( self.bounding_box[1] > 8 or self.bounding_box[3] > 8):
            return True
        return False

    def dynamic_mask(self,distance2wall = 2, box_width = 1):
        self.find_bounding_box(box_width+1)
        def mycmp( A,B, coor_fix = (18,0)):
            def Q(coor):
                return abs(coor_fix[0] - coor[0])+abs(coor_fix[1] - coor[1])
            if Q(A) == Q(B):
                return A[0] - B[0]
            else:
                return Q(A) - Q(B)
        # 1. given a bounding box
        # 2. bdbox裡面要全殺A)或活一塊B)
        #     A) bdbox 空 + 外圍的目 -/+ 貼目 > 184/178
        #     B) 外面的空 + bdbox中做活一小塊 -/+ 貼目 > 184/178


        if self.firststep_color == self.who_outside_color:
            self.goal = 'tokill'
        else:
            self.goal = 'tolive'
    
        #(1,9,0,8)
        #territory_in_bdbox = calculate_bdbox_territory( bdbox )
        bdbox = self.bounding_box

        print( 'indynamic', bdbox)

        tool = coor_tool()
        mask_outsidecolor = [tool.num2char(bdbox[3]-1)+tool.num2char(i) for i in range(bdbox[1]-1)]
        mask_outsidecolor.extend([ tool.num2char(j)+tool.num2char(bdbox[1]-1) for j in range(bdbox[3]-1)])
        mask_outsidecolor.append( tool.num2char(bdbox[3]-1)+tool.num2char(bdbox[1]-1) )
        


        if self.who_outside_color == 'b':
            self.section_AB = mask_outsidecolor + self.section_AB
        else:
            self.section_AW = mask_outsidecolor + self.section_AW
        
        #print(self.None_ABAW_SGF(nobw=True,check = False))

        coors = []
        for i in range(19):
            for j in range(19):
                if not self.inbox( (j,i)):
                    coors.append( (i,j) )
        
        coors.sort(key=cmp_to_key(mycmp))

        print(bdbox, len(coors))
        for eye in [ (15,0),(18,0),(0,15),(0,18)]:
            try:
                coors.remove(eye)
            except:
                print('eye not in list maybe error')

        if self.goal == 'tokill': #situation A
            if self.who_outside_color == 'b':
                self.section_AW = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[:174] ] + self.section_AW
                self.section_AB = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[174:] ] + self.section_AB
            elif self.who_outside_color == 'w':
                self.section_AB = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[:180] ] + self.section_AB
                self.section_AW = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[180:] ] + self.section_AW
        elif self.goal == 'tolive': #situation B 居然行為是一樣的????
            if self.who_outside_color == 'b':
                self.section_AW = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[:174] ] + self.section_AW
                self.section_AB = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[174:] ] + self.section_AB
            elif self.who_outside_color == 'w':
                self.section_AB = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[:180] ] + self.section_AB
                self.section_AW = [ tool.num2char(coor[0])+tool.num2char(coor[1]) for coor in coors[180:] ] + self.section_AW
        else:
            print('no set goal...')

        # for x in self.sections:
        #     print(len(x),x)
        self.section_B.clear()
        self.section_W.clear()
        return self.None_ABAW_SGF(nobw=True,check = False,target_flag=True,targetblock_flag=True)

    def None_ABAW_SGF(self,target_flag = False, nobw = False,targetblock_flag=False,check = True): #通常不會有 B ,W
        
        def ABAW2str(AB,AW, auto_balance_length = True):
            result_sgf = ''
            for i in range( max(len(AB) , len(AW) ) ):
                try:
                    result_sgf += ';B[' + AB[i] + ']'
                except:
                    result_sgf += ';B[]' if auto_balance_length else ''
                try:
                    result_sgf += ';W[' + AW[i] + ']'
                except:
                    result_sgf += ';W[]' if auto_balance_length else ''
            return result_sgf.replace(';B[];W[]','').replace(';W[];B[]','') #delete double pass
        
        if check and self.check_ABAWBW_error_occur() == 'INVALID':
            print('check_ABAWBW_error_occur ERROR')
            return None
        
        if target_flag:
            if self.firststep_color == self.who_outside_color:
                self.target = "TOKILL"
                self.target_first_color = "BLACK" if self.firststep_color == 'b' else "WHITE"
            else:
                self.target = "TOLIVE"
                self.target_first_color = "BLACK" if self.firststep_color == 'b' else "WHITE"
            
            if targetblock_flag:
                self.targetblock = self.find_maxblock(datasource='mix')
                print('targetblock',self.targetblock)
            else:
                self.targetblock = ''
            
            result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'+"TARGET[{},{},{}]".format(self.target,self.target_first_color,self.targetblock) #+  'MA[{}]'.format(self.targetblock)
        else:
            result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'
        print(result_sgf)

        if nobw: 
            #oldmask通常不會有 B ,W
            #黑先就代表 len(AB) == len(AW)
            #白先就代表 len(AB)+1 == len(AW)
            temp_AW =self.section_AW.copy() 
            temp_AB =self.section_AB.copy() 
            fix = abs(len(self.section_AB) - len(self.section_AW))
            print("before",fix , len(self.section_AB) , len(self.section_AW), self.firststep_color)
            if( len(self.section_AB) > len(self.section_AW) ):
                if( self.firststep_color == 'w'):
                    fix -= 1
                temp_AW =  [''] * fix + self.section_AW.copy() 
            else:
                if( self.firststep_color == 'w'):
                    fix += 1
                temp_AB = [''] * fix + self.section_AB.copy()

            print( "after",len(temp_AB),len(temp_AW) )      
            result_sgf += ABAW2str(temp_AB,temp_AW,auto_balance_length = False)
        else:
            result_sgf += ABAW2str(self.section_AB,self.section_AW)
            if self.firststep_color == 'w':
                result_sgf += ';B[]'
            result_sgf += self.BW2str()
        
        result_sgf += ')'
        return result_sgf


    def output(self, truncate_solution = False ):
        result_sgf = '(;CA[UTF-8]GM[1]AP[StoneBase:SGFParser.3.0]SZ[19]HA[0]'
        result_sgf += 'AB'
        for x in self.section_AB:
            result_sgf += '[' + x + ']'
        result_sgf += 'AW'
        for x in self.section_AW:
            result_sgf += '[' + x + ']'
        if not truncate_solution and self.firststep_color != 'None':
            result_sgf += '(' + self.BW2str() + ')'
        
        result_sgf += ')'
        return result_sgf

    def find_bounding_box(self, box_width = 0): 
        '''
        AB[aa][bb][cc][ak] => (0,10,0,2)
        '''
        pnts = []

        for x in self.coors:
            pnts.extend(x)

        xs = [pnt[0] for pnt in pnts]
        ys = [pnt[1] for pnt in pnts]
        xs.sort()
        ys.sort()

        
        #self.bounding_box =  (-1,xs[-1]+box_width, -1,ys[-1]+box_width)
        self.bounding_box =  (xs[0],xs[-1], ys[0],ys[-1]) 

    def who_outside(self):

        def distance2center(coor):
            return (coor[0]-9)**2+(coor[1]-9)**2
        if len(self.coor_AB) == 0:
            self.who_outside_color ='b'
            return 
        distances = []
        for coor in self.coor_AB:
            distances.append( (distance2center(coor) , 'b',coor) )
        for coor in self.coor_AW:
            distances.append( (distance2center(coor) , 'w',coor) )
        distances.sort(key=lambda x:x[0])

        #print('distance:' ,distances)


        self.who_outside_color = distances[0][1]

    def minus(self, bounding_box, padding = 2):
        # 刪除bounding_box內中的所有的點
        AB = []
        AW = []
        A = list(bounding_box)
        A[1] += padding
        A[3] += padding
        self.bounding_box = A

        for i , coor in enumerate( self.coor_AB , 0) :
            if not self.inbox( coor):
                AB.append( self.section_AB[i] )
        for i , coor in enumerate( self.coor_AW , 0) :
            if not self.inbox( coor):
                AW.append( self.section_AW[i] )

        # 不應該刪掉有落子的部分
        Q = self.coor_B.copy()
        Q.extend(self.coor_W)
        for coor in Q :
            if self.inbox( coor):
                print('Error!!!', coor, bounding_box)

        return AB, AW,self.section_B,self.section_W


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
        diffusion_interval = [-1,0,1]
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if i==0 and j == 0:
                    continue
                r.append( alphabet[ alpha_dict[s[0]] + i ] + alphabet[ alpha_dict[s[1]]+ j ] )
        return r
    def DFS(ABW,BW):
        result = set()
        f = []
        sABW = set(ABW)
        sBW = set(BW)
        while len(sBW)!=0:
            Q = []
            while len(sBW)!=0:
                Q.extend( diffusion(sBW.pop() ) )
            S = set(Q)

            sBW = (sABW & S)
            sABW = sABW - sBW
        return sABW

    AB = re.search('AB(\[..\])*', s).group(0)
    AW = re.search('AW(\[..\])*', s).group(0)
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

    r = DFS(ABW,BW)

    while len(r) !=0:
        Q = r.pop()
        Z = re.search( Q, s).group(0)
        s = s.replace( '['+Z+']' , '')
    return s




def union(problem,mask):
    # A 為題目
    # mask 為 mask , mask content 手順
    print('mask', len(mask.section_AB), len(mask.section_AW), len(mask.section_B), len(mask.section_W))
    AB,AW, _, _ = mask.minus(problem.bounding_box)
    B,W  = mask.section_B , mask.section_W
    print('problem bounding', problem.bounding_box)
    print(len(AB), len(AW), len(B), len(W))
    AB.extend(problem.section_AB)
    AW.extend(problem.section_AW)
    R = sgfstr_tool('')
    #R.show()
    R.init_by_AWABBW(AB,AW,B,W, mask.firststep_color)
    
    return R

def generate_isomorphism(n = 19): 
    
    A = np.array(range(n*n)).reshape(n,n)
    map_coor2num = dict()
    map_num2coor = dict()
    c = 0
    tool = coor_tool('sgf')
    for p in tool.alphabet:
        for q in tool.alphabet:
            map_coor2num[p+q] = c
            map_num2coor[c] = p+q
            c += 1
    maps = []
  
    for t in range(2):
        for r in range(4):
            map = dict()
            for p in tool.alphabet:
                for q in tool.alphabet:
                    map[ p + q ] = map_num2coor[ A[ tool.char2num(p)  ][ tool.char2num(q) ] ]
            maps.append(map)

            A = np.rot90(A)
        A = A.T
    return maps

def spin( sgfstr , map):
    result = []
    m = map
    Q = sgfstr
    for x in parse_coor(Q):
        Q = Q.replace('['+x+']', '[@@@@'+m[x]+'@@@@]')
    Q = Q.replace('[@@@@', '[').replace('@@@@]',']')
    return Q


def swap_color_in_sgfstr(sgf_str):
    return sgf_str.replace('AB','ZZZ').replace('AW', 'AB').replace('ZZZ','AW').replace(';B[', '$$$').replace(';W[',';B[').replace('$$$',';W[')

def sgfs2strs(path):
    sgf_filenames = []
    for filename in os.listdir(path):
        if 'sgf' not in filename:
            continue
        sgf_filenames.append( filename )
    
    sgf_strs = []
    for filename in sgf_filenames:
        sgf_strs.append( sgf2str(os.path.join(path,filename)) )
    return sgf_strs, os.listdir(path)

def sgf2str(fpath):
    with open(fpath, 'r', encoding = 'UTF-8') as f:
        sgf = f.read()
        f.close()
    return sgf

def parse_coor(sgf_str):
    coor = re.findall('(\[..\])', sgf_str)
    tool = coor_tool()
    r = []
    for x in coor:
        if x[1] in tool.alphabet and x[2] in tool.alphabet:
            r.append(x[1:3])
    return r

def str2sgf(fpath, sgf_str):

    with open(fpath , 'w', encoding='UTF-8') as f:
        f.write(sgf_str)
        f.close()



import pickle
def save(fname,var):
    f = open(fname, 'wb')
    pickle.dump(var, f)
    f.close()

def load(fname):
    f = open(fname, 'rb')
    var = pickle.load(f)
    f.close()
    return var

def negative(color):
    if color == 'b':
        return 'w'
    return 'b'




def branch_str(color,coor,comment=None):
    if comment == None:
        return '(;' +  color + '[' + coor +']'+ ')'
    else:
        return '(;' +  color + '[' + coor +']'+ 'C[' + comment +']' + ')'

def savecsv(path, book_answers):
    # labelnames = ['ProblemSgfFilename','BestMove']
    # for lbn in labelnames:
    #     content+=  lbn + ','
    # content += '\n'
    with open(path, 'w') as f:
        content =''
        for x in enumerate(book_answers):
            content += str(x[1][0])+','+str(x[1][2])+','+str(x[1][1])+'\n'
        f.write(content)
        f.close()
    

def gen_askcgi_script(book_answers,  script_file_path = '.' , gtp_input_file = '',book_answers_path= 'output', script_file = 'ask_cgi_{}.sh' , result_file = 'myresult.txt', experiment_name = 'default'):
    if experiment_name == 'default':    
        experiment_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    before = '''
A=time_`date "+%Y%m%d%H%M%S"`.txt
date "+%Y%m%d%H%M%S" >> $A
BOARD_SIZE=19
RADIUS_PATTERN_MODE_NUMBER=1
input_radius_pattern=.$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c 8).QQ
'''

    middle = '''echo \"loadsgf \"{sgf_filename} >> $input_radius_pattern \
#echo \"play \"{negative_color}\" pass\" >> $input_radius_pattern \
#echo \"dcnn_move_order\" >> $input_radius_pattern \
echo \"genmove \"{color} >> $input_radius_pattern'''
#     middle = '''\necho \"loadsgf \"{sgf_filename} >> $input_radius_pattern \
# \n#echo \"play \"{negative_color}\" pass\" >> $input_radius_pattern \
# \n#echo \"dcnn_move_order\" >> $input_radius_pattern \
# \necho \"genmove \"{color} >> $input_radius_pattern'''
    after = '''Release/CGI -conf_file cgi_play_g0_opp.cfg < {} | tee {}  
date "+%Y%m%d%H%M%S" >> $A\n
python3 /mnt/nfs_share/yshsu0918/Smail.py {} $A\n
rm $A\n
'''.format(gtp_input_file,'result_'+experiment_name+'.txt',experiment_name+'_complete')
    
    middle_content=''
    # for ans in book_answers:
    #     sgf_abs_path = os.path.join( book_answers_path ,ans[0] ).replace('\\','/')

    #     middle_content += middle.format(sgf_filename = sgf_abs_path, negative_color = negative(ans[2]) ,color = ans[2]) 
         
    outfile = open( os.path.join( script_file_path, script_file.format(experiment_name) ) , 'w')
    outfile.write(before+ '\n'+middle_content+'\n'+after)
    outfile.close()

    save( os.path.join(book_answers_path, 'book_answers.pickle'), book_answers)
    savecsv(os.path.join(book_answers_path, 'book_answers.csv'),book_answers)

def gen_askelf_script(elfs,script_file_path = '.', gtp_input_file = 'elfinput.txt'):
    outfile = open(os.path.join( script_file_path, gtp_input_file) , 'w')
    for x in elfs:
        #print(x)
        outfile.write(x)    
    outfile.write('quit\n')
    outfile.close()    

    