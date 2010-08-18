# -*- coding;utf-8 -*-
# 上传文件
import sys, os
import time
from StringIO import StringIO
from PIL import Image
from cicada.settings import *
import ImageFilter

def upload_face(data):
    u'''
    summary:
        上传用户头像
    params:
        data  object request.FILES.get('uploadcontrolname')
    returns:
        _state directory {'success':True|False, 'message':error info| new files path}    
    author:
        Kimly x <kimlyfly@gmail.com>
    '''
    _state = {
        'success':False,
        'message':'',
    }
    if data.size > 0:
        #try:
        base_im = Image.open(data)
        
        size16 = (16,16)
        size24 = (24,24)
        size32 = (32,32)
        size100 = (75,75)
        
        size_array = (size100, size32, size24, size16)
        
        # 生成的文件名和文件路径
        file_name = time.strftime('%H%M%S') + '.png'
        file_root_path = '%sface/' %(MEDIA_ROOT)
        file_sub_path = '%s' % (str(time.strftime("%Y/%m/%d")))
        
        # 生成不同尺寸的图片
        for size in size_array:
            file_middle_path = '%d/' % size[0]
            
            file_path = os.path.abspath(file_root_path + file_middle_path + file_sub_path)
            
            im = base_im
            im = make_thumb(im, size[0])
            
            # 检查路径是否存在
            if not os.path.exists(file_path):
                os.makedirs(file_path)
                
            im.save('%s/%s' % (file_path, file_name))
        
        _state['success'] = True
        _state['message'] = file_sub_path + file_name
        #except:
        #    _state['success'] = False
        #    _state['message'] = '还没有选择要上传的文件'
        
        return _state
