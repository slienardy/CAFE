# pycparser -- A C parser in Python
#
# Copyright (c) 2008-2017, Eli Bendersky
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this 
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation 
#  and/or other materials provided with the distribution.
# * Neither the name of Eli Bendersky nor the names of its contributors may 
#   be used to endorse or promote products derived from this software without 
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-----------------------------------------------------------------
# pycparser: __init__.py
#
# This package file exports some convenience functions for
# interacting with pycparser
#
# Copyright (C) 2008-2015, Eli Bendersky
# License: BSD
#-----------------------------------------------------------------
__all__ = ['c_lexer', 'c_parser', 'c_ast']
__version__ = '2.14'

from subprocess import Popen, PIPE
from .c_parser import CParser


def preprocess_file(filename, cpp_path='cpp', cpp_args=''):
    """ Preprocess a file using cpp.

        filename:
            Name of the file you want to preprocess.

        cpp_path:
        cpp_args:
            Refer to the documentation of parse_file for the meaning of these
            arguments.

        When successful, returns the preprocessed file's contents.
        Errors from cpp will be printed out.
    """
    path_list = [cpp_path]
    if isinstance(cpp_args, list):
        path_list += cpp_args
    elif cpp_args != '':
        path_list += [cpp_args]
    path_list += [filename]

    try:
        # Note the use of universal_newlines to treat all newlines
        # as \n for Python's purpose
        #
        pipe = Popen(   path_list,
                        stdout=PIPE,
                        universal_newlines=True)
        text = pipe.communicate()[0]
    except OSError as e:
        raise RuntimeError("Unable to invoke 'cpp'.  " +
            'Make sure its path was passed correctly\n' +
            ('Original error: %s' % e))

    return text


def parse_file(filename, use_cpp=False, cpp_path='cpp', cpp_args='',
               parser=None):
    """ Parse a C file using pycparser.

        filename:
            Name of the file you want to parse.

        use_cpp:
            Set to True if you want to execute the C pre-processor
            on the file prior to parsing it.

        cpp_path:
            If use_cpp is True, this is the path to 'cpp' on your
            system. If no path is provided, it attempts to just
            execute 'cpp', so it must be in your PATH.

        cpp_args:
            If use_cpp is True, set this to the command line arguments strings
            to cpp. Be careful with quotes - it's best to pass a raw string
            (r'') here. For example:
            r'-I../utils/fake_libc_include'
            If several arguments are required, pass a list of strings.

        parser:
            Optional parser object to be used instead of the default CParser

        When successful, an AST is returned. ParseError can be
        thrown if the file doesn't parse successfully.

        Errors from cpp will be printed out.
    """
    if use_cpp:
        text = preprocess_file(filename, cpp_path, cpp_args)
    else:
        with open(filename, 'rU') as f:
            text = f.read()

    if parser is None:
        parser = CParser()
    return parser.parse(text, filename)
