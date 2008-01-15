#! /usr/bin/env python
# Last Change: Tue Dec 04 03:00 PM 2007 J

# Module for custom, common checkers for numpy (and scipy)
import sys
import os.path
from copy import deepcopy
from distutils.util import get_platform

# from numpy.distutils.scons.core.libinfo import get_config_from_section, get_config
# from numpy.distutils.scons.testcode_snippets import cblas_sgemm as cblas_src, \
#         c_sgemm as sunperf_src, lapack_sgesv, blas_sgemm, c_sgemm2, \
#         clapack_sgesv as clapack_src
# from numpy.distutils.scons.fortran_scons import CheckF77Mangling, CheckF77Clib
from perflib import CheckMKL, CheckFFTW3, CheckFFTW2
from support import check_include_and_run
from configuration import BuildOpts, ConfigRes, add_info

__all__ = ['CheckFFT']

def CheckFFT(context, autoadd = 1, check_version = 0):
    """This checker tries to find optimized library for fft"""
    libname = 'fft'
    env = context.env

    def check(func, name):
        st, res = func(context, autoadd, check_version)
        # XXX: check for fft code ?
        if st:
            add_info(env, libname, res)

        return st

    # Check MKL
    st = check(CheckMKL, 'MKL')
    if st:
        return st

    # Check fftw3
    st = check(CheckFFTW3, 'fftw3')
    if st:
        return st

    # Check fftw2
    st = check(CheckFFTW2, 'fftw2')
    if st:
        return st

    add_info(env, libname, None)
    return 0
