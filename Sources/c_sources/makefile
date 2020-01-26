# Copyright - Simon Liénardy <simon.lienardy@uliege.be> 2020
#
# This file is part of CAFÉ.
#  
# CAFÉ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# CAFÉ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CAFÉ.  If not, see <http://www.gnu.org/licenses/>.
CC = gcc
LD = gcc
CFLAGS=--std=c99
CHECKFLAGS=--std=c99 --pedantic -Wall -W -Wmissing-prototypes -DCHECK
LDFLAGS=
EXEC=main

ALL_SRCS=$(wildcard *.c)
SRCS=$(filter-out main.c, $(ALL_SRCS)) # 
OBJS = $(patsubst %.c,%.o,$(SRCS))
HEAD = $(patsubst %.c,%.h,$(SRCS))

#
.PHONY: clean, all, check

all:$(EXEC)

main: $(OBJS)
	$(LD) -o main $^ $(LDFLAGS)

%.o: %.c %.h
	$(CC) $(CFLAGS)  -c  $<

check: $(ALL_SRCS)
	$(CC) $(CHECKFLAGS)  -c  $^
	@./loopcounter.sh test.c
	@./script.sh test.c

clean:
	rm *.o
