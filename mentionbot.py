#!/usr/bin/env python
# Script:  Mentionbot
# Author:  MyBagofTricks
# Version: 0.96
# Website: http://github.com/MyBagofTricks

from time import sleep, localtime, strftime
import praw
import pymysql

try:
    from modules import messages as msg
    import settings as sets
except ImportError as err:
    print ("[x] Error: {}".format(err))
    raise SystemExit
done = []


def addpost(subid, title, link, author, subname, created, sql):
    query = pymysql.connect(
        sets.sql['host'], sets.sql['user'], sets.sql['pwd'], sets.sql['db'],
        charset='utf8mb4'
    )
    try:
        with query.cursor() as cursor:
            cmd = "INSERT INTO posts (subid, title, link, author, subname, created)"\
            "VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(cmd, (subid, title, link, author, subname, created))
            query.commit()
    finally:
        query.close()


def empty():
    query = pymysql.connect(
        sets.sql['host'], sets.sql['user'], sets.sql['pwd'], sets.sql['db'],
        charset='utf8mb4'
    )
    try:
        with query.cursor() as cursor:
            cmd = "DROP TABLE IF EXISTS posts"
            cursor.execute(cmd)
            cmd = "CREATE TABLE posts (subid text,title text,"\
            "link text, author text, subname text, created int(11))"
            cursor.execute(cmd)
            query.commit()
    finally:
        query.close()


def populate():
    query = pymysql.connect(
        sets.sql['host'], sets.sql['user'], sets.sql['pwd'], sets.sql['db'],
        charset='utf8mb4'
    )
    try:
        with query.cursor() as cursor:
            cmd = "SELECT subid FROM posts"
            cursor.execute(cmd)
            result = cursor.fetchall()
            for row in result:
                done.append(row[0])
    finally:
        query.close()
    msg.print_loaded(len(done))



def init_db():
    clear = input('[-] Clear the database? [y/n]?: ')
    if clear in ('Y', 'y'):
        msg.print_clear()
        try:
            empty()
        except pymysql.OperationalError as err:
            msg.error_nosql(err)
            return False
    else:
        populate()
        msg.print_not_clear()





def main():
    try:
        reddit = praw.Reddit(
            client_id=sets.reddit['client_id'], 
            client_secret=sets.reddit['client_secret'],
            password=sets.reddit['password'],
            user_agent=sets.reddit['user_agent'],
            user_name=sets.reddit['user_name'],
    )
    except praw.exceptions.ClientException as err:
        print("[x] Login error  - {err}".format(err=err))
        raise SystemExit
    msg.print_title()
    init_db()
    while True:
        msg.run_msg(strftime("%a, %y-%m-%d %H:%M:%S %Z ", localtime()),
                        sets.conf['subs'])
        for submission in reddit.subreddit("+".join(sets.conf['subs'])).new(limit=1000):
            name = str(submission.author)
            subname = str(submission.subreddit_name_prefixed)
            try:
                has_key = any(
                    string in submission.title.lower() for string in sets.conf['keywords'])
                if submission not in done and has_key:
                    addpost(
                        submission.id, submission.title, submission.shortlink,
                        str(submission.author), str(submission.subreddit_name_prefixed), submission.created, True)
                else:
                    pass
            except Exception as e:
                msg.error_gen(e)
        sleep(sets.conf['sleep'])

if __name__ == '__main__':
    main()
