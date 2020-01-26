/**
 *
@author Simon Liénardy <simon.lienardy@uliege.be>

@section LICENSE

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

 @section DESCRIPTION
 
C Implementation for the Challenge 3
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "vector.h"
#include "loopcounter.h"

#define MIN_VAL -100
#define MAX_VAL 100

void test(unsigned int N, unsigned int M, int inter_empty, int max_iter);
void challenge3(int *A, int *B, int *C, const unsigned int N, const unsigned M, const unsigned L);
int rand_range(double min, double max);
void print_tab(const unsigned int N, int tab[N+1]);
int *init_tab(const unsigned int size, int min_val, int max_val);
void rand_sorted_tab(int* t, int size, int min);
int *duplicate(const unsigned int size, int *src);
void intersect(const unsigned int N, const unsigned int M, unsigned int *L, int *S1, int *S2, int *D);

int *duplicate(const unsigned int size, int *src)
{
	int *tab = (int *) malloc(size * sizeof(int));

	tab = memcpy(tab, src, size * sizeof(int));

	return tab;
}

void intersect(const unsigned int N,
               const unsigned int M,
               unsigned int *L,
               int *S1,
               int *S2,
               int *D
              )
{
	unsigned int i = 0, j = 0, k = 0;
   
   while(i < N && j < M)
   {
      if(*(S1 + i) == *(S2 + j)){
         *(D + k) = *(S1 + i);
         ++k;
         ++i;
         ++j;
      }
      else if(*(S1 + i) < *(S2 + j))
      {
         ++i;
      }
      else
         ++j; 
   }
   
   *L = k;
}

int rand_range(double min, double max)
{
	/* Not the best but still better than modulo */
	return ((double) rand() / ((double) RAND_MAX+1)) * (max-min+1) + min;
}

int *init_tab(const unsigned int size, int min_val, int max_val){

	int *tab = (int *) malloc(size * sizeof(int));

	for(unsigned int i = 0; i < size; ++i)
		tab[i] = rand_range(min_val, max_val);

	return tab;
}

void print_tab(const unsigned int N, int *tab)
{

	for(unsigned int i = 0; i < N; ++i)
      if(tab[i])
		   printf(" %3d", tab[i]);
      else
         printf("  ? ");

	printf("\n");
}

void rand_sorted_tab(int* t, int size, int min)
{
   int j = min;
   
   for (int i = 0; i < size; (void)(0))
   {
      if(rand()>(RAND_MAX/2))
      {
         t[i] = j;
         ++i;
      }
      j += (int) rand_range(1, 3);
   }
}

void test(unsigned int N, unsigned int M, int inter_empty, int max_iter)
{
   // 1. Array declarations;
   int *A = new_tab(N);
   int *B = new_tab(M);
   unsigned int L = (N > M) ? N : M;
   int *C = new_tab((N > M) ? N : M);
   
   // Save pointers:
   int *stu_A = student_tab(A);
   int *stu_B = student_tab(B);
   int *stu_C = student_tab(C);
   
   // 2. Arrays A and B initialisation:
   rand_sorted_tab(stu_A, N, (int) rand_range(2, 3));
   if(inter_empty)
      rand_sorted_tab(stu_B, M, stu_A[N-1] + 1);
   else if(max_iter)
   {
      rand_sorted_tab(stu_B, M, stu_A[N-1]);
      stu_A[N-1] = stu_B[M-1];
   }
   else // inter non empty (if possible).
      rand_sorted_tab(stu_B, M, (int) rand_range(1, 3));
   
   int *cpy_A = duplicate(actual_tab_l(A), actual_tab(A));
   int *cpy_B = duplicate(actual_tab_l(B), actual_tab(B));
   int *correct = duplicate(actual_tab_l(C), actual_tab(C));    
   
   int offset = get_offset();   

   int fors, whiles;
   
   // Expected result computation
   unsigned int K = 0;
   reset_counters();
   intersect(N, M, &K, stu_A, stu_B, correct + offset);
   save_counters(&fors, &whiles);
   
   
   // 3. Student's code execution:

   // Disp before launch
   printf("N = %2u\n", N);
   printf("M = %2u\n", M);
   print_tab(N, stu_A);
   print_tab(M, stu_B);
   print_tab(L, correct + offset); // Correction
   printf("%d %d\n", fors, whiles); // Correction too

   // Actual student code launch.
   reset_counters();
   bad_access = 0;
   challenge3(A, B, C, N, M, L);
   save_counters(&fors, &whiles);   
   
   print_tab(L, stu_C);
   
   printf("%d %d\n", fors, whiles);
   printf("%d\n", bad_access);   
   
   // 4. Additionnal tests
   // Diff A, Diff B, Diff C
   printf("%d %d %d\n", memcmp(cpy_A, actual_tab(A), sizeof(int) * actual_tab_l(A)),
                        memcmp(cpy_B, actual_tab(B), sizeof(int) * actual_tab_l(B)),
                        memcmp(correct, actual_tab(C), sizeof(int) * actual_tab_l(C)));
                        
   release(A);
   release(B);
   release(C);
}

int main(int __attribute__((unused)) argc, char *argv[])
{
	srand(time(NULL));
   
	const int BASE = 10;
   
	long test_nbr = strtol(argv[1], NULL, BASE);
   
	
	unsigned int N;
   unsigned int M;
   int inter_empty;
   int max_iter = 0;
   
	switch(test_nbr){
		case 0:
			N = 0;
         M = 0;
         inter_empty = 0;
			break;
		case 1:
			N = rand_range(20, 30);
         M = rand_range(20, 30);
         inter_empty = 0;
			break;
		default:
		case 2:
			N = rand_range(20, 30);
         M = rand_range(20, 30);
         inter_empty = 1;
			break;
      case 3:
         N = rand_range(20, 30);
         M = rand_range(20, 30);
         inter_empty = 0;
         max_iter = 1;
			break;
	}

	test(N, M, inter_empty, max_iter);
   
	return EXIT_SUCCESS;
}
