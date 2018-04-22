from random import randint


def colored_message(message):
    return '\033[0;{};01m{message}\033[0m'.format(randint(30, 37), message=message)
    
class CV:
    def __str__(self):
        return '田岩的简历'

    def show(self):
        print(colored_message('基本信息:'))
        for k, v in self.basic:
            print('\t{}: {}'.format(k.ljust(12), v))

        print(colored_message('毕业学校:'))
        for k, v in self.collage:
            print('\t{}: {}'.format(k.ljust(12), v))

        print(colored_message('工作经历:'))
        for index, career in enumerate(self.career):
            print(colored_message('\t[{}]:'.format(index + 1)))
            for k, v in career:
                print('\t{}: {}'.format(k.ljust(12), v))

        print(colored_message('项目经历:'))
        for index, project in enumerate(self.projects):
            print(colored_message('\t[{}]:'.format(index + 1)))
            for k, v in project:
                print('\t{}: {}'.format(k.ljust(12), v))

        print(colored_message('个人技能:'))
        for index, skill in enumerate(self.skills):
            print(colored_message('\t[{}]:'.format(index + 1)))
            for k, v in skill:
                print('\t{}: {}'.format(k.ljust(12), v))

    @property
    def basic(self):
        return [('name', '田岩'),
                ('sex', '男'),
                ('birthday', '1997'),
                ('phone', 'echo MTgwOTI2NyoqKiogDQo= | base64 -d'),
                ('email', 'mtianyan@qq.com'),
                ('address', '陕西西安'),
                ('github', 'https://github.com/mtianyan'),
                ('blog', 'http://blog.mtianyan.cn')]

    @property
    def collage(self):
        return [('school', '云南大学'),
                ('degree', '本科'),
                ('period', '2014.09 - 2018.06'),
                ('major', '软件工程')]

    @property
    def career(self):
        return [(('company', '家里蹲有限公司'),
                 ('period', '一直 - 至今'),
                 ('position', 'Python瞎折腾工程师'),
                 ('duty', '网站开发, 文档编写, 爬虫瞎爬,服务器运维'))]

    @property
    def projects(self):
        return [(('name', 'mtianyan慕课小站'),
                 ('description', ('Django2.0 + Mysql + xadmin')),
                 ('duty', '后端开发'),
                 ('url', 'http://mxonline.mtianyan.cn')),
                (('name', 'mtianyan搜索'),
                 ('description', ('Django + ELasticSearch + Scrapy')),
                 ('duty', '爬虫 + 搜索程序员'),
                 ('url', 'http://search.mtianyan.cn')),
                (('name', '弹幕电影'),
                 ('description', 'Flask开发的弹幕电影网站'),
                 ('duty', '后端开发'),
                 ('url', 'http://movie.mtianyan.cn')),
                (('name', 'vueshop生鲜超市'),
                 ('description', 'vue + Django restframework + xadmin'),
                 ('duty', '后端开发'),
                 ('url', 'http://vueshop.mtianyan.cn/index'))]

    @property
    def skills(self):
        return [(('name', '后端开发'),
                 ('description', '利用Python相关技术快速完成后端开发, 部署')),
                (('name', '网络爬虫'),
                 ('description', '利用Python相关技术快速完成网络爬虫编写')),
                (('name', '系统运维'),
                 ('description', '掌握Linux相关环境部署运维技能')),
                (('name', '机器学习 & 深度学习'),
                 ('description', '正在努力学习'))]


cv = CV()
cv.show()