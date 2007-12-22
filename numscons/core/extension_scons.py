#! /usr/bin/env python
# Last Change: Fri Dec 07 06:00 PM 2007 J

# Module for support to build python extension. scons specific code goes here.
import sys
from copy import deepcopy

from distutils.unixccompiler import UnixCCompiler
from numpy.distutils.misc_util import msvc_runtime_library

from extension import get_pythonlib_dir, get_python_inc
from misc import built_with_mstools, built_with_ming, built_with_gnu_f77, \
                 get_pythonlib_name

def PythonExtension(env, target, source, *args, **kw):
    # XXX: Some things should not be set here... Actually, this whole
    # thing is a mess.
    def floupi(key):
        if env.has_key(key):
            narg = deepcopy(env[key])
        else:
            narg = []

        if kw.has_key(key):
            narg.append(kw.pop(key))

        return narg

    LINKFLAGS = floupi('LINKFLAGS')
    CPPPATH = floupi('CPPPATH')
    LIBPATH = floupi('LIBPATH')
    LIBS = floupi('LIBS')

    CPPPATH.append(get_python_inc())
    if sys.platform == 'win32': 
        if built_with_mstools(env):
            # XXX: We add the path where to find python lib (or any other
            # version, of course). This seems to be necessary for MS compilers.
            #env.AppendUnique(LIBPATH = get_pythonlib_dir())
            LIBPATH.append(get_pythonlib_dir())
    	elif built_with_mingw(env):
            # XXX: this part should be moved elsewhere (mingw abstraction
            # for python)

            # This is copied from mingw32ccompiler.py in numpy.distutils
            # (not supported by distutils.)

            # Include the appropiate MSVC runtime library if Python was
            # built with MSVC >= 7.0 (MinGW standard is msvcrt)
            py_runtime_library = msvc_runtime_library()
            LIBPATH.append(get_pythonlib_dir())
            LIBS.extend([get_pythonlib_name(), py_runtime_library])
    elif sys.platform == "darwin":
        # XXX: When those should be used ? (which version of Mac OS X ?)
        LINKFLAGS += ' -undefined dynamic_lookup '
    else:
        pass

    # Use LoadableModule because of Mac OS X
    # ... but scons has a bug (#issue 1669) with mingw and Loadable
    # Module, so use SharedLibrary with mingw.
    if built_with_mingw(env):
        wrap = env.SharedLibrary(target, source, SHLIBPREFIX = '', 
                                 #LDMODULESUFFIX = '$PYEXTSUFFIX', 
                                 SHLIBSUFFIX = '$PYEXTSUFFIX', 
                                 LINKFLAGS = LINKFLAGS, 
                                 LIBS = LIBS, 
                                 LIBPATH = LIBPATH, 
                                 CPPPATH = CPPPATH, *args, **kw)
    else:
        wrap = env.LoadableModule(target, source, SHLIBPREFIX = '', 
                                  LDMODULESUFFIX = '$PYEXTSUFFIX', 
                                  SHLIBSUFFIX = '$PYEXTSUFFIX', 
                                  LINKFLAGS = LINKFLAGS, 
                                  LIBS = LIBS, 
                                  LIBPATH = LIBPATH, 
                                  CPPPATH = CPPPATH, *args, **kw)
    return wrap

def createStaticExtLibraryBuilder(env):
    """This is a utility function that creates the StaticExtLibrary Builder in
    an Environment if it is not there already.

    If it is already there, we return the existing one."""
    import SCons.Action

    try:
        static_extlib = env['BUILDERS']['StaticExtLibrary']
    except KeyError:
        action_list = [ SCons.Action.Action("$ARCOM", "$ARCOMSTR") ]
        if env.Detect('ranlib'):
            ranlib_action = SCons.Action.Action("$RANLIBCOM", "$RANLIBCOMSTR")
            action_list.append(ranlib_action)

    static_extlib = SCons.Builder.Builder(action = action_list,
                                          emitter = '$LIBEMITTER',
                                          prefix = '$LIBPREFIX',
                                          suffix = '$LIBSUFFIX',
                                          src_suffix = '$OBJSUFFIX',
                                          src_builder = 'SharedObject')

    env['BUILDERS']['StaticExtLibrary'] = static_extlib
    return static_extlib