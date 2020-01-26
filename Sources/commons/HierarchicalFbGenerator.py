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


from collections import Counter
from itertools import chain as ch

import remarks_and_printing as rp
import random


DEBUG=False


class HierarchicalFbGenerator(object):
    '''
    classdocs
    '''
    
    
    __default_printing_rules__ = {rp.R_TYPE.TITLE    : rp.print_title,
                                  rp.R_TYPE.FEEDFWD_W: rp.print_warning,
                                  rp.R_TYPE.FEEDFWD_Q: rp.print_ff,
                                  rp.R_TYPE.FEEDFWD_T: rp.print_ff,
                                  #rp.R_TYPE.EXAMPLE  : lambda r: ("".join(("EXEMPLE : ", r.text))),
                                  #rp.R_TYPE.DISPLAY  : None, Not needed
                                  #rp.R_TYPE.REMARK   : None, Not needed too
                                  }
    
    @staticmethod    
    def __default_printing__(remark):
        """
        Printing can send tuple of str.
        """
        return (remark.text,)

    def __init__(self, printing_rules=__default_printing_rules__, params=None):
        '''
        Constructor
        '''
        self.printing_rules = printing_rules #if printing_rules else HierarchicalFbGenerator.__default_printing_rules__
        self.END_OF_FB = "\nDo not hesitate to sumbit again. Sincerely."
        self.FINAL_TITLE = "Overall recommendations"
        self.FAIL = (rp.disp_msg("Something went wrong during the correction.\n", 0),)
            
    def generate(self, coms_list, titles=None):
        """
        """        
        # Creating the list  
        remark_list = list(ch.from_iterable(coms_list))
        
        if DEBUG:
            print remark_list
        
        # Remove useless Remarks and creating new ones
        filtred_remark_gen = self.filtrate(remark_list)
        
        # Remarks printing
        feedback = self.print_remark_list(filtred_remark_gen)
        
        return feedback
            
    def filtrate(self, remarks_list, **args):
        """
        
        Keywords Args:
            max_feedfwd  (int): Maximum number of feedforward pieces of advices printed
            max_example  (int): Maximum number of examples illustrating an error
            remark_min   (int): Below this limit, all the Remark will be printed, regardless of their priority
            remark_thres (int): Threshold under which Remark with smaller priority are silented.
                All the Remark with higher priority are still printed
            warning_thresh (int): A Remark (or a sum of several Remarks) above this threshold will be placed
                in first position in the feedback
        """
        
        if DEBUG:
            print args
        
        MAX_FEEDFWD    = 5
        MAX_EXAMPLE    = 3
        REMARK_MIN     = 10
        REMARK_THRESH  = 150
        WARNING_THRESH = 300
        
        max_feedfwd    = args.get('max_feedfwd', MAX_FEEDFWD)
        max_example    = args.get('max_example', MAX_EXAMPLE)
        remark_min     = args.get('remark_min', REMARK_MIN)
        remark_thres   = args.get('remark_thres', REMARK_THRESH)
        warning_thresh = args.get('warning_thresh', WARNING_THRESH)
        
        #print {r.code : r.priority for r in remark_list}
        """
        for k,v in {r.code : r.priority for r in remark_list}:
            c.update({k:v})for r in remark_list:
            c.update({r.code :  r.priority})
            
            #d = defaultdict(int)
        
        """
        
        """
        Here, the Remarks will be stored in a flat list in [TD*[REF]*]* order.
        we could use a generator (with yield to not copy all the remarks.
        """
        
        
        
        c = Counter()
        
        example_cnt = []
        
        for r in remarks_list:
            
            if DEBUG:
                print r
            
            if r.code and r.priority:
                c[r.code] += r.priority
            
            if r.type == rp.R_TYPE.TITLE:
                example_cnt.append(0)
                
            if example_cnt and r.type == rp.R_TYPE.EXAMPLE:
                example_cnt[-1] += 1
                
        
        # 1) Selection of most important feedforward pieces of informations
        # -> Up to MAX_FEEDFWD
        ff_to_be_disp = dict(c.most_common(max_feedfwd))
        
        warning = c.most_common(1)
        
        # On the basis of the previous computation, decide if the feedforward should be put at
        # the end or in the beginning of the feedback
        if warning and warning[0][1] >= warning_thresh:
            # Normallement beaucoup plus complexe...
            yield rp.warning(warning[0][0], None)
            # delete the yielded ff:
            del ff_to_be_disp[warning[0][0]]
        
        # yield all the Remarks now
        # Normally, each question should not produce more than 1 example of feedforward code
        # Hence, if the ff code belongs to ff_to_be_disp but with an highest priority, it should be
        # trailed-displayed. If not, it should be placed 
        # Do not display the warning too.
        trail_ff = []
        question_ff = []
        
        #New_quest = False
        
        quest_nb = 0
        
        # 
        for r in remarks_list:
            if r.type == rp.R_TYPE.TITLE:
                for qff in question_ff:
                    yield rp.feedfwd_question(qff, None, 0)
                
                # Back to empty list
                question_ff = []
                
                # Compute the example now
                example_gen = self.select_exemple(example_cnt[quest_nb], max_example)
                quest_nb += 1
            
            if r.type != rp.R_TYPE.EXAMPLE or example_gen.next():
                yield r
            
            if r.code in ff_to_be_disp:
                if r.priority == ff_to_be_disp[r.code]:
                    question_ff.append(r.code)
                else:
                    trail_ff.append(r.code)
                    del ff_to_be_disp[r.code]
                    
        for qff in question_ff:
            yield rp.feedfwd_question(qff, None, 0)         
        
        # yield the eventual trail_ff
        #if trail_ff:
        yield rp.title(self.FINAL_TITLE, None)
        
        for t in trail_ff:
            yield rp.feedfwd_trail(t)
        
        yield rp.disp_msg(self.END_OF_FB,None)
        
    def print_remark_list(self, remarks_list):
        
        #Appeler print_remark
        if DEBUG:
            remarks_list = [r for r in remarks_list]
        
            for r in remarks_list:
                print "DEBUG: ", r
        
        return "".join(ch.from_iterable((self.print_remark(r) for r in remarks_list)))   
        
    def print_remark(self, remark):
        """
        print return iterables of string.
        """
        
        return self.printing_rules.get(remark.type, HierarchicalFbGenerator.__default_printing__)(remark)
        
    def select_exemple(self, nb_examples, nb_to_print):
        """ 
        """
        if nb_examples <= nb_to_print:
            return (True for i in xrange(nb_to_print))
        
        to_print = [True]*nb_to_print + [False]*(nb_examples - nb_to_print)
        
        random.shuffle(to_print)
        
        return (pr for pr in to_print)
        

