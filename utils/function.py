# -*- coding:utf-8 -*-
import hashlib

def md5_encode(str):
    u"""
    summary:
        返回md5加密后的字符串
        
    """
    return hashlib.md5(str).hexdigest()

def get_referer_url(request):
    u"""
    summary:
        获取url来源,默认为 '/'
    author:
        kimly x <kimlyfly@gmail.com>
    """
    return request.META.get('HTTP_REFERER', '/')