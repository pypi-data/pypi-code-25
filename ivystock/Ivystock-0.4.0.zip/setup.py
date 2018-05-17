from distutils.core import setup  
  
PACKAGE = "Ivystock"  
NAME = "Ivystock"  
DESCRIPTION = "This package can very easily and friendly download China market and USA market and any stock data from yahoo HK and future data from Sina, then analyze the data."  
AUTHOR = "Shuangxi Zhang"  
AUTHOR_EMAIL = "shuangxipop@163.com"  
URL = "https://github.com/Sandychuang/Ivystock"  
VERSION = "0.4.0"  
long_description = '''
* Ivystock
Ivystock

* Installation
pip install Ivystock

* Help
    Hongkong
    code='0336.HK'
    Shenzhen
    code='000969.SZ'
    Shanghai
    code='600011.SS'
    Shangzheng Index
    code='000001.SS'
    HK index
    code='^HSI'
    USA stock
    code='AAPL'
    
* Sample    
    
    from ivystock import ivystock as ivy

    if __name__ == '__main__':
        code = '0336.HK'
        stock = ivy.Ivystock()
       # SS.begin = SS.datetime_timestamp("2018-1-1 09:00:00")
        #stock.help()
        #stock.get(code)
        #stock.plot(code)

     #   hl50 = r"http://www.csindex.com.cn/uploads/file/autofile/cons/000015cons.xls"
       # hs300 = r"http://www.csindex.com.cn/uploads/file/autofile/closeweight/000300closeweight.xls"

        #aa = stock.get_code(hs300)
        
        #dd = stock.get_code('hl50')
        #stock.get_list(dd)
        #stock.preprocess(dd,['Date','Close'])

        #futurelist = ['TA0','RS0','RM0']
        code = 'A0'
        #stock.get_future(futurelist)
        tick = stock.get_dick(code, '5m')
        tick1m = stock.get_1m(code)
   '''
  
setup(  
    name=NAME,  
    version=VERSION,  
    description=DESCRIPTION,  
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author=AUTHOR,  
    author_email=AUTHOR_EMAIL,  
    license="MIT License",  
    url=URL,  
    packages=["ivystock"],  
    install_requires = [],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
     'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    ]
)