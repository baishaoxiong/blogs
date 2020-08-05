import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from tools.logging_dec import logging_check, get_user_by_request
from .models import Topic
from user.models import UserProfile

#异常码 10300 - 10399


# Create your views here.
class TopicViews(View):


    def make_topics_res(self, author, author_topics):
        #博主主页 文章列表页的返回值

        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            #2018-09-03 10:30:20
            d['introduce'] = topic.introduce
            d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['author'] = author.nickname
            topics_res.append(d)

        res = {'code': 200, 'data': {}}
        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res



    @method_decorator(logging_check)
    def post(self, request, author_id):
        #发表文章
        author = request.myuser
        json_str = request.body
        json_obj = json.loads(json_str)
        #获取json串内容
        #{"content":"<p>aaaasdasdasd<br></p>","content_text":"aaaasdasdasd","limit":"public","title":"aaaaaaa","category":"tec"}
        #带有html的 文章内容
        content = json_obj['content']
        #纯文本的文章内容 - 用来截取文章简介
        content_text = json_obj['content_text']
        #根据 content_text 前20个字为文章简介
        introduce = content_text[:20]
        title = json_obj['title']


        limit = json_obj['limit']
        if limit not in ['public', 'private']:
            result = {'code':10300, 'error':'The limit is error'}
            return JsonResponse(result)

        category = json_obj['category']
        if category not in ['tec', 'no-tec']:
            result = {'code':10301, 'error':'The category is error'}
            return JsonResponse(result)

        #数据入库
        Topic.objects.create(title=title, content=content,limit=limit, category=category,introduce=introduce,user_profile=author)

        return JsonResponse({'code':200, 'username':author.username})



    def get(self, request, author_id,category):
        #/v1/topics/guoxiaonao
        #获取用户guoxiaonao的文章列表
        #1,访问者 visitor
        #2, 博主  author

        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e:
            result = {'code':10305, 'error':'The author id is error'}
            return JsonResponse(result)
        #尝试获取访问者的身份
        visitor_username = get_user_by_request(request)

        category = request.GET.get['category']
        filter_category=False
        if category in ['tec','no-tec']:
            filter_category=True


            if visitor_username == author_id:
                #博主访问自己的博客
                author_topics = Topic.objects.filter(user_profile_id=author_id,category=category)
            else:
                #非博主访问博主的博客
                author_topics = Topic.objects.filter(user_profile_id=author_id, limit='public',category=category)
        else:
            if visitor_username == author_id:
                # 博主访问自己的博客
                author_topics = Topic.objects.filter(user_profile_id=author_id)
            else:
                # 非博主访问博主的博客
                author_topics = Topic.objects.filter(user_profile_id=author_id, limit='public')

        res = self.make_topics_res(author, author_topics)
        return JsonResponse(res)













