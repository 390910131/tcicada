# -*- coding:utf-8 -*-
import time
from django.db import models, connection
from django.contrib import admin
from django.utils import timesince, html
from cicada.utils import function, formatter
from cicada.settings import *

# Create your models here.
class Category(models.Model):
    name = models.CharField('分类名称', max_length=20)
    
    def __unicode__(self):
        return self.name
    
    def save(self):
        self.name = self.name[0:20]
        return super(Category, self).save()
    
    class Meta:
        verbose_name = '分类名称'
        verbose_name_plural = '分类名称'
        
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    list_per_page = ADMIN_PAGE_SIZE

# Area Model
class Area(models.Model):
    TYPE_CHOICES = ((0, '国家'), (1, '省'), (2, '市'), (3, '区县'))
    
    name = models.CharField('地名', max_length=100)
    code = models.CharField('代码', max_length=255)
    type = models.IntegerField('类型', choices = TYPE_CHOICES)
    parent = models.IntegerField('父级编号（关联自己）')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u'所在地'
        verbose_name_plural = u'所在地'
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id','name','code')
    list_display_links = ('id','name','code')
    list_per_page = ADMIN_PAGE_SIZE
    
# User Model
class User(models.Model):
    username = models.CharField('用户名', max_length=20) 
    password = models.CharField('密码', max_length=100)
    realname = models.CharField('姓名', max_length=20)
    email = models.EmailField('Email')
    area = models.ForeignKey(Area, verbose_name='地区')
    face = models.ImageField('头像', upload_to='face/%Y/%m/%d',default='',blank=True)
    url = models.CharField('个人主页', max_length=200, default='',blank=True)
    about = models.TextField('关于我', max_length=1000, default='', blank=True)
    addtime = models.DateTimeField('注册时间', auto_now=True)
    friend = models.ManyToManyField('self', verbose_name='朋友')
    
    def __unicode__(self):
        return self.realname
    
    def addtime_format(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')
    
    def save(self, modify_pwd=True):
        if modify_pwd:
            self.password = function.md5_encode(self.password)
        self.about = formatter.substr(self.about, 20, True)
        super(User, self).save()
    
    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户'

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'realname', 'email', 'addtime_format')
    list_display_links = ('username', 'realname', 'email')
    list_per_page = ADMIN_PAGE_SIZE

# Note Model
class Note(models.Model):
    message = models.TextField('消息')
    addtime = models.DateTimeField('发布时间', auto_now=True)
    category = models.ForeignKey(Category, verbose_name='来源')
    user = models.ForeignKey(User, verbose_name='发布者')
    
    def __unicode__(self):
        return self.message
    
    def message_short(self):
        return formatter.substr(self.message, 30)
    
    def addtime_format_admin(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')
    
    def category_name(self):
        return self.category.name
    
    def user_name(self):
        return self.user.realname
    
    def save(self):
        self.message = formatter.content_tiny_url(self.message)
        self.message = html.escape(self.message)
        self.message = formatter.substr(self.message, 140)
        super(Note, self).save()
    
    def get_absolute_url(self):
        return APP_DOMAIN + 'message/%s/' % self.id
    
    class Meta:
        verbose_name = u'消息'
        verbose_name_plural = u'消息'

class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'message_short', 'addtime_format_admin', 'category_name')
    list_display_links = ('id', 'message_short')
    search_fields = ['message']
    list_per_page = ADMIN_PAGE_SIZE

admin.site.register(Note,NoteAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(Area,AreaAdmin)