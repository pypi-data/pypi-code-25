#coding:utf-8
from setuptools import setup, find_packages  
  
setup(  
      name='jiangwei_test',   #名称  
      version='0.20',  #版本  
      description="a console translation dictionary used dict.baidu.com Api", #描述  
      keywords='python english translation dictionary terminal',  
      author='蒋为',  #作者  
      author_email='ok@xjiangwei.cn', #作者邮箱  
      url='http://www.xjiangwei.cn', #作者链接  
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),  
      include_package_data=True,  
      zip_safe=False,  
      install_requires=[      #需求的第三方模块  
        'requests',  
      ],  
      entry_points={  
        'console_scripts':[     #如果你想要以Linux命令的形式使用  
            'bword = bword.bword:main'      
        ]  
      },  
)  