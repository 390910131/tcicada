# -*- coding:utf-8 -*-
from django.template import Library
from cicada.mvc.models import *
from cicada.settings import *

register = Library()

def in_list(val, lst):
    u"""
    summary:
        检查值是否在列表中
    author:
        kimly x <kimlyfly@gmail.com>
    """
    return val in lst

register.filter('in_list', in_list)