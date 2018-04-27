#!/usr/bin/env python
# created by BBruceyuan on 18-4-27

import pathlib

pic_name = {
    'default': 'monster.txt',
    'monster': 'monster.txt',
    'buddist': 'buddist.txt',
    'god': 'jesus.txt',
    'jesus': 'jesus.txt'
}


class CommentWrite:

    def __init__(self, target_files, pic='default'):
        # if you want to add new text pic, you should add a item in the dict pic_name
        # 如果后面想增加新的文本无图片，需要在pic_name中添加新的项
        self.pic = pic_name[pic]
        # this is a target file list
        self.target_files = target_files

    def write_comment(self):
        content = self.get_comment()
        for i in self.target_files:
            if i.endswith('/'):
                # if it's a dir
                p = pathlib.Path(i)
                for x in p.iterdir():
                    # print(x)
                    self._write_comment_to_file(content, str(x))
            else:
                self._write_comment_to_file(content, i)

    @staticmethod
    def _write_comment_to_file(content, target):
        with open(target, 'r+') as f:
            f.seek(0, 0)
            a = f.readline()
            if a.startswith('#!'):
                tmp = f.read()
                f.seek(len(a))
                for item in content:
                    f.write('#{}'.format(item))
                f.write('#\n')
                f.write(tmp)
            else:
                f.seek(0)
                tmp = f.read()
                f.seek(0)
                for item in content:
                    f.write('#{}'.format(item))
                f.write('#\n')
                f.write(tmp)

    def get_comment(self):
        """
        Get what we need, the picture with text format which we wanna write in our python file
        :return: The content of the pic, it's a list
        """
        # 这里不知道为啥一定不能写 ../text_pictures/
        parent_path = pathlib.Path('text_pictures/')
        target_path = parent_path / self.pic
        with target_path.open('r') as f:
            tmp = f.readlines()
        return tmp
