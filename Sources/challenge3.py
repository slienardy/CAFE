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

from commons.InvariantTest import Limit, make_limits_list_wFB
from commons.tools import fake_dict
from commons.HomeworkChecker import HomeworkChecker
import commons.HomeworkCorrector as hc
from code.CodeHandler import CodeHandler
from code.CodePreprocessor import CodePreprocessor
from commons.HomeworkCorrector import GroundTruth
from itertools import izip_longest
import commons.remarks_and_printing as rap
from commons.HierarchicalFbGenerator import HierarchicalFbGenerator
import sys
from code.Statistics import Statistics, CodeStatistics
import re


DEBUG=True

fonction_c = """#include <stdio.h>
#include <stdlib.h>
#ifndef CHECK
#include "loopcounter.h"
#include "vector.h"
#endif

void challenge3(int *A, int *B, int *C, const unsigned int N, const unsigned M, const unsigned L);

void challenge3(int *A, int *B, int *C, const unsigned int N, const unsigned M, const unsigned L)
{{
   {{
      {0}
   }}
}}

"""

# Used in several functions.
DICO_1 = ("different",
          "maximal",
          "browsed",
          "analyzed",
          "congruent",
          "extraterrestrial",
          "common",
          )

DICO_2 = ("Part A1",
          "Part A2",
          "Part B1",
          "Part B2",
          "Part C1",
          "Part C2",
          "Area 51",
          )

def deal_with_to_few_index(array, assumed_index):
        """Deal with the try/except in one function.
            (Pad with "???" values)
        """
        try:
            return str(array[assumed_index])
        except IndexError:
            return "???"

"""
│                                  │                                   │
├──────────────────────────────────┼───────────────────────────────────┤
│                                  │                                   │
╰──────────────────────────────────┴───────────────────────────────────╯
"""
def table_to_str(name, first, ind_prev, ind, last, size):
    """
    """
    
    indent = len(name) + 3
    content1 = " Part {}1 ".format(name)
    content2 = " Part {}2 ".format(name)
    
    l_ind1 = len(first) + len(ind_prev)
    l_ind2 = len(ind) + len(last) 
    
    l_content_1 = max(len(content1), (l_ind1 + 3))
    l_content_2 = max(len(content2), (l_ind2 + 3))
    
    bef1 = (l_content_1 - len(content1)) / 2
    aft1 = l_content_1 - len(content1) - bef1
    
    bef2 = (l_content_2 - len(content2)) / 2
    aft2 = l_content_2 - len(content2) - bef2
    
    
    line1 = "".join((" "*indent, "│", first, " "*(l_content_1 - l_ind1), ind_prev, "│", ind, " "*(l_content_2 - l_ind2), last, "│", size))
    line2 = "".join((" "*indent, "├", "─"*l_content_1, "┼", "─"*l_content_2, "┤"))
    line3 = "".join((" ", name, ": ", "│", " "*bef1, content1, " "*aft1, "│", " "*bef2, content2, " "*aft2, "│"))
    line4 = "".join((" "*indent, "╰", "─"*l_content_1, "┴", "─"*l_content_2, "╯"))    

    return "\n".join((line1, line2, line3, line4))

def affichage_invariant(limit_list):
    """
        Display the Invariant
    """
    NB_TEXTS = 19

    texts = [deal_with_to_few_index(limit_list, i) for i in range(NB_TEXTS)]

    comment = "and the values that are {} to the {} and to the {} are in the {}\n".format(fake_dict(DICO_1, texts[15]),
                                                                               fake_dict(DICO_2, texts[16]),
                                                                               fake_dict(DICO_2, texts[17]),
                                                                               fake_dict(DICO_2, texts[18]),)

    return """{}\n{}\n{}\n{}""".format(table_to_str("A", texts[0], texts[1] , texts[2], texts[3] , texts[4]),
                                       table_to_str("B", texts[5], texts[6] , texts[7], texts[8] , texts[9]),
                                       table_to_str("C", texts[10], texts[11] , texts[12], texts[13] , texts[14]),
                                       comment)



