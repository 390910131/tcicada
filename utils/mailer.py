# -*- coding:utf-8 -*-
from django.core.mail import send_mail
# 发件人email
FROM_EMAIL = ''

MAIL_FOOT = u'''<br/><br/><br/>
CiCaDa开发小组.<br/>
<a href="http://www.google.com">cicada.com</a>
'''

def send_register_success_mail(userinfo):
    subject = u'注册成功'
    body = u'''您好！<b>%s</b><br/>
    您已经成功注册为Cicada用户<br>
    以下是您的注册信息:<br/>
    <ul>
        <li>用户名: %s </li>
        <li>密  码: %s </li>
    <ul>''' %(userinfo['realname'],userinfo['username'],userinfo['password'])
    recipient_list = [userinfo['email']]
    send(subject, body, recipient_list)

def send(subject, body, recipient_list):
    body += MAIL_FOOT
    send_mail(subject, body, FROM_EMAIL, recipient_list, fail_silently=True)


def test(request):
    send_register_success_mail(
        {
            'username' : 'kimly x',
            'password' : '*******',
            'email': 'kimlyx@qqcom',
            'realname' : 'kimly x',
        }
    )