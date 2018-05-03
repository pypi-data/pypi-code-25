from setuptools import (
    setup,
)

setup(
    name="multiJump",
    version = "0.0.4",
    author="seqyuan",
    author_email='seqyuan@gmail.com',
    url="https://github.com/seqyuan/multiJump/wiki",
    download_url = "https://codeload.github.com/seqyuan/multiJump/zip/master",
    description="multiple Jump IP do something",
    long_description="""Mid Jump IP rum cmd and Jump to End IP rum cmd""",
    license="MIT",
    packages=['multiJump'],
    extras_require = {
        'sys' : [ 'sys'],
        'paramiko' : ['paramiko'],
        'socket' : ['socket'],
        'time' : ['time'],
    }
)
