/**
 * CAFÉ - C implementation
 *
 * @author Simon Liénardy <simon.lienardy@uliege.be>
 * @version 1.0 
 *
 *  @section LICENSE
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
 * This file contains the implementation of the functions declared in the header vector.h
 */

#include"vector.h"
#include <stdlib.h>
#define SECURITY 4
  
int bad_access = 0;

struct tab{
   int *array;
   int length;
   int *raw;
   int true_length;
};

int get_offset(){return SECURITY;}

int *new_tab(int N)
{
   struct tab *T = malloc(sizeof(struct tab));
   
   T->raw = (int *) calloc(N + 2 * SECURITY, sizeof(int));
   T->array = T->raw + SECURITY;
   T->length = N;
   T->true_length = N + 2 * SECURITY;
   
   return (int*) T;
}

int *get(int *a, int i)
{
   struct tab *obj = (struct tab *) a;   
   
   if(i < 0 || i >= obj->length)
      ++bad_access;
      
   return obj->array + i;
}

int *student_tab(int *a){
   struct tab *obj = (struct tab *) a;    
   
   return obj->array;
}

int student_tab_l(int *a){
   struct tab *obj = (struct tab *) a;    
   
   return obj->length;
}

int *actual_tab(int *a){
   struct tab *obj = (struct tab *) a;    
   
   return obj->raw;
}

int actual_tab_l(int *a){
   struct tab *obj = (struct tab *) a;    
   
   return obj->true_length;
}

void release(int *a){
   struct tab *obj = (struct tab *) a;
   
   free(obj->raw);
   free(obj);
}

int* dup(int *a){
   struct tab *obj = (struct tab *) a;    
   
   
   
   return obj->array;
}


