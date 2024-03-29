# -*- coding:utf-8 -*-
# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError
from django.template import Context ,loader
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core import serializers
from cicada.settings import *
from cicada.mvc.models import Note, User, Category, Area
from cicada.mvc.feed import RSSRecentNotes, RSSUserRecentNotes
from cicada.utils import mailer, formatter, function, uploader

# action functions


def __do_login(request, _username, _password):
    """
    summary:
        Do login
    """
    _state = __check_login(_username, _password)
    if _state['success']:
        # save login info to session
        request.session['islogin'] = True
        request.session['userid'] = _state['userid']
        request.session['username'] = _username
        request.session['realname'] = _state['realname']        
    return _state

def __user_id(request):
    """
    summary:
        Get session user id
    """
    return request.session.get('userid', -1)

def __user_name(request):
    """
    summary:
        Get session realname
    """
    return request.session.get('username', '')

def __is_login(request):
    """
    summary:
        Return user login state
    """
    return request.session.get('islogin', False)

def __check_login(_username, _password):
    """
    summary:
        Check username and password
    """
    _state = {
        'success':True,
        'message':'none',
        'userid':-1,
        'realname':'',
    }
    try:
        _user = User.objects.get(username=_username)
        
        # To decide password
        if _user.password == function.md5_encode(_password):
            _state['success'] = True
            _state['userid'] = _user.id
            _state['realname'] = _user.realname
        else:
            # Password incorrect
            _state['success'] = False
            _state['message'] = u'密码不正确.'
    except User.DoesNotExist:
        # User not exist
        _state['success'] = False
        _state['message'] = u'用户不存在.'
    return _state

# Check username was existed
def __check_username_exist(_username):
    _exist = True
    
    try:
        _user = User.objects.get(username=_username)
        _exist = True
    except:
        _exist = False
    return _exist

# Post signup data
def __do_signup(request, _userinfo):
    
    _state = {
        'success':False,
        'message':'',
    }
    # check username exist
    if _userinfo['username'] == '':
        _state['success'] = False
        _state['message'] = u'用户名未输入.'
        return _state
    
    if _userinfo['password'] == '':
        _state['success'] = False
        _state['message'] = u'密码未输入.'
        return _state
    
    if _userinfo['realname'] == '':
        _state['success'] = False
        _state['message'] = u'姓名未输入.'
        return _state
    
    if _userinfo['email'] == '':
        _state['success'] = False
        _state['message'] = u'Email未输入.'
        return _state
    
    # Check username exist
    if __check_username_exist(_userinfo['username']):
        _state['success'] = False
        _state['message'] = u'用户名已经存在.'
        return _state
    
    # Check password & confirm password
    if _userinfo['password'] != _userinfo['confirm']:
        _state['success'] = False
        _state['message'] = u'两次输入的密码不一致.'
        return _state
    
    _user = User(
        username = _userinfo['username'],
        realname = _userinfo['realname'],
        password = _userinfo['password'],
        email = _userinfo['email'],
        area = Area.objects.get(id=1)
    )
    #try:
    _user.save()
    _state['success'] = True
    _state['message'] = u'注册成功!'
    #except:
        #_state['success'] = False
        #_state['message'] = u'程序异常，注册失败.'
    # send regist success mail
    mailer.send_register_success_mail(_userinfo)
    
    return _state

# Response result message page
def __result_message(request, _title=u'消息', _message='程序有异常，操作未成功',_go_back_url=''):
    
    _islogin = __is_login(request)
    
    if _go_back_url == '':
        _go_back_url = function.get_referer_url(request)
    
    # body content
    _template = loader.get_template('result_message.html')
    _context = Context({
        'page_title':_title,
        'message':_message,
        'go_back_url':_go_back_url,
        'islogin':_islogin
    })
    _output = _template.render(_context)
    return HttpResponse(_output)

# ##################
# views method
# ##################

# home view
def index(request):
    return index_user(request, '')

# user messages vies by self
def index_user_self(request):
    _user_name = __user_name(request)
    return index_user(request, _user_name)

# user messages view
def index_user(request, _username):
    return index_user_page(request, _username, 1)

# index page
def index_page(request, _page_index):
    return index_user_page(request, '', _page_index)

