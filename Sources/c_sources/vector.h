/**
 * CAFÉ - C implementation
 *
 * @author Simon Liénardy <simon.lienardy@uliege.be>
 * @version 1.0 
 *
 * @section LICENSE
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

 * @section DESCRIPTION
 *
 * This header defines macros and functions that will be used to detect Out Of Bound Error.
 * 
 * How it works:
 *
 * Arrays must be initialized thank to the new_tab function. This method seems to return an int *
 * BUT IT IS NOT TRUE. The new_tab function allocate a struct tab objet that will embed the array
 * that the user will eventually manipulate. The following operations were thought to hide this
 * behavior to the final user: this one can write a code that manipulate an array (let call it 'A')
 * without being aware that the real array is stored in a struc tab object that enables to count the
 * out of bound access atempts. Note that the actual array that is allocated with new_tab is always
 * larger than the user's array. It was meant to reduce the Segmentation Fault errors when indexing
 * Out Of Bounds array cells. It guarrantees that A[-1], A[N] (where N is user's array size) never fail
 * BUT are counted in the variable bad_access.
 *
 * Array accesses like:
 * 
 *   A[i + j]
 *
 * must first be tansformed into : A(i + j) thanks to e.g. 
 *   sed -i 's/\[/\(/g' $1
 *   sed -i 's/\]/\)/g' $1 
 * 
 * This header defines a macro that will convert A(i + j) into
 * (*get(A, (i + j)))
 *
 * This last method can count the Out Of Bounds accesses to A. As get function returns a pointer
 * to the (i + j + 1)th integer of A, the dereference (i.e. *get(...)) is the (i + j + 1)th
 * of the user's array. Hence, it is equivalent to the initial A[i + j] that was previously transformed.
 * 
 * Note: (i + j + 1)th because first index is 0.
 */ 

#ifndef INSIGNED
#define INSIGNED 

/**
 * This is black magic. It expands macros <Array name>(...) into a call to the function 
 *    get(<Array name>, (...))
 * and passes, as a second parameter, what the user expected as array index. The function call
 * returns a pointer that is dereferenced (the expanded macro can then be used as a L-value
 * or a R-value.
 *
 * for other array names, the receipe is:
 * #define <Array name>(...) (*get(<Array name>, (__VA_ARGS__)))
 *
 * @warning Do not use this if you did not understand the explainations.
 */
#define A(...) (*get(A, (__VA_ARGS__)))
#define B(...) (*get(B, (__VA_ARGS__)))
#define C(...) (*get(C, (__VA_ARGS__)))   

/**
 * Variable used to count the out of bound accesses in the arrays when calling
 * get function
 */
extern int bad_access;   

/**
 * Get an element in the user's array. Manipulate the (struct tab *) hidden behind a
 * (int *). Count the Out Of Bounds accesses in the variable bad_access
 *
 * @param (int *) A struct tab * hidden behind an int *
 * @param (int) The index in the user's array
 * @return a pointer to the element in the user's array at the desired index.
 * @warning This function is not meant to be called by the user
 */
int *get(int *, int);


/**
 * Get the user's array. Manipulate the (struct tab *) hidden behind a (int *). 
 *
 * @param (int *) A struct tab * hidden behind an int *
 * @return The length of the user's array
 * @warning This function is not meant to be called by the user
 * @note The 'student' comes from the fact this function was first developed to assess student's work.
 */
int *student_tab(int *);

/**
 * Get the length of the user's array. Manipulate the (struct tab *) hidden behind a
 * (int *). 
 *
 * @param (int *) A struct tab * hidden behind an int *
 * @return The length of the user's array
 * @warning This function is not meant to be called by the user
 * @note The 'student' comes from the fact this function was first developed to assess student's work.
 */
int student_tab_l(int *);


/**
 * Get the actual array. Manipulate the (struct tab *) hidden behind a
 * (int *). 
 *
 * @param (int *) A struct tab * hidden behind an int *
 * @return a pointer to the actual array, always larger than the user's array
 * @warning This function is not meant to be called by the user
 */
int *actual_tab(int *);

/**
 * Get the length of the actual array. Manipulate the (struct tab *) hidden behind a
 * (int *). 
 *
 * @param (int *) A struct tab * hidden behind an int *
 * @return The length of the actual array
 * @warning This function is not meant to be called by the user
 */
int actual_tab_l(int *);

// Duplicate array (do not use this: incomplete/deprecated
int* dup(int *a);

/**
 * Initialise a new 'struct tab' and return it as a int *
 * Use the function 'release' to free the allocated struct
 * 
 * @param (int) the length of the user's array
 * @return A struct tab *, hidden as an int *
 * @see vector.c
 * @see fucntion void release(int *)
 */
int *new_tab(int);

/*
 * Free the 'struct tab' hidden behind the int*
 * (Must be used to free struct allocated with new_tab)
 *
 * @param (int *) the struct tab * to free
 */
void release(int *);

/**
 * Get the offset between the first element in actual array and the first element of user's array.
 * Manipulate the (struct tab *) hidden behind a (int *). 
 *
 * Here is a drawing of the memory :
 *
 *      offset                           offset
 *    ____/\____                       ____/\____
 *   /          \                     /          \ 
 *   [0, ..., 0, [?, ?, ?, ?, ... , ?], 0, ..., 0]
 *    ^           ^
 *    |           |
 *    actual_tab  student_tab
 *
 * @param (int *) A struct tab * hidden behind an int *
 * @return The length of the actual array
 * @warning This function is not meant to be called by the user
 */
int get_offset();

#endif

