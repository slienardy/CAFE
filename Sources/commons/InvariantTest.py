#!/usr/bin/env python
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

import re
from commons.Errors import NotAValidLimitError

class Limit(object):
    """
    Attention: only work with integer limits
    """

    NO = 0
    DEFAULT = 1
    PLUS = 2
    MINUS = 3

    #CST_DICT = {0: '', 1:"?", 2:"+1", 3:'-1'}
    #Optim :
    CST_DICT = ('', '?', '+1', '-1')
    CST_NBR = len(CST_DICT)

    def __init__(self, symbol, modif):
        """Constructor
        
        Args:
            symbol (stringable): representation of a limit (either a string or 
                an int (is converted by the constructor)
            modif (int): a constant value representing a modifier appended to 
                the limit (e.g. "+1", "-1", etc. must be a key in cls.CST_DICT
            
        Raises:
            NameError or SyntaxError if symbol is not a proper string...
        """
        self.symbol = str(symbol)
        
        # Make "+1" become numerical const.
        if not self.symbol:
            if modif == self.PLUS:
                self.symbol = "1"
                self.modif = self.NO
            elif modif == self.MINUS:
                self.symbol = "-1"
                self.modif = self.NO
            else:
                self.modif = modif if modif == self.NO else self.DEFAULT
        
        else:
            self.modif = modif if (modif >= 0 and modif < self.CST_NBR) else self.DEFAULT

    def __eq__(self, other):
        """
        """
        return self.symbol == other.symbol and self.modif == other.modif

    def __ne__(self, other):
        """
        """
        return self.symbol != other.symbol or self.modif != other.modif

    def __str__(self):
        """Called by str() builtin function
        """
        return self.symbol + self.CST_DICT[self.modif]

    def next(self):
        """Give the following limit"""
        if self.modif == self.NO:
            return Limit(self.symbol, self.PLUS)

        elif self.modif == self.MINUS:
            return Limit(self.symbol, self.NO)
        else:
            return None

    def prev(self):
        """Give the previous limit"""
        if self.modif == self.NO:
            return Limit(self.symbol, self.MINUS)

        elif self.modif == self.PLUS:
            return Limit(self.symbol, self.NO)
        else:
            return None

    def is_num_const(self):
        """
        """
        try:
            _ = int(self.symbol)
        except ValueError:
            return False
        
        return True
        #return self.symbol and (self.symbol.isdigit() or (self.symbol[0] == '-' and self.symbol[1:].isdigit()))

    def is_unspecified(self):
        """
        """
        return self.symbol == '_' or (self.symbol == '' and self.modif == self.NO)

    def is_var(self):
        """Determine if the Limit is described by a var
        
        """
        return not self.is_num_const() and not self.is_unspecified()

    def eval(self, value):
        """
        Eval a Limit
        """
        if self.is_num_const():
            return int(self.symbol)
        
        if self.is_unspecified():
            return None
        
        value = value
        if self.modif == self.PLUS:
            value += 1
        elif self.modif == self.MINUS:
            value -= 1
            
        return value    
        
            
    
def create_Limit(text):
    """Factory on the basis of text and enabling to raise error on creation.
    """

    """
    REGEX EXPLANATION:
        (-?[0-9]*)        - Match a number and capture into a group
        \.\s*             - Do not capture the dot and allow spaces
        (-?[a-zA-Z0-9_]*) - Capturer identifier or const in a group
        (\s*+\s*1)        - Capture if "+1" is present
        (\s*-\s*1)        - Capture if "-1" is present
    
    As regex are gready, "-1" is considered a constant and not the '-1' modifier.
        
    MATCH GROUP:
        1 Line number
        2 Constant or Identidfier
        3 "+1" is present
        4 "-1" is present 
    """
    pat = re.compile("([0-9]*)\.\s*(-?[a-zA-Z0-9_]*)(?:(\s*\+\s*1)|(\s*-\s*1))?\s*")

    m = pat.match(text)

    if not m or len(m.group()) != len(text):
        raise NotAValidLimitError("{}: Mauvaise spécification de limite\n".format((text)))
    """
    if m.group(2) == "":
        if m.group(3):
            return Limit('1', Limit.NO)
        
        if m.group(4):
            return Limit('-1', Limit.NO)
    """
    if m.group(3):
        modif = Limit.PLUS
    elif m.group(4):
        modif = Limit.MINUS
    else:
        modif = Limit.NO

    return Limit(m.group(2), modif)

def make_limits_list(text):
    """
    
    """
    return [create_Limit(line.strip()) for line in text.splitlines() if line]

def make_limits_list_wFB(text):
    """Give some feedback creating the list
    
    """
    def defensive_creation(text):
        feedback = ""

        try:
            result = create_Limit(text)
        except NotAValidLimitError as e:
            result = Limit("??", Limit.DEFAULT)
            feedback = e.feedback

        return (result, feedback)

    lists = (defensive_creation(line.strip()) for line in text.splitlines() if line)

    limits, coms = zip(*lists)

    return (list(limits), "".join(coms))

