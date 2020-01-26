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

#from code.CodeHandler import CodeHandler
from commons.Errors import CompileError, PreprocessError
import subprocess as sub
import commons.HomeworkCorrector as hc
from itertools import repeat

class CodePreprocessor(hc.HomeworkPreprocessor):
    '''
    classdocs
    '''

    def __init__(self, code_handler, **params): 
        """Constructor
        
        Keywords Args:
            code_name (string): name of the code to be created. This file MUST
                 be compliant with the makefile.
            exec_name (strin): name of the executable. This file MUST be 
                compliant with the makefile.
            template (string): template to build the code with 
                code_handler.generate
            gap_number (int): Number of gaps in the template string (a gap is the
                place where the student's code excerpt must be quoted).
            nb_tests (int): number of the tests. Tests are computed by calling 
                './compile_dir + exec_name i' for i in range(nb_tests)
            format (fct): A function that will take a piece_of_code from the
                student and will format it (e.g. to be properly used with a
                parser) the function will be called like this : 
                    format(p_o_c, **args_format) (default: does not alter p_o_c)
            args_format: dict of eventual k/v args to function format (default: 
                None)
            compile_dir (path string): directory in which the code must be 
                compiled. Default is current working directory ('./')
            poc_mask (list of int): for each 
        """
        super(CodePreprocessor, self).__init__()
        self.c_h = code_handler

        self.code_name = params['code_name']
        self.code_template = params['template']
        self.gap_number = params['gap_number']
        self.compile_dir = params.get('compile_dir', './')
        self.exec_name = params.get('exec_name', 'main')
        self.args_format = params.get('args_format', {})
        # If args_format is {}, format(s, {}) = format(s)
        self.poc_format = params.get('format', lambda (s) : s)
        # Enables to have mixed code and text. By default, all is code
        self.poc_mask = params.get('poc_mask', repeat(1))
        
        self.tests_number = params.get('nb_tests', 1)

    
    def prepare_file(self, student_file):
        """
        
        """
        
        classic_prepro = super(CodePreprocessor, self).preprocess(student_file)
    
        # if zipped with repeat(1), is_code always true and select everything
        pieces_of_code = [piece for piece, is_code in zip(classic_prepro, self.poc_mask) if is_code]
    
        others_answers = []    
        
        if len(classic_prepro) > len(pieces_of_code):
            others_answers = [piece for piece, is_code in zip(classic_prepro, self.poc_mask) if not is_code]
    
        code = self.c_h.code_aggregate(self.code_template, pieces_of_code, None)
        
        # This only works with a single file...
        with open(self.compile_dir + self.code_name, "w") as code_file:
            code_file.write(code)

        return others_answers, pieces_of_code

    def preprocess(self, student_file, requierments=None):
        """Preprocess code
        
        Preprocess the code, forming a source code by filling a template with 
        pieces of code taken from student submission. The source code is then 
        
        Requires:
            A makefile that must compile the code using 'make all' target.
        
        Args:
            student_file (string): the path to student file
            requierments (list of int or tuple of int): First generate a list of
                answers in the order:
                    TEXT, FORMATED CODE, CODE EXECUTION RESULTS
                Where:
                    TEXT are texts questions identified when poc_mask[i] = 0
                    FORMATED CODE is pieces of code formated by function "format"
                    CODE EXECUTION RESULTS are obtained for each test (one for each
                        test, number of tests is nb_tests).
                requierments is a list used to group answers together. A request 
                    can be a single int to just quote an answer. A tuple request
                    will group all the answers corresponding of the value stored
                     in the tuple. The grouped answers are then gathered in a tuple
                     that forms a new merged answer.
        
        Returns:
            list of strings: list of the pieces of codes then path to the
                 compiled codes.
                 FIXME : explain with requierments.
                 
        Raises:
            PreprocessError is the file is not properly formated.
            
        See Also:
            CodeHandler, PreprocessorError
        """
        
        others_answers, pieces_of_code = self.prepare_file(student_file)
        
        # Just for the students: (enable to change the recipes in check main command for the students)
        try:
            sub.check_output(['make', 'check', "-s", "-C", self.compile_dir],stderr=sub.STDOUT)
        except sub.CalledProcessError as e:
    
            offsets = list(self.c_h.compute_offsets(self.code_template, pieces_of_code, self.gap_number))
            feedback = "".join(self.c_h.modify_compile_output(e.output, self.code_name, offsets))
        
            raise CompileError("\n".join((feedback, self.c_h.print_code(pieces_of_code))))
        
        # 
        try:
            sub.check_output(['make', 'all', "-s", "-C", self.compile_dir],stderr=sub.STDOUT)
        except sub.CalledProcessError as e:
            raise PreprocessError("")
        
        tests_results = (self.launch_test(i, self.compile_dir + self.exec_name) for i in range(self.tests_number))    
        formatted_poc = (self.poc_format(poc, **self.args_format) for poc in pieces_of_code)
        
        answers = others_answers + list(formatted_poc)  + list(tests_results)
    
        if not requierments:
            return answers
        
        else:
            """
            If requierement is a tuple, produce the tuple containing all the corresponding answers
            So basically, it is a combination of answers.
            
            If requierement is only an int, just return the corresponding answer.
            """
            return (tuple(answers[i] for i in r) if type(r) == tuple else answers[r] for r in requierments)
        
    def preprocess_to_file(self, student_file):
        """
        
        """
        self.prepare_file(student_file)
        
        
    def launch_test(self, test_number, test_pgrm):
        """
        
        """
        try:
            #déterminer comment paramétriser au mieux pour être réutilisable
            output = sub.check_output(["timeout", "300", test_pgrm, str(test_number)], stderr=sub.STDOUT)
        except sub.CalledProcessError as e:
            #print e.output
            return (e.returncode, e.output)
        else:
            # Return code is 0 (no error)
            return (0, output)


