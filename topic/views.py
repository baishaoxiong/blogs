import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from message.models import Message
from tools.logging_dec import logging_check,get_user_by_request
from django.utils.decorators import method_decorator
from  user.models import UserProfile
from tools.cache_dec import topic_cache


from .models import  Topic

class TopicViews(View):

    def make_topics_res(self,author,author_topics):

        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            # 2018-09-03 10:30:20
            d['introduce'] = topic.introduce
            d['created_time'] = topic.created.strftime('%Y-%m-%d %H:%M:%S')
            d['author'] = author.nickname
            topics_res.append(d)

        res = {'code': 200, 'data': {}}
        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res

    def make_topic_res(self,author,author_topics,is_self):
        if is_self:
            nixt_topic= Topic.objects.filter(id__gt=author_topics.id,user_profile=author.username).first()
            last_topic= Topic.objects.filter(id__lt=author_topics.id,user_profile=author.username).last()
        else:
            nixt_topic = Topic.objects.filter(id__gt=author_topics.id, user_profile=author.username,limit='piblic').first()
            last_topic = Topic.objects.filter(id__lt=author_topics.id, user_profile=author.username,limit='piblic').last()
        if  nixt_topic:
            next_id=nixt_topic.id
            next_title=nixt_topic.title
        else:
            next_id = None
            next_title = None
        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None
        all_messages = Message.objects.filter(topic=author_topics).order_by('-created_time')
        msg_list = []
        r_dict = {}
        msg_count = 0
        for msg in all_messages:
            if msg.parent_message:
                # 回复
                r_dict.setdefault(msg.parent_message, [])
                r_dict[msg.parent_message].append(
                    {'msg_id': msg.id, 'content': msg.content, 'publisher': msg.user_profile.nickname,
                     'publisher_avatar': str(msg.user_profile.avatar),
                     'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                # 留言/评论
                msg_count += 1
                msg_list.append({'id': msg.id, 'content': msg.content, 'publisher': msg.user_profile.nickname,
                                 'publisher_avatar': str(msg.user_profile.avatar),
                                 'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S'), 'reply': []})

        # 将 留言和回复进行关联
        for m in msg_list:
            if m['id'] in r_dict:
                m['reply'] = r_dict[m['id']]

        d={}
        d['nickname']=author.nickname
        d['title']=author_topics.title
        d['category']=author_topics.category
        d['created_time']=author_topics.created.strftime('%Y-%m-%d %H:%M:%S')
        d['content']=author_topics.content
        d['introduce']=author_topics. introduce
        d['author']=author.nickname
        d['next_id']=next_id
        # author_2=Topic.objects.get(id=tid+1)
        d['next_title']=next_title
        d['last_id']=last_id
        d['last_title']=last_title
        d['messages']=[]
        d['messages_count']=2
        res={'code':200,'data':{}}
        res['data']=d
        return res


    def clear_topic_cache(self,request):

        all_path = request.get_full_path()
        all_key_p = ['topic_cache_self_', 'topic_cache_']
        all_keys = []
        for key_p in all_key_p:
            for key_h in ['', '?category=tec', '?category=no-tec']:
                all_keys.append(key_p + all_path + key_h)

        print(all_keys)
        # 删除
        # for del_key in all_keys:
        #     cache.delete(del_key)
        cache.delete_many(all_keys)


    @method_decorator(logging_check)
    def post(self,request,author_id):
        #发表文章
        author=request.myuser
        #获取jsion串儿内容
        json_str = request.body
        json_obj = json.loads(json_str)
        content = json_obj['content']
        content_text = json_obj['content_text']
        introduce = content_text[:20]
        limit = json_obj['limit']
        if limit not in ['public','private']:
            result={'code':10300,'error':'The limit is error'}
            return JsonResponse(result)
        import html


        title = json_obj['title']
        title = html.escape(title)
        category = json_obj['category']


        if category not in ['tec', 'no-tec']:
            result = {'code': 10301, 'error': 'The categroy is error'}
            return JsonResponse(result)


        #根据content——text 20 个子为文章简介
        Topic.objects.create(title=title,content=content,limit=limit,category=category,introduce=introduce,user_profile=author)
        self.clear_topic_cache(request)

        result={'code':200}
        return JsonResponse(result)

    @method_decorator(topic_cache(200))
    def get(self,request,author_id):
        print('----------------------------in')

        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e :
            result={'code':10305,'error':'The author id is error'}
            return  JsonResponse(result)
        visitor_username = get_user_by_request(request)
        t_id=request.GET.get('t_id')
        is_self=False
        if t_id:
            if visitor_username == author_id:
                is_self=True
                try:
                    author_topics = Topic.objects.get(id=t_id,user_profile_id=author_id)
                except Exception as e:
                    result={'code':5555,'error':'wrong'}
                    return JsonResponse(result)

            else:
                try:
                    author_topics = Topic.objects.get(id=t_id, user_profile_id=author_id,limit='public')
                except Exception as e:
                    result = {'code': 5555, 'error': 'wrong'}
                    return JsonResponse(result)
            res=self.make_topic_res(author,author_topics,is_self)
            return JsonResponse(res)


        else:
            category = request.GET.get('category')
            filter_category = False
            if category in ['tec', 'no-tec']:
                filter_category = True

            if visitor_username == author_id:
                # 博主访问自己的博客
                if filter_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id, category=category)
                else:
                    # 非博主访问博主的博客
                    author_topics = Topic.objects.filter(user_profile_id=author_id, limit='public', category=category)

            else:
                # 博主访问自己的博客
                if filter_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id)
                else:
                    # 非博主访问博主的博客
                    author_topics = Topic.objects.filter(user_profile_id=author_id, limit='public')

            res = self.make_topics_res(author, author_topics)
            return JsonResponse(res)













