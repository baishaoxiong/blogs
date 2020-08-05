# 小学春游 - 两组同学，每组1-3人，每组有一个队长;春游期间，由于景点人数较多，秩序混乱，班主任要求在指定地点，按组集合

# 源数据
s = [{'name': 'leader-1', 'belong_to': None},
     {'name': 'jack', 'belong_to': 'leader-2'},
     {'name': 'lili', 'belong_to': 'leader-1'},
     {'name': 'leader-2', 'belong_to': None},
     {'name': 'Tom', 'belong_to': 'leader-1'}]
# 目标数据
d = [
    # {'name':'leader-1', 'team':[{'name':'lili'},{'name':'Tom'}]},
    # {'name':'leader-2', 'team':[{'name':'jack'}]}
]


# def find_time(data):
#
#
#     m_dict = {}
#     leader_data = []
#     for d in data:
#         if d['belong_to']:
#             m_dict.setdefault(d['belong_to'], [])
#             m_dict[d['belong_to']].append({'name': d['name']})
#             print(m_dict)
#         else:
#             leader_data.append({'name':d['name'],'team':[]})
#
#
#     print(m_dict)
#     print(leader_data)
#     for l in  leader_data:
#         if l['name'] in m_dict:
#             l['team']=m_dict[l['name']]
#
#     return  leader_data
#
# find_time(s)

def fand_time(data):
    s={}
    team=[]
    for i in data:
        if i['belong_to']:
            s.setdefault(i['belong_to'],[])

            s[i['belong_to']].append({'name':i['name']})

        else:
            team.append({'name':i['name'],'team':[]})

    for i in team:
        if i['name']in s:
            i['team']=s[i['name']]
    return team

print(fand_time(s))





