from setuptools import setup, find_packages

setup(
    name='easyPyMySQL',  # 名称
    version='1.3',  # 版本
    description="简单易用的数据库ORM模块",
    keywords='mysql orm',
    author='akiyamaryou',  # 作者
    author_email='crh51306@gmail.com',  # 作者邮箱
    url='https://github.com/AkiYama-Ryou',  # 作者链接
    packages=find_packages(exclude=['easyPyMySQL']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[  # 需求的第三方模块
        'pymysql',
    ],
)



