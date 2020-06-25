#!/usr/bin/python3
# Author: ifact

'''使用方法
0. 需要安装 Python 3.6 或以上版本来使用此脚本
1. 在设置（Settings）中设置需要的更改
  1.5. 运行前请做好备份，防止错误操作导致文件重命名错误
2. 双击运行脚本（Windows），或从命令行进入脚本所在目录运行脚本（Mac/Linux）
3. 输入要整理文件名格式的文件夹路径（不输入默认脚本所在路径）
4. 等待完成提示，按回车退出脚本
'''

################### Settings ####################

rename_filetypes = {'jpg', 'png'}   # 要整理命名格式的文件后缀名
rename_folder = True                # 是否将命名格式用于文件夹
delete_prefix = ['cgaxis_pbr_14']   # 要删除的原来文件的前缀
delete_postfix = []                 # 要删除的原来文件的后缀
prefix = 'T'                        # 新的文件前缀（不会作用于文件夹）
suffix_trans_dict = {               # 后缀转换表
    'diffuse'       : 'D',
    'glossiness'    : 'S',
    'height'        : 'H',
    'normal'        : 'N',
    'reflection'    : 'Evil_R',
}
origin_spliter = [' ', '_']         # 原文件和文件夹名称使用的分割符

#################################################

import re
import sys
import os
from typing import List

delete_prefix_pattern = None
delete_postfix_pattern = None
origin_spliter_pattern = None
trim_front_pattern = None
trim_back_pattern = None

class Name:
    '''Name of file or folder'''
    
    def __init__(self, name : str, is_file : bool):
        '''Create a file name
        :param name: name of the file
        '''
        self.is_file = is_file
        self.body = None
        self.suffix = None
        self.ext = None
        if (is_file):
            parts = name.rsplit('.', 1)
            if len(parts) != 2 or not parts[0] or not parts[1]:
                raise NameError(f'Invalid file name: \'{name}\'' )
            self.ext = parts[1]
            for key in suffix_trans_dict.keys():
                if parts[0].endswith(key):
                    self.body = parts[0][:-len(key)]
                    self.suffix = key
                    break
            if not self.suffix:
                self.body = parts[0]
        else:
            self.body = name
            
        self.__prepare()

    def __prepare(self):
        '''Delete prefixes and postfixes'''
        self.trim()
        if delete_prefix_pattern:
            self.body = re.sub(delete_prefix_pattern, '', self.body)
        if delete_postfix_pattern:
            self.body = re.sub(delete_postfix_pattern, '', self.body)
        self.trim()
        
    def trim(self):
        self.body = re.sub(trim_front_pattern, '', self.body)
        self.body = re.sub(trim_back_pattern, '', self.body)
        
    def to_pascal(self):
        words = re.split(origin_spliter_pattern, self.body)
        self.body = ''
        for word in words:
            if word:
                self.body += word[0].upper()
                if len(word) > 1:
                    self.body += word[1:]
    
    def translate_suffix(self):
        if (self.suffix):
            try:
                self.suffix = suffix_trans_dict[self.suffix]
            except KeyError:
                raise Exception('Don\'t translate twice!')
            return True
        else:
            return False
    
    def __str__(self):
        result = self.body
        if self.is_file:
            result = prefix + '_' + result
            if self.suffix:
                result += '_' + self.suffix
            result += '.' + self.ext
        return result
    
    def __repr__(self):
        return self.__str__()
    
    def __radd__(self, string : str):
        return string + str(self)
    
    def __add__(self, string : str):
        return str(self) + string
        
def build_or_pattern(strings : List[str]) -> str:
    pattern = r''
    for string in strings:
        pattern += re.escape(string) + r'|'
        
    return r'(?:' + pattern[: -1] + r')'

def init():
    global delete_prefix_pattern
    global delete_postfix_pattern
    global origin_spliter_pattern
    global trim_front_pattern
    global trim_back_pattern
    if (delete_prefix):
        delete_prefix_pattern = re.compile(build_or_pattern(delete_prefix))
    if (delete_postfix):
        delete_postfix_pattern = re.compile(build_or_pattern(delete_postfix))
    if (origin_spliter):
        origin_spliter_string = build_or_pattern(origin_spliter)
        origin_spliter_pattern = re.compile(origin_spliter_string)
        trim_front_pattern = re.compile(r'^' + origin_spliter_string + r'+')
        trim_back_pattern = re.compile(origin_spliter_string + r'+$')
    else:
        raise Exception()
    
def rename(abspath : str):
    for item in os.listdir(abspath):
        path = os.path.join(abspath, item)
        if os.path.isfile(path):
            name = Name(item, True)
            if not rename_filetypes.isdisjoint({name.ext}):
                name.to_pascal()
                name.translate_suffix()
                os.rename(path, os.path.join(abspath, str(name)))
            
        elif os.path.isdir(path):
            rename(path)
            if rename_folder:
                name = Name(item, False)
                name.to_pascal()
                os.rename(path, os.path.join(abspath, str(name)))
    
def test():
    names = [
        Name('beige_tiles_2.jpg', True),
        Name('cgaxis_pbr_14_beige_fabric_1_diffuse.jpg', True),
        Name('beige_tiles_2', False),
        Name('bad folder name', False)
    ]
    for name in names:
        print(name)
        name.to_pascal()
        name.translate_suffix()
        print('>> ' + name + '\n')
    
if __name__ == "__main__":
    init()
    abs_path = os.path.abspath(sys.argv[0])
    script_dir = os.path.dirname(abs_path)
    os.chdir(script_dir)
    
    print('Current path:\n    ' + os.path.realpath(os.getcwd()) + '\n')
    path = os.path.realpath(os.path.abspath(input('Path to rename files (Default: current path):\n')))
    
    rename(path)
    input('Finish! Press enter to exit.')