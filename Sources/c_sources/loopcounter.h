/**
 *

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

 * @author Simon Liénardy <simon.lienardy@uliege.be>
 * @version 1.0 
 *
 * @section DESCRIPTION
 *
 * This is the easiest way to count the number of iterations in the loop :
 * while and for are transformed into macro. In the macro, a variable is 
 * incremented when the loop guardian is evaluated. the variable is an extern one. 
 * Hence, it can be accessed in a test code.
 *  
 * Prerequisites (to catch how it works):
 *  * Understanding of macro mechanism in C;
 *  * Understanding of Variadic Macros
 *  * Understanding of C buildding process; 
 *  * Knowledge of the comma operator in C
 *    expr1, expr2 -> expr1 and expr2 are evaluated in this order (guaranted), 
 *    the value of the total expression is the value of expr2 (hence expr1 is 
 *    usefull just for side effects);
 *
 * Use case:
 *  Imagine a student implemented a method "student_method()" declared in file 
 *  student.h.
 * 
 *  1) append this file to a copy of student.h :
 *  cat student.h.cpy loopcounter.h > student.h
 *  
 *  2) The line #include "student.h" in student's code will now also include 
 *  this header.
 *    
 *  3) in your test file :
 *  for_loopcounter = 0;   // must be reset cf. reset_counters();
 *  while_loopcounter = 0; // idem
 *  student_method()
 *  -> Here, you can use the value of for_loopcounter and while_loopcounter to 
 *     analyse the number of iterations taken by the student's code execution.
 *      
 *  4) macro for can make the compilation fail if third expression in the 
 *  	parentheses is left blank because expansion
 *     for(... ; , ++for_loopcounter) is incorrect
 *               ^
 *              bad
 *     
 *     Consider using
 *     	sed "s/\(for[[:blank:]]*(.*;[[:blank:]]*\)\()\)/\1 (0) \2/g" -i $file
 *     on the source file first
 *
 *  N.B. : for_loopcounter and while_loopcounter must be global variable declared 
 *  wherever you consider it relevant.
 *
 */

#ifndef COUNT_LOOP_H
#define COUNT_LOOP_H

/**
 * Macro to replace the loop condition of a while (or do...while) loop by a equivalent operation
 * that also counts the loop condition evaluations.
 *  
 * Variadic Macros to catch expressions using the comma operator or var decl 
 * allowed in std C99 in for loops. 
 */
#define while(...) while(++while_loopcounter, __VA_ARGS__)

/**
 * Macro to replace the third expression of a for loop by a equivalent operation
 * that also counts the for loop body evaluations.
 *  
 * Variadic Macros to catch expressions using the comma operator or var decl 
 * allowed in std C99 in for loops. 
 */
#define for(...) for(__VA_ARGS__ , ++for_loopcounter)

/**
 * Counter that counts the for loop bodies evaluations
 */
extern int for_loopcounter;

/**
 * Counter that counts the while and do...while loop condtions evaluations.
 */
extern int while_loopcounter;

/**
 * Self documenting name.
 */
static inline void reset_counters(){for_loopcounter = while_loopcounter = 0;}

/**
 * Access the counters and save them in the variables *fors and *whiles
 */
static inline void save_counters(int *fors, int *whiles)
{
   *fors = for_loopcounter; *whiles = while_loopcounter;
}

#endif

