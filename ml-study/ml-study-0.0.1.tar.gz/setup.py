from setuptools import setup, find_packages

setup(
    name='ml-study',
    version='0.0.1',
    description='python machine learning structure architecture',
    url='https://github.com/LucianoPC/ml-study',
    author='Luciano Prestes Cavalcanti',
    author_email='lucianopcbr@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'click', 'jupyter', 'matplotlib', 'numpy', 'openpyxl', 'pandas',
        'pytest', 'requests', 'scikit-learn', 'scipy', 'seaborn', 'watermark',
    ],
    python_requires='>=3',
    entry_points={
        'console_scripts':[
            'ml-study = src.cli:main',
        ],
    },
)
