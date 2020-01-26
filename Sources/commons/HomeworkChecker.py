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

from textwrap import fill
from commons.Errors import CompileError, StatementNotRespectedError
import traceback, sys

class HomeworkChecker(object):
    """
    This class implements the behaviours of correction ot students homework and 
    then compute statistics, messages for the mail that will be send to the 
    student and statistics computation.
    
    This class handles all the main work: launch preprocessing, correction, save
    files, etc.  
    """
    
    COMPILE_ERROR_MESSAGE = ("Something went wrong during the compilation."
        " Please find in the following some details about what caused the problem"
        " during the compilation. Your code MUST compile in order to be corrected.\n")
    
    INDERTERMINED_ERROR_MESSAGE = ("An undetermined error has occurred. This implies "
        "that there is a problem with your submission file. As a result, your submission"
        " is given a null rating by default. After reviewing the statement, you may "
        "contact the education team if you think your submission should be acceptable.\n")
    
    STATEMENT_ERROR_MESSAGE = ("An error occurred in the correction because you do not "
        "respect the instructions. In these circumstances, it is not possible to continue"
        " correcting your work. The grade you are given is therefore 0.0/20. Please read "
        "below the reasons for your sanction for non-compliance with the instructions:\n")
    
    MARK_PRECISION = 1
    
    INTRO_MARK_MESSAGE = "Hello!\n\nYour grade is {}/20\n\n"
    INTRO_DETAILS_MESSAGE = "Here are some details about your result:"
    
    def __init__(self, corrector, preprocessor, ground_truth):
        """Consructor
        
        Args:
            corrector (HomeworkCorrector): implementing the correct method.
            preprocessor (HomeworkPreprocessor): enabling to create answers on 
                the basis on the student's submission.
            ground_truth (GroundTruth): enabling to compute answers and grades
             
        """
        self.corrector = corrector
        self.preprocessor = preprocessor
        self.gt = ground_truth
    
    def save_mark(self, mark, mark_file="mark.txt"):
        """
        Save mark in mark file
        
        Args:
            mark (float): the mark to be save
            mark_file (str): path to the mark file (default: mark.txt)
        """
        PRECISION = 1
        
        with open(mark_file, "w") as mfile:
            mfile.write(str(round(mark, PRECISION)))
            
    def save_comment(self, comment, comment_file="comments.txt"):
        """
        Save comment in comment file
        
        Args:
            comment (str): the comment to be save
            comment_file (str): path to the comment file (default: comment.txt)
        """    
        with open(comment_file, "w") as cfile:
            cfile.write(comment)
    
    def handle_submission(self, student_file, DEBUG=False):
        """
        Args:
        
        student_file (path string): string that contain the name of the file that 
            contains the student's submission
        
        Returns:
            (string) a complete feedback containing the result of the student
            
        """
        try:
            stu = self.preprocessor.preprocess(student_file, requierments=self.gt.requierments)
            
            feedback, grade = self.corrector.correct(self.gt, stu)
        except CompileError as e:
            if DEBUG:
                print e
            feedback = fill(self.COMPILE_ERROR_MESSAGE, 80)
            
            feedback += e.feedback
            grade = 0.0
            
        except StatementNotRespectedError as e:
            if DEBUG:
                print e
            feedback = fill(self.STATEMENT_ERROR_MESSAGE, 80)
            
            feedback += e.feedback
            grade = 0.0
            
        except Exception:
            if DEBUG:
                print e
            feedback = fill(self.INDERTERMINED_ERROR_MESSAGE, 80)
            
            grade = 0.0
            
            traceback.print_exc(file=sys.stderr)
             
        complete_feedback = "".join((self.INTRO_MARK_MESSAGE.format(round(grade, self.MARK_PRECISION)), 
                                     self.INTRO_DETAILS_MESSAGE, "\n",
                                    feedback))
        
        self.save_mark(grade)
        self.save_comment(feedback)
        
        print complete_feedback # on stdout -> sent to the student as a mail.
                   
    def preprocess_for_plagiarism(self, student_file, ):
        """Just preprocess the file in order to pass it to plagiarism detector 
        (e.g.: Stantford's MOSS).
        
        Args:
        
        student_file (path string): string that contain the name of the file that 
            contains the student's submission
        
        Returns:
            Nothing. Either create a file or print its content on stdout
            
        """
        try:
            self.preprocessor.preprocess_to_file(student_file)
        except Exception as e:
            print e
            print "An unexpected error occured!\n"
        
        
