##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Created by: Hang Zhang
## ECE Department, Rutgers University
## Email: zhang.hang@rutgers.edu
## Copyright (c) 2017
##
## This source code is licensed under the MIT-style license found in the
## LICENSE file in the root directory of this source tree
##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""Synchronized Cross-GPU Batch Normalization functions"""
import torch
from torch.autograd import Function
from .._ext import encoding_lib

__all__ = ['sum_square', 'batchnorm']

def sum_square(input):
    r"""Calculate sum of elements and sum of squares for Batch Normalization"""
    return _sum_square.apply(input)


def batchnorm(*inputs, **kwargs):
    r"""Applies Batch Normalization over a 3d input that is seen as a
    mini-batch.

    .. math::

        y = \frac{x - \mu[x]}{ \sqrt{var[x] + \epsilon}} * \gamma + \beta

    Shape:
        - Input: :math:`(N, C)` or :math:`(N, C, L)`
        - Output: :math:`(N, C)` or :math:`(N, C, L)` (same shape as input)

    """
    return _batchnorm.apply(*inputs, **kwargs)


class _sum_square(Function):
    @staticmethod
    def forward(ctx, input):
        ctx.save_for_backward(input)
        C = input.size(1)
        with torch.cuda.device_of(input):
            xsum = input.new().resize_(C).zero_()
            xsquare = input.new().resize_(C).zero_()
        if isinstance(input, torch.cuda.FloatTensor):
            with torch.cuda.device_of(input):
                encoding_lib.Encoding_Float_sum_square_Forward(
                    input, xsum, xsquare)
        elif isinstance(input, torch.cuda.DoubleTensor):
            with torch.cuda.device_of(input):
                encoding_lib.Encoding_Double_sum_square_Forward(
                    input, xsum, xsquare)
        else:
            raise RuntimeError('Unimplemented data type!', type(input))
        return xsum, xsquare

    @staticmethod
    def backward(ctx, gradSum, gradSquare):
        input, = ctx.saved_variables
        with torch.cuda.device_of(input.data):
            gradInput = input.data.new().resize_as_(input).zero_()
        if isinstance(input.data, torch.cuda.FloatTensor):
            with torch.cuda.device_of(input.data):
                encoding_lib.Encoding_Float_sum_square_Backward(
                    gradInput.data, input.data, gradSum.data, gradSquare.data)
        elif isinstance(input.data, torch.cuda.DoubleTensor):
            with torch.cuda.device_of(input.data):
                encoding_lib.Encoding_Double_sum_square_Backward(
                    gradInput.data, input.data, gradSum.data, gradSquare.data)
        else:
            raise RuntimeError('Unimplemented data type!')
        return gradInput


class _batchnorm(Function):
    @staticmethod
    def forward(ctx, input, xsum, xsqsum, gamma, beta,
                runningMean, runningVar, N, momentum, eps, training):
        ctx.save_for_backward(input, xsum, xsqsum, gamma, beta)
        ctx.N = N
        ctx.eps = eps
        ctx.training = training
        assert(input.dim() == 3)
        with torch.cuda.device_of(input):
            output = input.new().resize_as_(input)
        if isinstance(input, torch.cuda.FloatTensor):
            with torch.cuda.device_of(input):
                encoding_lib.Encoding_Float_batchnorm_Forward(output, \
                    input, xsum, xsqsum, gamma, beta,
                    runningMean, runningVar, N, momentum, eps, training)
        elif isinstance(input, torch.cuda.DoubleTensor):
            with torch.cuda.device_of(input):
                encoding_lib.Encoding_Double_batchnorm_Forward(output, \
                    input, xsum, xsqsum, gamma, beta,
                    runningMean, runningVar, N, momentum, eps, training)
        else:
            raise RuntimeError('Unimplemented data type!')
        return output

    @staticmethod
    def backward(ctx, gradOutput):
        input, xsum, xsqsum, gamma, beta = ctx.saved_variables
        assert ctx.training
        with torch.cuda.device_of(input.data):
            gradInput = gradOutput.data.new().resize_as_(input).zero_()
            gradGamma = gradOutput.data.new().resize_as_(gamma).zero_()
            gradBeta = gradOutput.data.new().resize_as_(beta).zero_()
            gradXsum = gradOutput.data.new().resize_as_(xsum).zero_()
            gradXsqsum = gradOutput.data.new().resize_as_(xsqsum).zero_()

        if isinstance(input, torch.cuda.FloatTensor):
            with torch.cuda.device_of(input.data):
                encoding_lib.Encoding_Float_batchnorm_Backward(
                    gradOutput.data, input.data, gradInput.data, gradGamma.data, gradBeta.data,
                    xsum.data, xsqsum.data, gamma.data, beta.data, gradXsum.data, gradXsqsum.data,
                    ctx.N, ctx.eps, ctx.training)
        elif isinstance(input, torch.cuda.DoubleTensor):
            with torch.cuda.device_of(input.data):
                encoding_lib.Encoding_Double_batchnorm_Backward(
                    gradOutput.data, input.data, gradInput.data, gradGamma.data, gradBeta.data,
                    xsum.data, xsqsum.data, gamma.data, beta.data, gradXsum.data, gradXsqsum.data,
                    ctx.N, ctx.eps, ctx.training)
        else:
            raise RuntimeError('Unimplemented data type!')
        return gradInput, gradXsum, gradXsqsum, gradGamma, gradBeta, \
            None, None, None, None, None, None
