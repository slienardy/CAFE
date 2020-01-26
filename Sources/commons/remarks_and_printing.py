# coding: utf-8
'''
@author: Simon Liénardy <simon.lienardy@uliege.be>

Copyright - Simon Liénardy <simon.lienardy@uliege.be> 2020

This file is part of CAFÉ.
 
CAFÉ is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CAFÉ is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CAFÉ.  If not, see <http://www.gnu.org/licenses/>.
'''
import textwrap as tw
from itertools import chain as ch
from collections import namedtuple
#from enum import Enum
from commons.enumS import Enum
from Course import ACTION_DICT, translate_code_to_chapter, INFO0946

LINE_LENGTH=80

FrameParts = namedtuple('FrameParts', 'LU, LD, RU, RD, H, V')

"""
text (iterable of str)
"""
Remark = namedtuple('Remark', 'code, priority, text, type, seq_number')

R_TYPE = Enum('R_TYPE', 
              ("TITLE",
               "DISPLAY",
               "REMARK",
               "EXAMPLE",
               "FEEDFWD_Q",
               "FEEDFWD_W",
               "FEEDFWD_T",
            )) 

# Creators

# 1.Title
title = lambda tit, i=0: Remark(None, None, tit, R_TYPE.TITLE, i)

# 2.Display
disp_msg = lambda msg, i=0: Remark(None, None, msg, R_TYPE.DISPLAY, i)

# 3.Remark
def remark(code, priority, text, seq_nb=0):
    return Remark(code, priority, text, R_TYPE.REMARK, seq_nb)

def add_ffwd(code, priority, seq_nb=0):
    return Remark(code, priority, "", R_TYPE.REMARK, seq_nb)

# 4.Example
def example(code, priority, text, seq_nb=0):
    return Remark(code, priority, text, R_TYPE.EXAMPLE, seq_nb)

# 5.Feedfwd_Q
def feedfwd_question(code, priority, seq_nb):
    return Remark(code, priority, "", R_TYPE.FEEDFWD_Q, seq_nb)

# 6.Feedfwd_W
warning = lambda war, i: Remark(war, None, None, R_TYPE.FEEDFWD_W, i)

# 7.Feedfwd_T
def feedfwd_trail(code):
    return Remark(code, 0, "", R_TYPE.FEEDFWD_T, 0)

###############################################################################
#                            Printing code                                    #
###############################################################################

# For simple feed-forward, for example
# All these code correspond to utf-8 char of length 1
single_frame = FrameParts('\xe2\x95\xad', '\xe2\x95\xb0', '\xe2\x95\xae', '\xe2\x95\xaf', '\xe2\x94\x80', '\xe2\x94\x82')


# For feed-forward in a Warning, for example
# All these code correspond to utf-8 char of length 1
double_frame = FrameParts('\xe2\x95\x94', '\xe2\x95\x9a', '\xe2\x95\x97', '\xe2\x95\x9d', '\xe2\x95\x90', '\xe2\x95\x91')

def print_title(remark):
    return ("\n\n", remark.text, "\n", '\xe2\x94\x80'*LINE_LENGTH, "\n\n")

def translate_course(code):
    """
    """
    RELIRE = "Nous vous conseillons de relire attentivement ces parties du cours :\n   "
    
    return RELIRE + " > ".join(translate_code_to_chapter(INFO0946, code))

def translate_action(code):
    """
    """
    # 
    return ACTION_DICT.get(code, code)
    

def translate_code(code):
    """
    Translation of the code into a feedforward message
    
    Args:
        code (str): code that indicate a feedforward
        
    Returns:
        (str): a text to be printed
    """
    translate_fct = {"A" : translate_action,
                     "C" : translate_course}
    
    return translate_fct.get(code[0], lambda i : i)(code[1:])
    

def print_ff(remark):
   
    return frame_text(translate_code(remark.code), LINE_LENGTH, single_frame)

def print_warning(remark):
    
    return frame_text(translate_code(remark.code), LINE_LENGTH, double_frame)

def frame_text(text, line_length, frame_parts):
    """
    Frame a text in a frame consisting of 1 character-wide symbols defined in frame_parts.
    
    Args:
    
    text (str): the text to be framed
    line_length (int): the total length of the line [nbr of char]
    frame_parts (FrameParts): a namedtuple that defines Left UP (LU), Right Up (RU), Left Down (LD),
        Right Down (RD), Left Down (LD), Horizontal (H) and Vertical (V) frame symbols. These symbols SHOULD
        be 1-char wide. (e.g. : a=FrameParts('+','+','+','+', '-', '|'))
    
    Returns:
        the framed text (encoded in utf8)
    
    """
    
    assert isinstance(frame_parts, FrameParts) and line_length >= 5
    
    TOT_MARGIN = 4
    
    lines  = ch.from_iterable(tw.wrap(t, line_length - TOT_MARGIN) for t in text.decode('utf8').splitlines())
    
    formated_hdr = (frame_parts.LU, frame_parts.H*(line_length - 2), frame_parts.RU, "\n")
    formated_ftr = (frame_parts.LD, frame_parts.H*(line_length - 2), frame_parts.RD, "\n")
    
    formatted_lines = ("".join((frame_parts.V, " ", line.ljust(line_length - 4).encode('utf8'), " ", frame_parts.V, "\n")) for line in lines)

    return ch.from_iterable((formated_hdr, formatted_lines, formated_ftr))
    
