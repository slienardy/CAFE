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

from pycparser import c_parser, c_ast
from collections import namedtuple, defaultdict

class GuardAnalyser(c_ast.NodeVisitor):
    
    def __init__(self):
        self.ops = []
        self.ids = []
    
    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c_name, c in node.children():
            self.visit(c)
            
        return ""
    
    def visit_BinaryOp(self, node):
        self.ops.append(node.op)
        
        return "".join(("(",
                        self.visit(node.left),
                        " ",
                        node.op, 
                        " ", 
                        self.visit(node.right),
                        ")"
                        ))
        
    def visit_UnaryOp(self, node):
        
        self.ops.append(node.op)
        
        return "".join((
                "(",
                node.op,
                " ",
                self.visit(node.expr),
                ")"
                ))
        
    def visit_ID(self, node):
        
        self.ids.append(node.name)
        
        return node.name
    
    def visit_Constant(self, node):
        
        return node.value

# Make a factory for the user (in order to add fields and reprogram visiting functions).
class CodeStatistics(c_ast.NodeVisitor):
    """
    This class has several goal:
    1. Count the loops
    2. Count the conditionals instructions (in and out the loops)
    3. Check the presence of returns / continues / break in and out loops.
    4. Presence of go to instruction
    5. List the variables, indexes and their initial values.
    """
    
    # some const
    # Loops are even numbers...
    WHILE = 0
    DOWHILE = 2
    FOR = 4
    IF = 1
    SWITCH = 3 
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        #Ensure that reset is redefined
        assert('reset' in type(self).__dict__)
        
        # 1. 
        self.while_count = 0
        self.dowhile_count = 0
        self.for_count = 0
        
        # 2.
        self.cond_in_loops = 0
        self.cond_out_loops = 0
        
        # 3.
        self.return_in_loop = 0
        self.return_in_control = 0
        self.return_encoutered = False
        
        self.continue_in_loop = 0
        
        self.break_in_loop = 0
        #. Do not exist, except in switch...
        
        # 4.
        self.goto_count = 0
        
        # 5. List of var, indexes, ...
        self.ids = []
        self.index_ids = []
        self.visiting_arrayRef_count = 0
        self.init_values = dict()
        self.remarks = []
        
        # 6. Instr. stack
        self.instr_stack = [] # empty stack
        self.push = self.instr_stack.append
        self.pop = self.instr_stack.pop
        self.top = lambda : self.instr_stack[-1] 
        
        # 7. Funcions usage
        self.called_func = set()
        
        # State information (0 = outside, > 0 counts inner level)
        self.stack_while = 0
        self.stack_for = 0
        self.stack_dowhile = 0
        self.stack_switch = 0
        self.stack_if = 0
        
        # Gather info about loop and guards
        self.guard = False
        self.loops_list = []
        
    def is_loop(self, x): 
        return (x % 2) == 0
        
    def get_level(self):
        return sum((self.stack_dowhile, self.stack_for, self.stack_if,
                   self.stack_switch , self.stack_while))
        
    def is_in_loop(self):
        return sum((self.stack_dowhile, self.stack_for, self.stack_while)) > 0

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c_name, c in node.children():
            # Set guard to True if cond of a loop
            if c_name == 'cond' and self.is_loop(self.top()):
                self.visit_guard(c)
                #self.loops_list[-1]['guard'] = c
                
            self.visit(c)
            
    def visit_guard(self, node):
        """
        Special visit for loop guards
        """
        """
        self.guard = True
        self.visit(node)
        self.guard = False    
        """
        g = GuardAnalyser()
        
        guard = g.visit(node)
        
        self.loops_list[-1]['guard'] = guard
        self.loops_list[-1]['ids'] = tuple(g.ids)
        self.loops_list[-1]['ops'] = tuple(g.ops)

    def loop_register(self, name):
        
        self.loops_list.append({
            'type' : name,
            'level': self.get_level(),
            'guard': None,
            'ids'  : None,
            'ops'  : None,
            })

    def switch_or_loop(self):
        """
        Determine if the last instr. block is a switch or a loop.
        """
        
        last_instr_pos_list = (pos if val != self.IF else 0 
                               for pos, val in enumerate(self.instr_stack))
        
        last_instr_pos = max(last_instr_pos_list)
        
        return self.instr_stack[last_instr_pos] == self.SWITCH
        

    def visit_Continue(self, node):
        
        self.continue_in_loop += 1
        
        self.generic_visit(node)
    
    def visit_Break(self, node):
        # This test must be done more precisly...
        # Cause a break in a if statement in a loop is not counted...
        if not self.switch_or_loop():
            self.break_in_loop += 1
        
        self.generic_visit(node)
    
    def visit_Return(self, node):
        
        self.return_encoutered = True
        
        if self.get_level() > 1:
            self.return_in_control += 1
            if self.is_in_loop():
                self.return_in_loop += 1
        
        self.generic_visit(node)

    def visit_While(self, node):
        self.push(self.WHILE)
        self.stack_while += 1   
        
        self.while_count += 1     
        
        self.loop_register('while')
        
        self.generic_visit(node)
        
        self.stack_while -= 1
        self.pop()
        
    def visit_DoWhile(self, node):
        self.push(self.DOWHILE)
        self.stack_dowhile += 1
        
        self.dowhile_count += 1 
        
        self.loop_register('dowhile')
        
        self.generic_visit(node)
        
        self.stack_dowhile -= 1
        self.pop()
        
    def visit_For(self, node):
        self.push(self.FOR)
        self.stack_for += 1
        
        self.for_count += 1 
        
        self.loop_register('for')
        
        self.generic_visit(node)
        
        self.stack_for -= 1
        self.pop()
        
    def visit_Goto(self, node):
        self.goto_count += 1
        self.generic_visit(node)
        
    def visit_If(self, node):
        self.push(self.IF)
        self.stack_if += 1
        
        if self.is_in_loop():
            self.cond_in_loops += 1
        else:
            self.cond_out_loops += 1
        
        self.generic_visit(node)
        
        self.stack_if -= 1
        self.pop()
        
    def visit_TernaryOp(self, node):
        
        if self.is_in_loop():
            self.cond_in_loops += 1
        else:
            self.cond_out_loops += 1
        
        self.generic_visit(node)
        
    def visit_Switch(self, node):
        self.push(self.SWITCH)
        self.stack_switch += 1
        
        if self.is_in_loop():
            self.cond_in_loops += 1
        else:
            self.cond_out_loops += 1
        
        self.generic_visit(node)
        
        self.stack_switch -= 1
        self.pop()
        
    def visit_ID(self, node):
        if self.visiting_arrayRef_count > 0:
            self.index_ids.append(node.name)
        
        """    
        if self.guard:
            print node.name
            (self.loops_list[-1]['guard_ids']).append(node.name)
        """
         
        self.generic_visit(node)
    
    def visit_Decl(self, node):
        """Visit declarations. Register the name of the var"""
        self.ids.append(node.name)
        if node.init:
            self.init_values[node.name] = self.check_init_value(node.init)

        self.generic_visit(node)
        
    def visit_Assignment(self, node):
        """Visits all assignement in order to find initialisations, bilding dict 
        of initial values.
        """
        
        if node.lvalue.name not in self.init_values:
            self.init_values[node.lvalue.name] = self.check_init_value(node.rvalue)
            #self.check_init_value(node.rvalue)
            
        self.generic_visit(node)
        
    def visit_ArrayRef(self, node):
        #FIXME: check this visit
        self.visiting_arrayRef_count += 1
        self.visit(node.subscript)
        self.visiting_arrayRef_count -= 1

    def visit_FuncCall(self, node):
        try:
            self.called_func.add(node.name.name)
        except:
            print "Impossible de trouver le nom de la fonction!\n"
        self.generic_visit(node)

    def check_init_value(self, node):
        """
        If numerical value -> return the value
        If variable -> return the variable
        If variable-1, return the string "variable-1" with the proper variable name
        """
        if node.__class__ == c_ast.Constant:
            return node.value
        elif node.__class__ == c_ast.ID:
            return  node.name
        else:
            if node.__class__ == c_ast.BinaryOp:
                requierements = (node.op == '-',
                                 node.right.__class__ == c_ast.Constant,
                                 node.right.value == '1',
                                 hasattr(node.left, "name"))
                if all(requierements):
                    return node.left.name + "-1"

            elif node.__class__ == c_ast.UnaryOp:
                requierements = (node.op == '-',
                                 node.expr.__class__ == c_ast.Constant)
                
                if all(requierements):
                    return "-" + node.expr.value
            
        return None
    
    def get_ids_set(self):
        return set(self.ids)

    def get_index_ids(self):
        return set(self.index_ids)
    
    def get_report(self):
        """
        Return a namedtuple containing sum up of information after code analysis.
        """
        
        Report = namedtuple('Report', (k for k,v in self.__dict__.iteritems() if not callable(v)))
        
        return Report(**{k : v for k,v in self.__dict__.iteritems() if not callable(v)})
        
        
class Statistics(object):
    """
    
    """
    
    
    def __init__(self, NodeVisitor=CodeStatistics()):
        """
        Args:
            NodeVisitor (c_ast.NodeVisitor) a visitor for the syntax tree (ast)
        """
        self.NodeVisitor=NodeVisitor
        self.parser = None
        
    def compute_report(self, function, decl_nbr=0, verbose=False):
        """
        Args:
            decl_nbr (int): nuber of the declaration (if several fct declared in a same file)
            
        """
        if not self.parser:
            self.parser = c_parser.CParser()
            
        ast = self.parser.parse(function, filename='<none>')
        
        if verbose:
            ast.show(attrnames=True)
        
        #FIXME : refactor this...
        self.NodeVisitor.reset();
        
        self.NodeVisitor.visit(ast.children()[decl_nbr][1])
        
        
        return self.NodeVisitor.get_report()
        
        
    
