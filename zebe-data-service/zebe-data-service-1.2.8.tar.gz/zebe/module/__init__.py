import os

# 根据操作系统的类型，设置不同的路径前缀
prefix = ''
if os.name == 'posix':  # Mac
    prefix = '/usr/zebe/'
elif os.name == 'linux':  # Linux
    prefix = '/home/data/'
elif os.name == 'nt':  # Windows
    prefix = 'D:/sqlite/'

# 组成完整路径
WECHAT_DB_FILE_PATH = prefix + 'zebe-wechat.sqlite'
PROJECT_DB_FILE_PATH = prefix + 'zebe-project.sqlite'
MEMCARD_DB_FILE_PATH = prefix + 'zebe-memcard.sqlite'
CDRVBA_DB_FILE_PATH = prefix + 'zebe-cdrvba.sqlite'
REMIND_DB_FILE_PATH = prefix + 'zebe-remind.sqlite'
BLOG_DB_FILE_PATH = prefix + 'zebe-blog.sqlite'
DIARY_DB_FILE_PATH = prefix + 'zebe-diary.sqlite'
AD_DB_FILE_PATH = prefix + 'zebe-ad.sqlite'
APP_DB_FILE_PATH = prefix + 'zebe-app.sqlite'

