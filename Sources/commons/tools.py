# coding: utf-8
'''
Created on 18 sept. 2017

@author: slienardy
'''

def fake_dict(tup, index, default="???"):
    """Fake dict.get utilisation with tuple
    As if tuple (a,b,c,d,e) was the dict :
    {"1":a, "2":b, "3":c, "4":d, "5":e}
    
    More efficient and do not need to compute hash function...
    """
    try:
        return tup[int(index) - 1]
    except:
        return default
    
