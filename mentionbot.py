#!/usr/bin/env python

__AUTHOR__ = "MyBagofTricks"
__COPYRIGHT__ = "2014-2015"
__LICENSE__ = "GPL"
__VERSION__ = "MentionBot 0.9.1b"
__WEBSITE__ = "http://github.com/MyBagofTricks/MentionBot"

import praw
import pymysql
import sys
import signal
from time import sleep, localtime, strftime
from modules import messages as msg
import settings
done = []


class Post(object):

    def __init__(self, sub_id, title, link, author, date):
        self.sub_id = sub_id
        self.title = title
        self.link = link
        self.author = author
        self.date = date


class MySQL(Post):

    def addpost(self):
        msg.print_add(self.link, self.title)
        query = pymysql.connect(settings.db['host'], settings.db['user'],
                                settings.db['pwd'], settings.db['db'],
                                charset='utf8')
        cursor = query.cursor()
        cmd = "INSERT INTO posts (subid, title, link, author, date) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(
            cmd, (self.sub_id, self.title, self.link, self.author, self.date))
        query.commit()
        query.close()

    @staticmethod
    def empty():
        clear = input('[-] Clear the database? [y/n]?: ')
        if clear in ('y', 'Y', 'yes', 'YES'):
            msg.print_clear()
            query = pymysql.connect(settings.db['host'], settings.db['user'],
                                    settings.db['pwd'], settings.db['db'],
                                    charset='utf8')
            cursor = query.cursor()
            cmd = "DELETE FROM posts"
            cursor.execute(cmd)
            query.commit()
            query.close()
        else:
            msg.print_not_clear()

    @staticmethod
    def populate():
        try:
            query = pymysql.connect(settings.db['host'], settings.db['user'],
                                    settings.db['pwd'], settings.db['db'],
                                    charset='utf8')
            cursor = query.cursor()
            cmd = "SELECT * FROM posts"
            cursor.execute(cmd)
            results = cursor.fetchall()
            for row in results:
                subid = row[0]
                done.append(subid)
            query.close()
            msg.print_loaded(len(done))
        except pymysql.Error as e:
            msg.error_gen(e)


# This class handles posts when SQL database can't be authenticated
class NoSQL(Post):

    def addpost(self):
        msg.print_add(self.link, self.title)
        done.append(self.sub_id)


# Sets up database and preloads posts. Failure to authenticate a database
# will fail Mentionbot gracefully into a test mode.
def init_db():
    try:
        MySQL.empty()
        MySQL.populate()
        return True
    except pymysql.OperationalError as e:
        msg.error_nosql(e)
        return False


def handle_sigint(signum, frame):
    msg.error_exit()
    sys.exit()


# Connects to reddit and finds new posts


def main():

    signal.signal(signal.SIGINT, handle_sigint)
    msg.print_title(__VERSION__, __WEBSITE__)
    usesql = init_db()
    r = praw.Reddit(settings.r_login['agent'])
    r.login(settings.r_login['user'], settings.r_login['pwd'])
    while True:
        msg.run_msg(strftime("%a, %y-%m-%d %H:%M:%S %Z ", localtime()),
                    settings.r_login['sub'])
        try:
            subreddit = r.get_subreddit(settings.r_login['sub'])
            for sub in subreddit.get_new(limit=1000):
                title_text = sub.selftext.title()
                has_key = any(
                    string in title_text for string in settings.keywords)
                if sub.id not in done and has_key and usesql is True:
                    done.append(sub.id)
                    post = MySQL(
                        sub.id, sub.title, sub.short_link, sub.author.name,
                        sub.created)
                    post.addpost()
                elif sub.id not in done and has_key and usesql is False:
                    done.append(sub.id)
                    post = NoSQL(sub.id, sub.title, sub.short_link, sub.author)
                    post.addpost()
                else:
                    pass
        except Exception as e:
            msg.error_gen(e)
        sleep(settings.time_sleep)


if __name__ == '__main__':
    main()
