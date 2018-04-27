# -*- coding: utf8 -*-
from setuptools import setup, find_packages
from spycmdbsdkcore import __version__
setup(
      name='spycmdbsdkcore',   #名称
      version=__version__,  #版本
      description="spy cmdb api sdk core", #描述
      keywords='python english translation dictionary terminal',
      author='feeir',  #作者
      author_email='54587841@qq.com', #作者邮箱
      url='https://github.com/feeir', #作者链接
      packages=find_packages(),
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