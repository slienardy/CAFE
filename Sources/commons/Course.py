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



def translate_code_to_chapter(course, code):
    """
    Translate a numerical code into a link to a particular resources.
    The link with our course is not given here.
    """
    return "[INSERT HERE A LINK TO THE THEORETICAL COURSE]"


COURSE = None

#
# Format : {code : action}
# code   : str
# action : str
#       
ACTION_DICT = {
    "Enonce"  : "Warning!\nYou should carefuly read again the instructions!",
    "Warning" : "Warning!",
    "RUS_MUL" : "You should carefuuly read again the example of Russian peasant multiplication."
                "Write first a draft and then, check your answer encoding.",
    "ACode"   : "Please contact the T.A. concerning the analysis of your code.",
    "Assist"  : "Please contact the T.A. quickly!",
    "Init"    : "Check that you initialize correctly all the variables that must be initialized.",
    "ValPart" : "Test your code with particular values (e.g. 0) and compare it to the expected result.",
    "Methodo" : "To correct your code, simulate the algorithm on a sheet of paper. Then, apply the course methodology. Read again this part of the course:\n{}".format(" > ".join(translate_code_to_chapter(COURSE, "2.1.1"))),
    "Tours"   : "In order to reduce the number of iterations, check the loop condition. Check also if your code does unnecessary iterations.",
    "Infinity": "Infinite loop: check the variables present in the loop condition and the way there are modified. The loop condition must become false (i.e. = 0) in order to make the iteration stop!",
    "Encodage": "Please read carefuly the Graphical Loop Invariant encoding instructions.\n",
    "Result"  : "In order to correct your code, test at home with different values, compare the output with the expected result (described in the instructions). Then use your Invariant to correct your code.",
    "InvInit" : "Variable initialisation according to the Invariant: thanks to the Graphical Loop Invariant, draw the initial situation. Derive from your sketch the initial values of the variables present in your code.",
    "InvFail" : "To correct your Loop Invariant(s), read again the Challenge instructions. Draw a picture, compare this picture to the blank Invariant given in the instructions. Then fill the template according to the instructions recommendations",
    "LoopInv" : "1 Loop Invariant = 1 loop. The architecture of the expected code is described in the instructions.",
    "GotoEtc" : "Use your Loop Invariant(s) Thanks to them, you will be able to write pieces of code without any 'break', 'continue' or 'goto'. These instructions are not usefull here (except the 'break' at the end of a switch's case.",
    "FCTT"    : "[INSERT HERE A HINT ABOUT THE LOOP VARIANT]",
    "BadArray": "Array Out Of Bounds: Use your Loop Invariant while you write the loop body. Check all the indeces whiles accessing array elements.",
    }

