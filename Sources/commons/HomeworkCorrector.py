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
from itertools import izip_longest, islice
from commons.Errors import Error
from commons.FeedbackGenerator import FeedbackGenerator
from random import choice

class HomeworkCorrector(object):
    """Class implementing an homework corrector
    
    This class implements the behaviour needed to correct a single homework. 
    Based on a ground truth that contents the expected solutions and the 
    student's work, it calculate the grade and generate the feedback. 
    """
    
    def __init__(self, feedback_generator=FeedbackGenerator(), DEBUG=False):
        self.fb_gen = feedback_generator
        self.DEBUG = DEBUG
    
    def secure_correct(self, question, response):
        """Test question and response in a safe way.
        
        Historical note: added after correct() method.
        """
        FAIL = self.fb_gen.FAIL
        
        try:
            return question['action'](response, **(question['params']))
        except Error as e:
            raise e
        except Exception as e:
            if self.DEBUG :
                print question['action'], '\n', e
                raise e
            return (0.0, FAIL)
    
    def correct(self, ground_truth, student_struct):
        """Correct the homework
        
        Args:
            ground_truth (GroundTruth): an ground truth object that contains all
                that is needed to check the student's answer.
            student_struct (list): a list of object (one object per question)
                each object must be handable by the ground_truth
        """ 
        
        questions = ground_truth.structure
        
        # ValueError risen if not in dict is the Assistant responsability
        weights = (q['weight'] for q in questions)
        names = (q['name'] for q in questions)
        
        nb_quest = len(questions)
        secure_correct = self.secure_correct # This is an accelerator trick.
        
        """
        Take the questions and responses (student_struct) and zip them in (q,r)
        tuple (r is the response to question q). Then perform the action on the
        response with the appropriate params. Produce a list of (score, com)
        
        itertools.islice ensures that at max nb_quest answers are considered
        itertools.izip_longest ensures that 'removed solutions' are also considered 
        """
        #results = (q['action'](r, **(q['params']))  for (q, r) in islice(izip_longest(questions, student_struct, fillvalue=" "), nb_quest))
        results = (secure_correct(q, r)  for (q, r) in islice(izip_longest(questions, student_struct, fillvalue=" "), nb_quest))
        
        #unzip trick -> produce a list of grades and a list of coms
        grades, coms = zip(*results)
        
        feedback = self.fb_gen.generate(coms, list(names))
    
        final_grade = ground_truth.grades_mean(grades, weights)
        
        return feedback, final_grade
    
    @staticmethod
    def check_string(test, **args):
        """Compare to strings
        
        Return true if case-lowered tested string is equal to correct one. 
        
        Args:
            test (string): The string to test
        
        Keyword Args:
            correct (string): The string to be compared to test. Use a lowercase
                string!
        """
        ground_truth = args['correct']
        
        if (ground_truth == test.lower()):
            return (1, "OK\n")
        else: 
            return (0, "La réponse est incorrecte\n")
    
    def merge_coms(self, coms_list, questions_names=None):
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
        len(coms_list)
        """
        get_name = questions_names.__getitem__ if questions_names else lambda i: "Question " + str(i + 1)
        
        
        """
        For all tuple (question_name, com), merge them with proper newline char
        + merge all the merged tuples. (+ title (question name) is underlined).
        """    
        return "".join("".join((get_name(i),"\n", '-'*len(get_name(i)) ,"\n\n" ,coms_list[i],"\n")) 
                       for i in range(0,len(coms_list)))
        
        
class HomeworkPreprocessor(object):
    """
    Preprocess the homework and produce an homework structure that will be
    used for the correction
    """
    
    def remove_non_ascii(self, string):
        """Remove non-ascci characters
        
        Args:
            string (str): An input string
        
        Returns:
            The same string, without non-ascci characters and remove '\r'
        """
        return "".join(char for char in string if (ord(char) < 128 and char != '\r'))
    
    
    def preprocess(self, student_file, requierments=None):
        """Preprocess the student homework
         
        Produce the homework structure that will be understood by correct
        functions. Just have to rewrite this to change the preprocessing 
        behaviour.
        
        Args:
            student_file (string): path to student submission
            requierments (list of tuple or int): after having preprocessed each
                elements composing the homework, this enables to builld answer_i
                on the basis of requierments_i. If requierments_i is an int X, 
                answer_i will be the Xth element, else if it a tuple of int, 
                answer_i will be the concatenation of the Yth elements, Y being 
                the ints in the tuple.
            
        Returns:
            (list of object): each object represents a question and should be
                correctly handled by the corrector, since it is the same user
                that chooses the preprocessor and the correction methods.
        """
        
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " " # note: a space and not an empty string
            else:
                return s
        
        # Added whitespaces characters after inline comments...
        pattern = re.compile(
                r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
                re.DOTALL | re.MULTILINE
                )
    
        with open(student_file, "r") as fstudent:    
            uncommented = re.sub(pattern, replacer, fstudent.read())       
                 
        return self.generate_answers(self.remove_non_ascii(uncommented), requierments=requierments)

    def preprocess_to_file(self, student_file):
        """
        
        """
        
        
        prep = self.preprocess(student_file)
        
        
        print "\n#\n".join(prep)
        

    def generate_answers(self, uncommented, answer_limit='#', requierments=None):
        """Transform uncommented homework in list of answers
        
        Args:
            uncommented (string): an uncommented string
            answer_limit (string): symbol separating two answers (default: '#')
            requierments (list of tuple or int): enables to either select parts of answers, either
                pack serveral answer together to be used by a correction fonction. E.g if only answer
                #1, #3, #4 must be corrected, requierements would be [1, 3, 4]. If, e.g. answers 2 is needed
                for all corrections fonctions, requierements would be [(1,2), (3,2), (4,2)] 
            
        Returns:
            (list of strings): a list of substrings that were separated by the
                answer_limit in the uncommented string
                OR list of tuple of answers, combined according to the requierments
                
        Note:
            Requierments were added to enables grouping of questions during correction.
            It enables to generate the groups of answers rather to allow all correcting
            function to access to all answer. That enables to write general correction
            functions, that do not depend on a particular homework since the correction
            function does not have to chose the answer in the list: the preprocessor
            handles this task.
        """
        
        """
        This obviously remove all the empty (if empty student response, it 
        will contain at least a newline character. Then, it trims the string
        (remove leading and trailing whitespace). 
        """
        answers = [s.strip() for s in uncommented.split(answer_limit) if s]
        
        if not requierments:
            return answers
        
        else:
            """
            If requierement is a tuple, produce the tuple containing all the corresponding answers
            So basically, it is a combination of answers.
            
            If requierement is only an int, just return the corresponding answer.
            """
            return [tuple(answers[i] for i in r) if type(r) == tuple else answers[r] for r in requierments]
    

class GroundTruth(object):
    """Define expected results and how to check them
    
    Actual check and verification is done by HomeworkCorrector. This class can
    be used to define new answer correction methods and is a kind of container
    thought to make the student answer parsing and correcting a bit cleaner. 
    """
    
    POSITIVE = ('OK !\n', 'Parfait !\n', 'TB !\n', 'Correct !\n')
    
    def __init__(self, num, name, structure):
        """Constructor
        
        Args:
            num (int): id of the homework
            name (name): name of the homework
            structure (list): a list of dict. Each dict have to contain the
                following keys: 'action' and 'params'. Each 'action' is a method
                that take at least one argument. This action is intented 
                to be used like this:
                    structure['action'](test, **params)
                where test is the proposition of the student and params is a 
                dict that may contain an up-to-you number of parameters that 
                will be used by action. There is no assumption on the type of
                test arg, as it will be determined by the choice of 
                HomeworkPreprocessor
        See Also:
            HomeworkPreprocessor
        """
        self.hmwk_id = num
        self.hmwk_name = name
        self.structure = structure
        self.requierments = None
    
    @staticmethod
    def get_positive():
        return choice(GroundTruth.POSITIVE)
    
    @staticmethod        
    def correct_nothing(actual, **args):
        return (0, "-")
    
    @staticmethod
    def correct_debug(actual, **args):
        
        print 'ACTUAL:', actual
        print 'KW-ARGS:', args
        
        return (0.0, "DEBUG")
    
    @staticmethod
    def correct_compilation(actual, **args):
        """Return 1
        Give point because compilation succeed
        """
        
        return (1, "La compilation a réussi\n")
    
    @staticmethod
    def grades_mean(grades, weights):
        """A standard way to compute mean
        
            Args:
                grades (list of float): grades to each questions
                weigth (list of float): a weight for each questions
        """
        return sum(((g if g > 0.0 else 0.0) * w for (g,w) in zip(grades, weights)))
    
    def test_and_merge_com(self, test, com_true, com_false):
        """Take a test and return the tuple (grade/1, com)
        """
    
        return (1.0, com_true) if test else (0.0, com_false)
    
if __name__ == '__main__':
    pass
