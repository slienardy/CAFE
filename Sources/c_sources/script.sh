#!/bin/bash
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

sed -i 's/\[/\(/g' $1
sed -i 's/\]/\)/g' $1