# user message view and page
def index_user_page(request, _username, _page_index):
    
    # Get user login state
    _islogin = __is_login(request)
    _page_title = u'首页'
    
    try:
         # Get post params
        _message = request.POST['message']
        _is_post = True
    except KeyError:
        _is_post = False
    
    # save message
    if _is_post:
        # check login
        if not _islogin:
            return HttpResponseRedirect('/signin/')
        # save message
        _category = Category.objects.get_or_create(name=u'网页')
        try:
            _user = User.objects.get(id=__user_id(request))
        except:
            return HttpResponseRedirect('/signin/')
        
        _note = Note(message=_message, category=_category, user=_user)
        _note.save(self, *args, **kwargs)
        return HttpResponseRedirect('/user/' + _user.username)
    
    _userid = -1
    # Get message list
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE
    _last_item_index = PAGE_SIZE * int(_page_index)
    _login_user_friend_list = None
    if _islogin:
        # Get friend message if user is logined
        _login_user = User.objects.get(username=__user_name(request))
        _login_user_friend_list = _login_user.friend.all()
    else:
        _login_user = None
    
    _friends = None
    _self_home = False
    if _username != '':
        # there is get user's message
        _user = get_object_or_404(User, username=_username)
        _userid = _user.id
        _notes = Note.objects.filter(user=_user).order_by('-addtime')
        _page_title = u'%s' % _user.realname
        # Get friend lists
        _friends = _user.friend.get_query_set().order_by('id')[0:FRIEND_LIST_MAX]
        if _userid == __user_id(request):
            _self_home = True
            
    else:
        # Get all message
        _user = None
        
        if _islogin:
            _query_users = [_login_user]
            _query_users.extend(_login_user.friend.all())
            _notes = Note.objects.filter(user__in=_query_users).order_by('-addtime')
        else:
            # Get all user message
            _notes = Note.objects.order_by('-addtime')
        
    # Page bar
    _page_bar = formatter.pagebar(_notes, _page_index, _username)
    # Get current page
    _notes = _notes[_offset_index:_last_item_index]
    #Body content
    _template = loader.get_template('index.html')
        
    _context = Context({
        'page_title':_page_title,
        'notes':_notes,
        'islogin':_islogin,
        'userid':__user_id(request),
        'self_home':_self_home,
        'user':_user,
        'page_bar':_page_bar,
        'friends':_friends,
        'login_user_friend_list':_login_user_friend_list,
    })
    _output = _template.render(_context)
    return HttpResponse(_output)
    
# detail view
def detail(request, _id):
    # Get user login status
    _islogin = __is_login(request)
    _note = get_object_or_404(Note, id=_id)
    # body content
    _template = loader.get_template('detail.html')
    _context = Context({
        'page_title':u'%s的消息 %s' %(_note.user.realname, _id),
        'item':_note,
        'islogin':_islogin,
        'userid':__user_id(request),
    })
    _output = _template.render(_context)
    return HttpResponse(_output)

def detail_delete(request, _id):
    # Get user login status
    _islogin = __is_login(request)
    _note = get_object_or_404(Note, id=_id)
    _message = ''
    try:
        _note.delete()
        _message = u'消息已经删除.'
    except:
        _message = u'删除出错.'
    return __result_message(request, u'消息 %s' % _id, _message)

# signin view
def signin(request):
    # Get user login status
    _islogin = __is_login(request)
    try:
        # Get post params
        _username = request.POST['username']
        _password = request.POST['password']
        _is_post = True
    except KeyError:
        _is_post = False
    # Check username and password
    if _is_post:
        _state = __do_login(request, _username, _password)
        
        if _state['success']:
            return __result_message(request, u'登录成功', u'恭喜，您已经登录成功')
    else:
        _state = {
            'success':False,
            'message':u'请登录'
            }
    # Body content
    _template = loader.get_template('signin.html')
    _context = Context({
        'page_title':u'登录',
        'state':_state,            
    })
    _output = _template.render(_context)
    return HttpResponse(_output)

def signup(request):
    # Check is login
    _islogin = __is_login(request)
    if _islogin:
        return HttpResponseRedirect('/')
    _userinfo = {
        'username':'',
        'password':'',
        'confirm':'',
        'realname':'',
        'email':'',
    }        
    try:
        # Get post params
        _userinfo = {
            'username':request.POST['username'],
            'password':request.POST['password'],
            'confirm':request.POST['confirm'],
            'realname':request.POST['realname'],
            'email':request.POST['email'],
        }
        _is_post = True
    except KeyError:
        _is_post = False
    if _is_post:
        _state = __do_signup(request, _userinfo)
    else:
        _state = {
            'success':False,
            'message':u'注册新用户'
        }
    if _state['success']:
        return __result_message(request,u'注册成功',u'恭喜，您已经注册成功。') 
    
    _result = {
        'success':_state['success'],
        'message':_state['message'],
        'form':{
            'username':_userinfo['username'],
            'realname':_userinfo['realname'],
            'email':_userinfo['email'],
        }
    }
    
    # Body content
    _template = loader.get_template('signup.html')
    _context = Context({
        'page_title':u'注册',
        'state':_result
    })
    _output = _template.render(_context)
    return HttpResponse(_output)

# signout view
def signout(request):
    request.session['islogin'] = False
    request.session['userid'] = -1
    request.session['username'] = ''
    return HttpResponseRedirect('/')

