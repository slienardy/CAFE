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

class FeedbackGenerator(object):
    '''
    Basic feedback generator.
    '''

    MARK_PRECISION = 1
    
    INTRO_MARK_MESSAGE = "Your grade is {}/20\n\n"
    INTRO_DETAILS_MESSAGE = "Here are some details about your result:\n\n"

    def __init__(self, params=None):
        '''
        Constructor
        '''
        self.FAIL = "Something went wrong during the correction.\n"


    def generate(self, coms_list, titles=None):
        """Merge commentaries in a good looking feedback message
        
        Args:
            com_list (list of string): list of the commentaries
        
        Keyword Args:
            questions_names (list of string): (default: None) a list of question
                names or title. If not precised, it will appear as Question X, 
                with X is the position in the com_list + 1 
        """
        
        """
        If the questions are not names, they are numbered from 1 to 
        len(coms_list) (get_name is either an array access either a lambda fct).
        """
        get_name = titles.__getitem__ if titles else lambda i: "Question " + str(i + 1)
        
        """
        For all tuple (question_name, com), merge them with proper newline char
        + merge all the merged tuples. (+ title (question name) is underlined).
        """    
        return "".join("".join((get_name(i),"\n", '-'*len(get_name(i)) ,"\n\n" ,coms_list[i],"\n")) 
                       for i in range(0,len(coms_list)))
        
