# pycparser -- A C parser in Python
#
# Copyright (c) 2008-2017, Eli Bendersky
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this 
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation 
#  and/or other materials provided with the distribution.
# * Neither the name of Eli Bendersky nor the names of its contributors may 
#   be used to endorse or promote products derived from this software without 
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#------------------------------------------------------------------------------
# pycparser: ast_transforms.py
#
# Some utilities used by the parser to create a friendlier AST.
#
# Copyright (C) 2008-2015, Eli Bendersky
# License: BSD
#------------------------------------------------------------------------------

from . import c_ast


def fix_switch_cases(switch_node):
    """ The 'case' statements in a 'switch' come out of parsing with one
        child node, so subsequent statements are just tucked to the parent
        Compound. Additionally, consecutive (fall-through) case statements
        come out messy. This is a peculiarity of the C grammar. The following:

            switch (myvar) {
                case 10:
                    k = 10;
                    p = k + 1;
                    return 10;
                case 20:
                case 30:
                    return 20;
                default:
                    break;
            }

        Creates this tree (pseudo-dump):

            Switch
                ID: myvar
                Compound:
                    Case 10:
                        k = 10
                    p = k + 1
                    return 10
                    Case 20:
                        Case 30:
                            return 20
                    Default:
                        break

        The goal of this transform it to fix this mess, turning it into the
        following:

            Switch
                ID: myvar
                Compound:
                    Case 10:
                        k = 10
                        p = k + 1
                        return 10
                    Case 20:
                    Case 30:
                        return 20
                    Default:
                        break

        A fixed AST node is returned. The argument may be modified.
    """
    assert isinstance(switch_node, c_ast.Switch)
    if not isinstance(switch_node.stmt, c_ast.Compound):
        return switch_node

    # The new Compound child for the Switch, which will collect children in the
    # correct order
    new_compound = c_ast.Compound([], switch_node.stmt.coord)

    # The last Case/Default node
    last_case = None

    # Goes over the children of the Compound below the Switch, adding them
    # either directly below new_compound or below the last Case as appropriate
    for child in switch_node.stmt.block_items:
        if isinstance(child, (c_ast.Case, c_ast.Default)):
            # If it's a Case/Default:
            # 1. Add it to the Compound and mark as "last case"
            # 2. If its immediate child is also a Case or Default, promote it
            #    to a sibling.
            new_compound.block_items.append(child)
            _extract_nested_case(child, new_compound.block_items)
            last_case = new_compound.block_items[-1]
        else:
            # Other statements are added as children to the last case, if it
            # exists.
            if last_case is None:
                new_compound.block_items.append(child)
            else:
                last_case.stmts.append(child)

    switch_node.stmt = new_compound
    return switch_node


def _extract_nested_case(case_node, stmts_list):
    """ Recursively extract consecutive Case statements that are made nested
        by the parser and add them to the stmts_list.
    """
    if isinstance(case_node.stmts[0], (c_ast.Case, c_ast.Default)):
        stmts_list.append(case_node.stmts.pop())
        _extract_nested_case(stmts_list[-1], stmts_list)