def settings(request):
    # Check is login
    _islogin = __is_login(request)
    if not _islogin:
        return HttpResponseRedirect('/signin/')
    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
    except:
        return HttpResponseRedirect('/signin/')
    
    if request.method == 'POST':
        # Get post params
        _userinfo = {
            'realname':request.POST['realname'],
            'url':request.POST['url'],
            'email':request.POST['email'],
            'face':request.FILES.get('face', None),
            'about':request.POST['about'],
        }
        _is_post = True
    else:
        _is_post = False
    
    _state = {
        'message':''
    }
    # save user info 
    if _is_post:
        _user.realname = _userinfo['realname']
        _user.url = _userinfo['url']
        _user.email = _userinfo['email']
        _user.anout = _userinfo['about']
        _file_obj = _userinfo['face']
        #try:
        if _file_obj:
            _upload_state = uploader.upload_face(_file_obj)
            if _upload_state['success']:
                _user.face = _upload_state['message']
            else:
                return __result_message(request, u'错误', u'提交数据时异常，保存失败')
        _user.save(False)
        _state['message'] = u'保存成功.'
        #except:
            #return __result_message(request, u'错误', u'提交数据时出现异常,保存失败.')
    # Body content
    _template = loader.get_template('settings.html')
    _context = Context({
        'page_title':u'个人设置',
        'state':_state,
        'islogin':_islogin,
        'user':_user,
    })
    _output = _template.render(_context)
    return HttpResponse(_output)

# All users list
def user_index(request):
    return users_list(request, 1)

# All users list
def users_list(request, _page_index=1):
    # Check is login
    _islogin = __is_login(request)
    _page_title = u'网友们'
    _users = User.objects.order_by('-addtime')
    
    _login_user = None
    _login_user_friend_list = None
    if _islogin:
        try:
            _login_user = User.objects.get(id=__user_id(request))
            _login_user_friend_list = _login_user.friend.all()
        except:
            _login_user = None
    # Page Bar
    _page_bar = formatter.pagebar(_users, _page_index, '', 'control/userslist_pagebar.html')
    # Get message list
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE
    _last_item_index = PAGE_SIZE * int(_page_index)
    # Get current page
    _users = _users[_offset_index:_last_item_index]
    # Body content
    _template = loader.get_template('users_list.html')
    
    _context = Context({
        'page_tile':_page_title,
        'users':_users,
        'login_user_friend_list':_login_user_friend_list,
        'islogin':_islogin,
        'userid':__user_id(request),
        'page_bar':_page_bar,
    })
    _output = _template.render(_context)
    return HttpResponse(_output)

# Add friend
def friend_add(request, _username):
    # Check is login
    _islogin = __is_login(request)
    if not _islogin:
        return HttpResponseRedirect('/signin/')
    _state = {
        'success':False,
        'message':'',
    }
    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
    except:
        return __result_message(request, u'对不起', u'你想添加的人不存在.')
    
    # Check friend exist
    try:
        _friend = User.objects.get(username=_username)
        _user.friend.add(_friend)
        return __result_message(request, u'成功', u'好友添加成功,%s 已成为你的朋友!' % _friend.realname)
    except:
        return __result_message(request, u'错误', u'你想添加的这个人不存在.')

# Remove friend
def friend_remove(request, _username):
    # Check is login
    _islogin = __is_login(request)
    if not _islogin:
        return HttpResponseRedirect('/signin/')
    _state = {
        'success':False,
        'message':'',
    }
    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
    except:
        return __result_message(request,u'对不起', u'你想添加这个人不存在。')
    
    # Check friend exist
    try:
        _friend = User.objects.get(username=_username)
        _user.friend.remove(_friend)
        return __result_message(request, u'成功', u'与,%s的好友关系已经删除.' % _friend.realname)
    except:
        return __result_message(request, u'错误', u'好友关系不存在.')
    
# Add note by to api
def api_note_add(request):
    """
    summary:
        Api interface post message
    params:
        GET['uname'] CiCaDa user's username
        GET['pwd'] user's password not encoding
        GET['msg'] want to post message
        GET['from'] your web site name
    author:
        kimly x
    """
    # Get querystring params
    _username = request.GET['uname']
    _password = functions.md5_encode(request.GET['pwd'])
    _message = request.GET['msg']
    _from = request.GET['from']
    
    # Get user info and check user
    try:
        _user = User.objects.get(username=_username, password=_password)
    except:
        return HttpResponse('-2')
    # Get category info ,If it not exist create new
    (_cate, _is_added_cate) = Category.objects.get_or_create(name=_from)
    
    try:
        _note = Note(message=_message, user=_user, category=_cate)
        _note.save()
        return HttpResponse('1')
    except:
        return HttpResponse('-1')    