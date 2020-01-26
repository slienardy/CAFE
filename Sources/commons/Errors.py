# coding: utf-8
"""
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
"""

class Error(Exception):
    """Base class for exception in the module
    """
    pass


class CompileError(Error):
    """Raised if an error occurs during the compilation of a student's code. 
    """
    def __init__(self, feedback):
        """
        Args:
            feedback (str): Something usefull to understand why self was risen.
        """
        self.feedback = feedback


class PreprocessError(Error):
    """Raised if an error occurs during the preprocessing of student input.
    
    
    """
    def __init__(self, feedback):
        """
        Args:
            feedback (str): Something usefull to understand why self was risen.
        """
        self.feedback = feedback


class StatementNotRespectedError(Error):
    """Raised if the statement is not respected and the correction should be stopped.
    
    """
    def __init__(self, feedback):
        """
        Args:
            feedback (str): Something usefull to understand why self was risen.
        """
        self.feedback = feedback
        

class NotAWhileLoopError(Error):
    """Raised if the code does not contain any while loop or another loop type
    
    """

    def __init__(self, feedback):
        """
        Args:
            feedback (str): Something usefull to understand why self was risen.
        """
        self.feedback = feedback
        
        
class NotAValidLimitError(Error):
    """Raised if the limits given in the invariant repr. is not relevant
    """
    
    def __init__(self, feedback):
        """
        Args:
            feedback (str): Something usefull to understand why self was risen.
        """
        self.feedback = feedback
        
        
class BullshitInvariantError(Error):
    """Trigger bullshit error if the student's Invariant is worst than bad
    
    This is an easter egg name. Do not change it, it is fun :-)
    """ 
    
    def __init__(self, feedback):
        """
        Args:
            feedback (str): Something usefull to understand why self was risen.
        """
        self.feedback = feedback
        
        
