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

import bisect
import math
import re
from pycparser import c_parser
from Statistics import IDLister, LoopCounter, CodeStatistics, Homework3CodeArchChecker, Homework4CodeArchChecker



class CodeHandler(object):
    """
    """
    def __init__(self):
        self.parser = None


    def modify_compile_output(self, compile_output, code_name, line_offsets):
        """
        """
        
        pat = re.compile(r'{}:([0-9]*):([0-9]*):'.format(code_name))
        m = pat.search(compile_output)
        
        begining = 0
        
        while(m):
            # match found in compile output.
            # First yield what that must not be modified
            yield compile_output[begining:m.start()]
            
            # Modify the number of the line
            correct_line = self.compute_line(int(m.group(1)), line_offsets)
            
            # Join is less readable but more efficient...
            yield "".join(("ligne ", str(correct_line), ", colonne ", m.group(2), " : "))
            
            # Used to search for match in not yet processed string.
            begining = m.end() + 1
            
            # Search new pattern if any.
            m = pat.search(compile_output, pos=m.end())
            
        # Then, yield what is after the last match
        if begining < len(compile_output):
            yield compile_output[begining:]
    
    def code_aggregate(self, code_template, pieces_of_code, params):
        """
        """
        
        return code_template.format(*pieces_of_code)
    
    def compute_line(self, line, line_offsets):
        """
        """
        pos = bisect.bisect_right(line_offsets, line)
        
        return line - line_offsets[pos - 1]
    
    def compute_offsets(self, code, code_filling, gap_nber):
        """Compute the offset in the code 
        
        Basically, code will look like this:
        
        Code
        Filling 1
        Code
        ...
        Code
        Filling i
        Code
        ...
        Code
        
        'Filling' is student submission. One want to say 'line' x is in fact line y
        in the part i of student submission
        
        Raises:
            AssertionError if len(code_filling) != gap_nber (in this case, calculation
                is impossible).
        """
        assert (len(code_filling) == gap_nber)
          
        gap_pos = (code.find(''.join(('{', str(i), '}')))  for i in range(gap_nber))
        
        fill_offset = (code.count('\n', 0, end) for end in gap_pos)
        
        # + 1 is not needed because of the '\n' that follow the {number} in format
        # string.
        fill_length = [fill.count('\n') for fill in code_filling]
    
        # Code n is offset by the lentgh of all the previous codes (from 1 to n-1)
        cumulative_code_length = (sum(fill_length[0:l]) for l in range(gap_nber))
    
        return (a + b for (a,b) in zip(fill_offset, cumulative_code_length))
    
    def number_lines(self, text):
        """Add number of the line in front of each line, starting at one
        
        This preserve line separator. The number are right justified to form a nice
        numbering column. Isn't it beautiful? Next time, it will do the coffee too.
        
        Args:
            text (string): text to be processed
            
        Returns:
            the same text but the lines are numbered.
        """
        
        if not text:
            return ''
        
        lines = text.splitlines(True)
        
        #print lines
        
        nb_lines = len(lines)
        
        # Nice padding:
        padding =  int(math.floor(math.log10(nb_lines) + 1))
        
        numeroted_lines = (" ".join((str(i + 1).rjust(padding), line)) for (i, line) in enumerate(lines))
        
        return "".join(numeroted_lines)
    
    def print_code(self, pieces_of_code):
        """
        
        """
        entitled_code = ("\n".join(("\n\nCode {}:".format((str(i + 1))), 
                                    self.number_lines(code))) for (i,code) in enumerate(pieces_of_code))
        
        return "".join(entitled_code)


    def check_loop_types(self, function):
        """Check the loops used in a function
    
        Create the ast of a C function, recursively browse it and produce the 
        numbers of loops that is contained in the function.
    
        Returns:
            tuple: (#While, #For, #Do...While)
        
        Raises:
            Parsing Error stuffs from pycparser if the student coded with his ass 
            rather than hands.
        """
        if not self.parser:
            self.parser = c_parser.CParser()
            
        ast = self.parser.parse(function, filename='<none>')
    
        lc = LoopCounter()
        lc.visit(ast)
    
        return (lc.while_count, lc.for_count, lc.dowhile_count)
    
    def get_init_values(self, function):
        """
        
        """
        if not self.parser:
            self.parser = c_parser.CParser()
            
        ast = self.parser.parse(function, filename='<none>')
        
        lister = IDLister()
        lister.visit(ast)
        
        return lister.init_values
    
    def get_index_init_values(self, function):
        """
        
        """
        if not self.parser:
            self.parser = c_parser.CParser()
            
        ast = self.parser.parse(function, filename='<none>')
        
        lister = IDLister()
        lister.visit(ast)
        
        return {k : v for k,v in lister.init_values.iteritems() if k in lister.get_index_ids()}
        
    def code_analysis(self, function, decl_nbr=0):
        """
        Args:
            decl_nbr (int): nuber of the declaration (if several fct declared in a same file)
            
        Deprecated: Should be moved apart CodeHandler (See Statistics module)
        """
        if not self.parser:
            self.parser = c_parser.CParser()
            
        ast = self.parser.parse(function, filename='<none>')
        
        cs = CodeStatistics()
        cs.visit(ast.children()[decl_nbr][1])
        
        return cs.get_report()
        
