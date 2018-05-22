from setuptools import find_packages, setup

setup(
    name='waitGPU',
    version='0.0.3',
    description="A small Python library that waits for GPU conditions to be satisfied, and then setting `CUDA_VISIBLE_DEVICES` to the qualifying GPU on multi-GPU systems.",
    author='Eric Wong',
    author_email='ericwong@cs.cmu.edu',
    platforms=['any'],
    license="Public Domain",
    url='https://github.com/riceric22/waitGPU',
    py_modules=['waitGPU'],
    install_requires=[
        'gpustat'
    ]
)
