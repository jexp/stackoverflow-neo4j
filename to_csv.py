import json, sys, os, xmltodict, csv
from os.path import join
from utils import *
import shutil

PATH = sys.argv[1]
DIR = PATH.replace('extracted/','')

print("importing",DIR)

file = join(PATH,'Posts.xml')

def clean(x):
    #neo4j-import doesn't support: multiline (coming soon), quotes next to each other and escape quotes with '\""'
    return x.replace('\n','').replace('\r','').replace('\\','').replace('"','')

def open_csv(name):
    return csv.writer(open('csvs/{}.csv'.format(name), 'w'), doublequote=False, escapechar='\\')

try:
    shutil.rmtree('csvs/')
except:
    pass
os.mkdir('csvs')

posts = open_csv('posts')
posts_rel = open_csv('posts_rel')
posts_answers = open_csv('posts_answers')
users = open_csv('users')
users_posts_rel = open_csv('users_posts_rel')
tags = open_csv('tags')
tags_posts_rel = open_csv('tags_posts_rel')

posts.writerow(['postId:ID(Post)', 'title', 'postType:INT','createdAt','score:INT','views:INT','answers:INT','comments:INT','favorites:INT','updatedAt','body'])
posts_rel.writerow([':START_ID(Post)', ':END_ID(Post)'])
posts_answers.writerow([':START_ID(Post)', ':END_ID(Post)'])

users.writerow(['userId:ID(User)', 'name','reputation:INT','createdAt','accessedAt','url','location','views:INT','upvotes:INT','downvotes:INT','age:INT','accountId:INT'])
users_posts_rel.writerow([':START_ID(User)', ':END_ID(Post)'])

tags.writerow(['tagId:ID(Tag)','count:INT','wikiPostId:INT'])
tags_posts_rel.writerow([':START_ID(Post)', ':END_ID(Tag)'])

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            _id = el['@Id']
            posts.writerow([
                _id,
                clean(el.get('@Title','')),
                el['@PostTypeId'],el['@CreationDate'],el.get('@Score'),el.get('@ViewCount'),el.get('@AnswerCount'),el.get('@CommentCount'),el.get('@FavoriteCount'),el['@LastActivityDate'],
                clean(el.get('@Body','')[0:240])
            ])
            if el.get('@AcceptedAnswerId'):
                posts_answers.writerow([_id,el['@AcceptedAnswerId']])
            if el.get('@ParentId'):
                posts_rel.writerow([el['@ParentId'],_id])
            if el.get('@OwnerUserId'):
                users_posts_rel.writerow([el['@OwnerUserId'],_id])
            if el.get('@Tags'):
                eltags = [x.replace('<','') for x in el.get('@Tags').split('>')]
                for tag in [x for x in eltags if x]:
                    tags_posts_rel.writerow([_id,tag])
    except Exception as e:
        print('x',e)
    if i and i % 5000 == 0:
        print('.',end='')
    if i and i % 1000000 == 0:
        print(i)

print(i,'posts ok')

file = join(PATH,'Users.xml')

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            users.writerow([
                el['@Id'],
                clean(el.get('@DisplayName','')),
                el.get('@Reputation'),el['@CreationDate'],el['@LastAccessDate'],el.get('@WebsiteUrl'),
                clean(el.get('@Location','')),el.get('@Views'),el.get('@UpVotes'),el.get('@DownVotes'),el.get('@Age'),el.get('@AccountId')
            ])
    except Exception as e:
        print('x',e)
    if i and i % 5000 == 0:
        print('.',end='')

print(i,'users ok')

file = join(PATH,'Tags.xml')

for i, line in enumerate(open(file)):
    line = line.strip()
    try:
        if line.startswith("<row"):
            el = xmltodict.parse(line)['row']
            tags.writerow([
                el['@TagName'],el.get('@Count'),el.get('@WikiPostId')
            ])
    except Exception as e:
        print('x',e)
    if i and i % 5000 == 0:
        print('.',end='')

print(i,'tags ok')
