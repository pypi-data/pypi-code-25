from setuptools import setup, find_packages

setup(
    name='qy_cli',  # 名称
    version='0.88',  # 版本
    description="a cli for qingyun",  # 描述
    keywords='python english translation dictionary terminal',
    author='tj',  # 作者
    author_email='tj@gmail.com',  # 作者邮箱
    url='https://github.com/',  # 作者链接
    # packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[  # 需求的第三方模块
        'requests',
    ],
    entry_points={
        'console_scripts': [  # 如果你想要以Linux命令的形式使用
            'qy_cli = cli.agrparse_cli:test'
        ]
    },
)