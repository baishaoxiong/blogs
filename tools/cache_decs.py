from django.core.cache import cache
from .logging_dec import get_user_by_request

def topic_cache(expire):
    def _topic_cache(func):
        def wrapper(request, *args, **kwargs):
            #根据查询字符串区分当前业务
            #根据有没有 t_id 查询字符串 区分当前拿的是批量数据还是具体某个文章的数据
            print(';;;;')
            if 't_id' in request.GET.keys():
                #TODO 拿具体文章
                return func(request, *args, **kwargs)
            print('00000')
            #####以下为 批量获取
            #检查访问者身份
            visitor=get_user_by_request(request)
            author_username = kwargs['author_id']
            print('%s ====== %s'%(visitor,author_username))
            if visitor==author_username:
            # 博主访问自己
                cache_key=' topic_cache_self_%s'%request.get_full_path()
            else:
            # 非博主访问
                cache_key=' topic_cache_%s'%request.get_full_path()
            print('cache  key is %s'%cache_key)
            res=cache.get('cache_key')
            if res:
                print('---cache in')
                return res
            res=func(request,*args,**kwargs)
            cache.set(cache_key,res,expire)
            #根据访问者身份和博主的关系,生成特定的cache_key
            #尝试先获取缓存,如果有 return cache
            #如果没有 return func,存储缓存
            return res

        return wrapper
    return _topic_cache