class GT_Homework3(GroundTruth):

    def __init__(self, num, name):
        """
        
        """
        super(GT_Homework3, self).__init__(num, name, None)
        self.stats = Statistics(CodeStatistics())
        self.structure = [
        {'name'   : "", # This is deprectaed
         'action' : self.statement_respect,
         'params' : {},
         'weight' : None #useless
        
        },    
        {'name' : '',
         'action' : self.correct_invariant,
         'params' : {},
         'weight' : 10,
         },  #
        {'name' : '',
         'action' : self.correct_fct_term,
         'params' : {},
         'weight' : 2,
        },
        {'name' : '',
         'action' : self.correct_output,
         'params' : {},
         'weight' : 4.0,
         },  #
        {'name' : '',
         'action' : self.correct_output_particular,
         'params' : {},
         'weight' : 2.0,
         },  #
        {'name'  : "",
         'action': self.correct_nb_iterations,
         'params': {},
         'weight': 2.0,
        },
        ]
        """
        There are :
        2 texts
        1 code with 3 test.
        So order is : text1, text2, code, test1, test2, test3
        Code report will be computed in inv1, stored after this.
        """
        self.requierments = (2, 0, 1, (4, 5, 6), 3, 6) # 3 and 4 reordered, 3 is N = 0

    @staticmethod
    def grades_mean(grades, weights):
        grades = tuple(grades)
        weights = tuple(weights)
        
        if DEBUG:    
            print grades, weights
        
        theo = sum((g * w for g,w in zip(grades[1:3], weights[1:3])))
        
        code = sum((g * w for g,w in zip(grades[3:], weights[3:]))) 
        
        return theo + (code * grades[0])
    
    def statement_respect(self, code, **args):
        """
        
        """
        coms = [rap.title("Compliance with the instructions and constrains")]
        
        self.report = None
        
        try:
            self.report = self.stats.compute_report(code, 0, False)
        except Exception:
            coms.append(rap.remark("AACode", 1500, "An error occured during the code analysis\n"))
            return 0, coms
        
        rep = self.report
        
        if sum((rep.while_count, rep.for_count, rep.dowhile_count)) > 1:
            coms.append(rap.remark("ALoopInv", 500, "The code does not comply with the number of loop constrain!\n\n"
                                   "Therefore, your grade for the implementation part is 0.\n"))
            return 0, coms
        
        if sum((rep.return_in_loop, rep.continue_in_loop, rep.break_in_loop, rep.goto_count)) != 0:
            coms.append(rap.remark("AGotoEtc", 500, "The code contains break-like instructions like \"break\", \"continue\" or \"goto\"\n\n"
                                                    "Therefore, your grade for the implementation part is 0.\n"))
            return 0, coms
        
        if self.report.called_func:
            coms.append(rap.remark("AEnonce", 500, "The code calls the following functions: {}\nThis is forbidden for this Challenge!\n".format(",".join((s for s in self.report.called_func)))))
  
            return 0, coms
              
        coms.append(rap.disp_msg(self.get_positive()))
        
        return 1, coms
    
    def correct_invariant(self, actual, **args):
        """
        
        """
        #Some decl.
        NO = Limit.NO
        MINUS = Limit.MINUS
        TOTAL = 10.0
        grade = TOTAL
        
        BAD_INV_PRIO = 40 # If #failure is high, will be event. > 350
        
        raw_limits = actual
        
        coms = [rap.title("Graphical Loop Invariant Correction")]
        
        C = coms.append
        R = rap.remark
        D = rap.disp_msg
        
        limits_list, com_lim = make_limits_list_wFB(raw_limits)
        
        C(D("\n".join(("Here is how the system understood your Invariant:\n",
                       affichage_invariant(limits_list),
                       '',))
                       ))
        
        if com_lim:
            C(R("AEncodage", 100, com_lim))
        
        
        
        
        #var decl. to be used in the following
        
        Astart = limits_list[0]
        Aprev  = limits_list[1]
        Aindex = limits_list[2]
        Alast  = limits_list[3]
        Asize  = limits_list[4]
        
        Bstart = limits_list[5]
        Bprev  = limits_list[6]
        Bindex = limits_list[7]
        Blast  = limits_list[8]
        Bsize  = limits_list[9]
        
        Cstart = limits_list[10]
        Cprev  = limits_list[11]
        Cindex = limits_list[12]
        Clast  = limits_list[13]
        Csize  = limits_list[14]
        
        epith  = limits_list[15]
        src1   = limits_list[16]
        src2   = limits_list[17]
        inter  = limits_list[18]
        
        # Invariant's correction
        
        fb_inv_needed = 0.0
        self.vars = {"A" : None,
                     "B" : None,
                     "C" : None}
        
        if len(limits_list) > 19:
            coms.append(rap.remark("AEncodage", 100, "You must encode 19 boxes.\n"))
            return (0, coms)
        
        def test_one_tab(start, prev, index, last, size, correct_size, name, offset):
            C(D("\nAbout the array {}:\n──────────────────\n".format(name)))
            TOTAL = 3.0
            grade = TOTAL
            fb_inv_needed = 0
            
            # mandatory
            if start != Limit(0, NO):
                C(D("Box {}: Wrong content! Array indeces all start at...\n".format(0 + offset)))
                grade -= 1
                fb_inv_needed += BAD_INV_PRIO
                
            if size != Limit(correct_size, NO):
                C(D("Box {}: Wrong content! The array size is expected.\n".format(4 + offset)))
                grade -= 1
                fb_inv_needed += BAD_INV_PRIO
                
            if not(index.is_var() and index.modif == NO):
                C(D("Box {}: An array index is expected here!\n".format(2 + offset))) 
                grade -= 1
                fb_inv_needed += BAD_INV_PRIO
            else:
                C(D("Box {}: [INFO] A variable was detected: {}\n".format(2 + offset, index.symbol)))
                self.vars[name] = index.symbol
            
            if prev.is_var() and prev.modif == NO:
                C(D("Box {}: Considering the arrays sizes types (unsigned int), it is highly recommended to NOT\n"
                    "   put the variable on this side of the division bar!\n".format(1 + offset)))
            
            # not mandatory
            if not(prev.is_unspecified() or (prev == Limit(index.symbol, MINUS))):
                C(D("Box {}: The content of this Box MUST be related to the content of the Box {}\n"
                    "   (and this last one should be correct too).\n".format(1 + offset, 2 + offset)))
                grade -= 0.5
                fb_inv_needed += BAD_INV_PRIO / 2
            
            if not(last.is_unspecified() or (last == Limit(correct_size, MINUS))):
                C(D("Box {}: Wrong content! The last array index is expected here.\n".format(5 + offset)))
                grade -= 0.5
                fb_inv_needed += BAD_INV_PRIO / 2
            
            C(D("\n"))
            
            return max(0.0, grade / TOTAL), fb_inv_needed
        
        test, fbn = test_one_tab(Astart, Aprev, Aindex, Alast, Asize, "N", "A", 1)
        fb_inv_needed += fbn
        grade -= (1 - test) * 2
        
        test, fbn = test_one_tab(Bstart, Bprev, Bindex, Blast, Bsize, "M", "B", 6)
        fb_inv_needed += fbn
        grade -= (1 - test) * 2 
        
        test, fbn = test_one_tab(Cstart, Cprev, Cindex, Clast, Csize, "L", "C", 11)
        fb_inv_needed += fbn
        grade -= (1 - test) * 2 
        
        C(D("\nBoxs remainder:\n───────────────\n"))
        
        # Boxs 16 to 19 relevance test
        
        clean = True
        
        if epith != Limit(7, NO):
            C(D("Box 16: The instructions does not mention \"{}\" values.\n".format(fake_dict(DICO_1, epith.symbol))))
            grade -= 0.25
            fb_inv_needed += BAD_INV_PRIO / 4.0
            clean = False
        
        if not ((src1 == Limit(1, NO) and src2 == Limit(3, NO)) 
            or (src2 == Limit(1, NO) and src1 == Limit(3, NO))):
            C(D("Box 17 and 18: The parts already treated (according to the drawing in A and B) must be specified.\n"))
            grade -= 0.5
            fb_inv_needed += BAD_INV_PRIO / 2.0
            clean = False
            
        if inter != Limit(5, NO):
            C(D("Box 19: Where is stored the result?\n"))
            grade -0.25
            fb_inv_needed += BAD_INV_PRIO / 4.0
            clean = False
        
        if clean:
            C(D(self.get_positive() + "\n"))
        
        if fb_inv_needed :
            coms.append(rap.add_ffwd("AInvFail", fb_inv_needed))
        
        # Test des variables dans le code
        
        C(D("\nCode analysis:\n──────────────"))
        
        if not self.report:
            coms.append(rap.disp_msg("The code analysis has failed. This was previously mentioned.\n"))
            grade -= 2
            return (grade / TOTAL, coms)
        else:
            init_dict = self.report.init_values
         
        
        def check_init(name, val_init):
            init = self.vars[name]
            
            malus = 0.0
            
            if init:
                if init not in init_dict:
                    C(R("AInvInit", 200, "\n-> The variable {} does not seem to be present in the code.\n".format(init)))
                    malus += 1
                elif init_dict[init] != val_init:
                    C(R("AInvInit", 100, "\n-> The variable {} does not seem to be initialized according to the Loop Invariant.\n".format(init)))
                    malus += 0.5
                else:
                    C(D("\n=> The code and the Loop Invariant matches, as the initialisation of {} is concerned.\n".format(init)))
                
            else:
                C(D("\nAs it stands, your Invariant cannot be confronted with the code for the array {}.\n".format(name)))
                malus += 1
            
            return malus
                
        # Variable parcourant A
        grade -= check_init("A", '0')
        
        # Variable parcourant B
        grade -= check_init("B", '0')
        
        # Variable parcourant C
        grade -= check_init("C", '0')
        
    
        return (grade / TOTAL, coms)
    
    
    def correct_fct_term(self, actual, **args):
        
        coms = [rap.title("Loop Variant")]
        
        if not self.report:
            coms.append(rap.disp_msg("The code analysis has failed. This was previously mentioned.\n"))
            return (0, coms)
        
        TOTAL = 3.0
        grade = 3.0
        
        fb_fct_t = 0
        FB_STEP = 20
        
        C = coms.append
        R = rap.remark
        D = rap.disp_msg
        
        ids =  re.findall(r"[a-zA-Z_]\w*", actual)
        ids_in_guard = self.report.loops_list[0]['ids']
        
        go_on = True
        
        # Une fonction t est construite sur base des variables du programme.
        
        for i in ids:
            if i not in ids_in_guard:
                C(D("The identifier {} does not seem to appear in the loop condition.\n".format(i)))
                fb_fct_t += FB_STEP
                go_on = False
                
        varA = self.vars['A']
        varB = self.vars['B']
        
        if not(varA in ids and varB in ids):
            C(D("The variables {} and/or {} does not appear in the Loop Variant expression,\n"
                "this is a problem\n".format(varA, varB)))
            fb_fct_t += FB_STEP
            go_on = False
        
        if not go_on:
            C(R("AFCTT", fb_fct_t, "Continuing to test the Loop Variant is not possible.\n"))
            return 0, coms
                
        # Computaiotn of several values.
        
        def compute_t(values):
            try:
                val = eval(actual, {}, values)        
            except Exception as e:
                if DEBUG:
                    print actual, values
                return None
        
            return val
        
        tests = (
                {varA :  0, varB :  0,  'N' : 100.0, 'M' : 50.0, 'L' : 50.0},
                {varA : 99, varB : 49,  'N' : 100.0, 'M' : 50.0, 'L' : 50.0},
                {varA : 10, varB : 10,  'N' : 100.0, 'M' : 50.0, 'L' : 50.0},               
                {varA : 11, varB : 10,  'N' : 100.0, 'M' : 50.0, 'L' : 50.0},
                {varA : 10, varB : 11,  'N' : 100.0, 'M' : 50.0, 'L' : 50.0},
                )
        
        results = [compute_t(v) for v in tests]
        
        if any(r is None for r in results):
            C(R("AAssist", 1000, "Something went wrong when calculating the value of the Loop Variant\n."))
            return 0, coms
        
        integer_test = [isinstance(v, float) and v.is_integer() for v in results]
        
        # Entier
        if not all(integer_test):
            fb_fct_t += 2 * FB_STEP
            C(D("Your Loop Variant does not seem to be an integer function.\n"))
        
        # Positif si B
        if not all(r > 0 for r in results):
            fb_fct_t += 2 * FB_STEP
            C(D("Your Loop variant does not seem to be always positive if the loop condition is true!\n"
                "-> Check all the possible cases.\n"))
        
        # Décroissance (I love that)
        if not(results[3] < results[2]):
            fb_fct_t += 3 * FB_STEP
            C(D("If between 2 iterations, the value of {} is increasing, the value of the Loop Variant should be decreasing.\n".format(varA)))
        
        if not(results[4] < results[2]):
            fb_fct_t += 3 * FB_STEP
            C(D("If between 2 iterations, the value of {} is increasing, the value of the Loop Variant should be decreasing.\n".format(varB)))
            
        
        if fb_fct_t:
            C(rap.add_ffwd("AFCTT", fb_fct_t))
            return 0, coms
        else:
            C(D(self.get_positive()))
        
        return grade / TOTAL, coms
        

    def correct_output(self, actual, **args):
        """
        
        """
        coms = [rap.title("Code execution")]
        
        C = coms.append
        R = rap.remark
        D = rap.disp_msg
        
        inter, w_inter, max_iter = actual
        
        def correct_one(text, context):
        
            C(D(context))
            
            return_code, text_output = text
            
            if return_code == 124:
                
                coms.append(rap.remark("AInfinity", 300, "The execution of your code generates an infinite loop: correction impossible!\n"))
                return 0
             
            elif return_code != 0:
                coms.append(rap.remark("AAssist", 200, "The code execution failed due to an error.\n"))
                return 0
            
            
            lines = text_output.splitlines()
            
            N = lines[0]
            M = lines[1]
            A = lines[2]
            B = lines[3]
            Corr = lines[4]
            Stu  = lines[6]
            bad_access = int(lines[8])
            Results = [int(i) for i in lines[9].split()]
            
            Disp_tab = "".join(("With ", N, ", ", M, "\nA : [", A, "]\nB : [", B, "]\n"))
            compa    = "".join(("Expected result : [", Corr, "]\n",
                                "Your result     : [", Stu , "]\n"))
            
            if bad_access != 0:
                C(R("ABadArray", 500, "An array Out Of Bound Error was detected! This is one of the most dangerous bugs in the world!\n"
                                      "The arrays were:\n{}".format(Disp_tab)))
                return 0
            
            if Results[0] != 0 or Results[1] != 0:
                C(R("AEnonce", 300, "It seems that you modify the array(s) A and/or B. This is forbidden.\n"))
                return 0
            
            if Results[2] != 0 :
                C(R("AResult", 350, "Your code does not provide the expected result:\n" + Disp_tab + compa))
                return 0
            
            else:
                C(D(self.get_positive()))
            
            return 1
        
        grade = (correct_one(inter, "\nWhen the array C is not empty (there are common values in A and B):\n\n")
                 * correct_one(max_iter, "\nWhen there is only a single common value:\n\n")
                 * correct_one(w_inter, "\nWhen the array C is empty (no common value between A and B):\n\n"))
        
        self.ok_code = grade == 1
        
        return (grade, coms)
        
    def correct_output_particular(self, actual, **args):
        """
        Particular case : N = 0
        """
        
        coms = [rap.title("Particular case: M = 0 and N = 0")]
        
        C = coms.append
        R = rap.remark
        D = rap.disp_msg
        
        return_code, text_output = actual
            
        if return_code == 124:
            
            coms.append(rap.remark("AInfinity", 300, "The execution of your code generates an infinite loop: correction impossible!\n"))
            return 0, coms
         
        elif return_code != 0:
            coms.append(rap.remark("AAssist", 200, "The code execution failed due to an error.\n"))
            return 0, coms
        
        if not self.ok_code:
            C(D("A code that only handles the particular case and not the general case is useless...\n"))
            return 0, coms
        
        
        lines = text_output.splitlines()
        
        N = lines[0]
        M = lines[1]
        A = lines[2]
        B = lines[3]
        Corr = lines[4]
        Stu  = lines[6]
        bad_access = int(lines[8])
        Results = [int(i) for i in lines[9].split()]
        
        Disp_tab = "".join(("With ", N, ", ", M, "\nA : [", A, "]\nB : [", B, "]\n"))
        compa    = "".join(("Expected result : [", Corr, "]\n",
                            "Your result     : [", Stu , "]\n"))
        
        if bad_access != 0:
            C(R("ABadArray", 500, "An array Out Of Bound Error was detected! This is one of the most dangerous bugs in the world!\n"
                                      "The arrays were:\n{}".format(Disp_tab)))
            return 0, coms
        
        if Results[0] != 0 or Results[1] != 0:
            C(R("AEnonce", 300, "It seems that you modify the array(s) A and/or B. This is forbidden.\n"))
            return 0, coms
        
        if Results[2] != 0 :
            C(R("AValPart", 350, "Your code does not provide the expected result:\n" + Disp_tab + compa))
            return 0, coms
        
        else:
            C(D(self.get_positive()))
            
        return 1, coms

    def correct_nb_iterations(self, actual, **args):
        """
        """
        
        
        return_code, text_output = actual
        
        coms = [rap.title("Iterations count")]
        
        C = coms.append
        R = rap.remark
        D = rap.disp_msg
        
        if return_code == 124:
            
            coms.append(rap.remark("AInfinity", 300, "The execution of your code generates an infinite loop: correction impossible!\n"))
            return 0, coms
         
        elif return_code != 0:
            coms.append(rap.remark("AAssist", 200, "The code execution failed due to an error.\n"))
            return 0, coms
        
        if not self.ok_code:
            C(D("There is no point in testing this if the code is not correct...\n"))
            return 0, coms
        
        lines = text_output.splitlines()
        N = int(lines[0].split()[2])
        M = int(lines[1].split()[2])
        nb_it_stu = max(int(i) for i in lines[7].split())
        A = lines[2]
        B = lines[3]
        
        Disp_tab = "".join(("Avec N = ", str(N), ", et M = ", str(M), "\nA : [", A, "]\nB : [", B, "]\n"))
        
        if nb_it_stu > N + M:
            C(R("ATours", 50, "{}\nYour code generates {} iterations while the maximal limit is {}\n".format(Disp_tab,
                                                                                                                 nb_it_stu,
                                                                                                                 N + M)))
            return 0, coms 
        else:
            coms.append(rap.disp_msg("If N = {}, M = {}, there are {} iterations: {}"
                                     "".format(N, M, nb_it_stu, self.get_positive())))
            
        return 1, coms

    @staticmethod
    def poc_format(code):

        template = """int main(void){{
        const unsigned int N = 20;
        const unsigned int M = 20;
        const unsigned int L = 20;
        int A[N];
        int B[M];
        int C[L];
        
        
        {0}
        
        }}
        """

        return template.format(code)

# End class GT_Homework3
###############################################################################

def main(args):
    """Main method 
    
    Args: 
        args (dict): that were given as parameters to the script.
    """
    # Param handling
    # Will provide student_file
    student_file = args[1]

    c_h = CodeHandler()
    
    compile_dir = "companion3/c_sources/"
    
    if DEBUG:
        compile_dir = "../../c_sources/"

    params = {'template' : fonction_c, 'code_name' : 'test.c',
              'compile_dir' : compile_dir, 'exec_name' : "main",
              'nb_tests' : 4, 'format' : GT_Homework3.poc_format,
              'poc_mask' : [0, 0, 1], 'gap_number' : 1, }

    prep = CodePreprocessor(c_h, **params)
    
    fb_gen = HierarchicalFbGenerator()
    
    hwk_ckr = HomeworkChecker(hc.HomeworkCorrector(fb_gen, DEBUG=DEBUG),
                              prep,
                              GT_Homework3(3, "03"))
    
    
    hwk_ckr.handle_submission(student_file)


if __name__ == '__main__':
    
    if DEBUG:
        main(["", "../../Test/_2018/Challenge3/fct_t.txt"])
    else:
        sys.exit(main(sys.argv))
    
    
