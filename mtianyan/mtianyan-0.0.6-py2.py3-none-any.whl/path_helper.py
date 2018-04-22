import os
def path_file_existed_or_create(path_or_file=[]):
    """
    目录或文件是否存在，不存在就创建。
    传入参数为列表
    """
    # 创建目录
    if len(path_or_file) == 0:
        pass
    for path_or_file in path_or_file:
        if str(path_or_file)[-1] == "/" or str(path_or_file)[-1] == "\\":
            # 这是个目录
            if not os.path.exists(path_or_file):
                os.makedirs(path_or_file)
                # os.chmod(path_or_file, "rw")
        else:
            # 这是个文件
            if not os.path.exists(path_or_file):
                f = open(path_or_file,'w')
                f.close()

if __name__ == '__main__':
    assert_path_files = ['./video/',
                        './picture/color/',
                        './picture/gray/',
                        './picture/color/mtianyan.txt',
                        ]
    path_file_existed_or_create(assert_path_files)