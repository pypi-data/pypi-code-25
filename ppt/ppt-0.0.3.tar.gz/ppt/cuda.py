#!/usr/bin/env python3

import os


def block_cuda():
    os.environ['CUDA_LAUNCH_BLOCK'] = '1'


def noblock_cuda():
    os.environ['CUDA_LAUNCH_BLOCK'] = '0'
