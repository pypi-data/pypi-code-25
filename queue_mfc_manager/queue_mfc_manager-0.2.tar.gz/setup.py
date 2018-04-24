from setuptools import setup, find_packages


setup(
    name='queue_mfc_manager',
    description='Simple queue manager for me and you!',
    author='Sergey Gavrilov',
    version='0.2',
    url='https://github.com/seregagavrilov/queue_mfc_manager',
    packages=find_packages(),
    include_package_data=True,
    author_email='sergeigavrilov123@gmail.com',
    py_modules=['workers'],
    license='MIT',
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        workers=workers.workers:start_workers
    ''',
)