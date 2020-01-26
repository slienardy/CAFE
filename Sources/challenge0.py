
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

import commons.HomeworkCorrector as hc
from commons.HomeworkChecker import HomeworkChecker
import sys
import math
from commons.HierarchicalFbGenerator import HierarchicalFbGenerator
import commons.remarks_and_printing as rap
import random as ran

debug = False
__profile__ = False

class GT_Homework0(hc.GroundTruth):
    """
     
    """
    
    def __init__(self, num, name):
        super(GT_Homework0, self).__init__(num, name, None)
        self.structure = [
         {'name'  : 'Q0 - The answer is \"white\"',
          'action': self.check_string,
          'params': {'correct': 'white',
                     'title' : 'Q0 - The answer is \"white\"',
                     'remark' : ("AEnonce", 350, "Please type the word \"white\".", 0),},
          'weight': 0.0
          },
         {'name'  : 'Q1 - 74 x 48 - Russian peasant way',
          'action': self.check_russian_mul, 
          'params': {'russia': [[74,48,0,0],[148,24,0,0],[296,12,0,0],[592,6,0,0],[1184,3,1,1184], [2368,1,1,3552]],
                     'title' : 'Q1 - 74 x 48 - Russian peasant way'},
          'weight': 6.0
          },
         {'name'  : 'Q1 - 34 x 23 - Russian peasant way',
          'action': self.check_russian_mul, 
          'params': {'russia': [[34,23,1,34],[68,11,1,102],[136,5,1,238],[272,2,0,238], [544,1,1,782]],
                     'title' : 'Q1 - 34 x 23 - Russian peasant way'},
          'weight': 6.0
          },
         {'name'  : 'Q2 - 842 to binary notation',
          'action': self.check_string,
          'params': {'correct': '0000001101001010',
                     'title'  : 'Q2 - 842 to binary notation',
                     'remark' : ("C0.4.2", 50, "The conversion is incorrect", 0),
                     },
          'weight': 2.0
          },
         {'name'  : 'Q2 - 842 as a sum of powers of 2',
          'action': self.check_sum , 
          'params': {'terms': [2,8,64,256,512],
                     'title': 'Q2 - 842 as a sum of powers of 2',},
          'weight': 2.0
          },
         {'name'  : 'Q2 - 3242 to binary notation',
          'action': self.check_string,
          'params': {'correct': '0000110010101010',
                     'title'  : 'Q2 - 3242 to binary notation',
                     'remark' : ("C0.4.2", 50, "The conversion is incorrect", 0),
                     },
          'weight': 2.0
          },
         {'name'  : 'Q2 - 3242 as a sum of powers of 2',
          'action': self.check_sum, 
          'params': {'terms': [2,8,32,128,1024,2048],
                     'title': 'Q2 - 3242 as a sum of powers of 2'},
          'weight': 2.0}
        ]
        
    POSITIVE = ('OK!\n', 'Perfect!\n', 'Great!\n', 'Correct!\n')
    
    @staticmethod
    def check_string(actual, **args):
        """
        Comparation of string
        """
        # First display the title
        i = 1
        com = [rap.title(args['title'], 1)]
        
        ground_truth = args['correct']
        
        i += 1
        grade = 0
        
        if (ground_truth == actual.lower()):
            com.append(rap.disp_msg(ran.choice(GT_Homework0.POSITIVE), i))
            grade = 1
        else: 
            com.append(rap.remark(*(args['remark'])))
                       
        return (grade, com)
    
    @staticmethod
    def check_sum(actual, **args):
        """Check the terms in a sum representation
        
        The string parameter should represent a sum of integer. This code check
        if the terms of the sum are correct and give a grade.
        
        Args:
            actual (string): a string representing a sum (numbers separed by '+'
                sign.
        
        Keywords Args:
            terms (list of int): sorted list of terms
        """
        #FIXME
        com = [rap.title(args['title'], 1)]
        
        grade = 1
        
        if debug:
            print repr(actual)
        
        terms = args['terms']
        
        try:
            actual_term  = [int(s.strip()) for s in actual.split('+')]
            
        except ValueError:
            grade = 0
            com.append(rap.remark("C0.4.2", 50, "Error in the sum expression. You must type numbers that are"
                    "separated with a '+'. Check your answer!\n", 0))
            return (grade, com)
        
        if terms == sorted(actual_term):
            com.append(rap.disp_msg(ran.choice(GT_Homework0.POSITIVE), 0))
        else:
            grade = 0
            com.append(rap.remark("C0.4.2", 50, "The sum is not correct\n", 0))
            
        return (grade, com)
        
    @staticmethod
    def check_russian_mul(actual, **args):
        """Check russian multiplication correctness
        
        This check the russian multiplication proposed by the student. The 
        proposition is intended to be a string that is parsed by this function. 
        
        Checking computed:
            * Correct parsing 
            * Proposition answers to the question
            * Table size
            * Multiplication per 2 of multiplicand
            * Reminders calculation
            * Table correctness
            * Final result correctness
        
        Args:
            actual (string):
            
        Keyword Args:
            russia (list of list of int): representing a 2D array (list of 
                lines) of size n * 4. n is the number of lines and can vary 
                whereas the number of column (4) should be fixed. The table
                a | b | c | d
                e | f | g | h
                is hence represented as [[a,b,c,d],[e,f,g,h]]
        
        Returns:
            (int): a grade (over 1).
            (string): a french commentary that gives feedback about the 
                correctness oth the student's proposal
        """
        #FIXME
        com = [rap.title(args['title'], 1)]
        append = com.append
        
        # Get the structure from the answer
        russia_table = args['russia']
        
        """
        PARTIE I : data parsing and elementary tests
        """
        
        if debug:
            print repr(actual)
        
        
        # Recover the proposed table from the string
        try:
            actual_table =[[int(i.strip()) for i in t.split('|')] for t in actual.splitlines()]
        except ValueError:
            append(rap.remark("AEnonce", 200, "An error occured with the Russian peasant multiplication\n"
                    "You typed:\n\"{}\"\n".format(actual), 0))
            return (0, com)
        
        # Test 1 : premier multiplicande et multiplicateur correct
        try:
            if not ((actual_table[0][0] == russia_table[0][0] and actual_table[0][1] == russia_table[0][1])
                    or (actual_table[0][0] == russia_table[0][1] and  actual_table[0][1] == russia_table[0][0])):
                append(rap.remark("AEnonce", 200, "The first multiplier and/or the first multiplicand"
                        " are incorrect. Check you are computing the right operation."
                        "\nYou were asked: {} x {}\n".format(russia_table[0][0], russia_table[0][1]), 0))
                return (0, com)
        except IndexError:
            append(rap.remark("AEnonce", 200, "Format error for the Russian peasant multiplication\n"
                    "You typed:\n\"{}\"\n".format(actual), 0))
            return (0, com)
        
        length = int(math.floor(math.log(actual_table[0][1], 2)) + 1)
        
        # Test 2 : tables de longueur correcte :
        if len(actual_table) != length:
            append(rap.remark("AEnonce", 200, "The table length is not correct. Do you divide properly the multiplier?\n", 0))
            return (0, com)
            
        # Test 2b : vérifier qu'il y a bien 4 valeur par ligne :
        if not all(len(line) == 4 for line in actual_table):
            append(rap.remark("AEnonce", 200, "The table width is incorrect: there must be 4 columns:"
                    " Multiplicand, multiplier, Remainder and partial sum. In that order!", 0))
            return (0, com) 
        
        """
        PARTIE II : deeper tests
        """
        score = 10
        #com = ""
        
        # Test 3 : multiplicande est multiplié par 2 à chaque ligne
        mul2 = all(actual_table[i][0] == 2 * actual_table[i-1][0] 
                   for i in range(1, length))
        
        if not mul2:
            append(rap.remark("ARUS_MUL", 75, "The multiplicand must be multiplied by 2 from a row to another.\n",0))
            score -= 2.5
            
        # Calcul des reste sont corrects
        reminders = all(line[2] == line[1] % 2  for line in actual_table)
        
        if not reminders:
            append(rap.remark("ARUS_MUL", 75, "The remainders are not properly computed\n", 0))
            score -= 2.5
            
        # Calcul des multiplicateurs divisés
        multi = all(actual_table[i][1] == actual_table[i-1][1] // 2
                    for i in range(1, length))
        
        # Vérification des sommes partielles
        sum_part = (all((actual_table[i][3] == actual_table[i-1][3] + actual_table[i][2] * actual_table[i][0])  
                       for i in range(1, length)) 
                    and  actual_table[0][3] == actual_table[0][2] * actual_table[0][0])
        
        if not (multi and sum_part):
            append(rap.remark("ARUS_MUL", 75, "There are error in the table (concerning multiplicands or partial sum)\n",0))
            score -= 2.5
        else:
            append(rap.disp_msg("Partial sums are correct.\n", 0))
        
        # Résultat final est correct
        # Index -1 is the last elem... 
        if actual_table[length-1][3] != russia_table[-1][-1]:
            append(rap.remark("ARUS_MUL", 75, "The final result is incorrect.\n",0))
            score -= 2.5
        else: 
            append(rap.disp_msg("The final result is correct.\n", 0))
            
        return (score / 10.0, com)


def main(args):
    """Main method 
    
    Args: 
        args (dict): that were given as parameters to the script.
    """
    # Param handling
    # Will provide student_file and student_id
    if debug :
        student_file = "../Test/_2018/Challenge_0/Challenge_0.txt"
    else:
        student_file = args[1]
    
    """
    Here we can put instruction to build FB Generator and pass it to the HomeworkCorrector
    fb_gen = HierarchicalFbGenerator(...)
        hwk_ckr = HomeworkChecker(hc.HomeworkCorrector(fb_gen), ...
    """
    fb_gen = HierarchicalFbGenerator()
    
    hwk_ckr = HomeworkChecker(hc.HomeworkCorrector(fb_gen),
                              hc.HomeworkPreprocessor(),
                              GT_Homework0(0, "00"))
    
    hwk_ckr.handle_submission(student_file)
    

if __name__ == '__main__':
    if __profile__:
        import cProfile
        cProfile.run('sys.exit(main(sys.argv))', sort='cumtime')
    else:
        sys.exit(main(sys.argv))
    
