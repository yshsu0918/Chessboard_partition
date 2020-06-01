import sys
import argparse
import os

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

def elfcc2sgfcc(charchar):
    if len(charchar) != 2:
        return charchar
    #print('cur', charchar)
    A = coor_tool(mode='sgf')
    return charchar[0] + A.num2char( 18 - A.char2num(charchar[1]) )
    

def parse_move_changeorder(lines): #split with samox0918 debugger
    last_count = ''
    last_coor = ''
    content_charchar = ''
    content_charnum = ''
    #print(lines)
    for line in lines:
        line_ = line.replace('[', '').replace(']',':').split(':')
        if len(line_) != 6:
            continue
        count = line_[0]
        coor_charchar= line_[1]
        coor_charnum = line_[2]

        if last_coor != coor_charchar:
            content_charchar += "({}:{}):".format(count, elfcc2sgfcc(coor_charchar) )
            content_charnum+= "({}:{}):".format(count, coor_charnum )
            last_coor = coor_charchar
            #print(content_charchar)
            #print(content_charnum)

    
    return content_charchar, content_charnum



def split_file(fname):
    offset = len('SAMOX0918_data|(')
    lines = []
    print(fname)
    with open(fname, 'r') as f:
        for line in f.readlines():
            #print(line)
            if 'samox0918 debuger' in line:
                return parse_move_changeorder(lines)
            elif 'SAMOX0918_data' in line:
                lines.append( line[offset:-2] )
    return False, False
if __name__ == "__main__":
    info = '''
    Parse \"special\" ELF output file. 
    ex. 
    SAMOX0918_data|(65:[C15][co][318]:0.704676)
    ...
    SAMOX0918_data|(194415:[A11][ak][232]:0.764189)
    samox0918 debuger: this msg should only show once.
    '''

    parser = argparse.ArgumentParser(description=info)
    parser.add_argument("--src", help="src folder")
    # parser.add_argument("--dest", help="output folder")
    
    args = parser.parse_args()

    # if not os.path.isdir(args.dest):
    #     os.mkdir(args.dest)
    
    for f in os.listdir(args.src):
        print(f)
        
        content_charchar, content_charnum = split_file(os.path.join(args.src,f))
        #if content_charchar and content_charnum:
        print(content_charchar)
        print(content_charnum)
        #else:
        #    print('sth error')
            