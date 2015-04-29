#!/usr/bin/python

########################################################################
#                              Mentionbot                              #
########################################################################

# This is Mentionbot, a simple script which scans reddit.com for
# keywords and stores them in a database.
#
# LICENSED UNDER GPL. See LICENSE for details.
#
# github : https://github.com/MyBagofTricks/MentionBot

import praw
import pymysql
from time import sleep, localtime, strftime
from sys import argv
from configobj import ConfigObj
subid_array = []
config = ConfigObj('mentionbot.setup')
keywords = config['keywords']
dbhost = config['dbhost']
dbuser = config['dbuser']
dbpass = config['dbpass']
redlogin = config['redlogin']
redpass = config['redpass']
subname = config['subname']
user_agent = config['user_agent']
time_sleep = int(config['time_sleep'])


class MySQL(object):

    def addpost(self, id, title, link):
        print ("[+] POST ADDED! | {} | {}...".format(link, title[0:35]))
        db = pymysql.connect(dbhost, dbuser, dbpass, 'mentionbot',
                             charset='utf8')
        cursor = db.cursor()
        cmd = u"INSERT INTO posts (subid, title, link) VALUES (%s, %s, %s)"
        cursor.execute(cmd, (id, title, link))
        db.commit()
        db.close()

    @staticmethod
    def empty():
        clear = raw_input('[-] Clear the database? [y/n]?: ')
        if clear in ('y', 'Y', 'yes', 'YES'):
            print ("[-] Clearing database...")
            db = pymysql.connect(
                dbhost, dbuser, dbpass, 'mentionbot', charset='utf8')
            cursor = db.cursor()
            cmd = "DELETE FROM posts"
            cursor.execute(cmd)
            db.commit()
            db.close()
        else:
            print ("[-] Database was not cleared.")

    @staticmethod
    def populate():
        try:
            print('*' * 80 + "\n[-] Populating existing thread")
            db = pymysql.connect(
                dbhost, dbuser, dbpass, 'mentionbot', charset='utf8')
            cursor = db.cursor()
            cmd = "SELECT * FROM posts"
            cursor.execute(cmd)
            results = cursor.fetchall()
            for row in results:
                subid = row[0]
                subid_array.append(subid)
            db.close()
            print ('*' * 80 + "\n[+] Database loaded. {} post(s) already "
                  + "populated.\n" + '*' * 80).format(len(subid_array))
        except IOError as e:
            print ("[x] Error = " + str(e))


class NoSQL(object):

    def addpost(self, id, title, link):
        print ("[+] POST ADDED! | {} | {}...".format(link, title[0:35]))
        subid_array.append(id)


def initialize_db():
    try:
        MySQL.empty()
        MySQL.populate()
        return True
    except Exception as e:
        print ("[x] ERROR! Unable to load database!\n[x] " +  str(e) +
            "\n[x] You are currently using Mentionbot without a database. \n"+
            "[x] This mode is mostly for testing and not very useful.")
        return False


def run_bot():
    print ("[-] " + strftime("%a, %y-%m-%d %H:%M:%S %Z ", localtime())
           + "Scanning /r/{} for keyword(s)".format(subname))
    try:
        subreddit = r.get_subreddit(subname)
        for sub in subreddit.get_new(limit=1000):
            title_text = sub.selftext.title()
            has_keyword = any(string in title_text for string in keywords)
            if sub.id not in subid_array and has_keyword and usesql is True:
                subid_array.append(sub.id)
                post = MySQL()
                post.addpost(sub.id, sub.title, sub.short_link)
            elif sub.id not in subid_array and has_keyword and usesql is False:
                subid_array.append(sub.id)
                post = NoSQL()
                post.addpost(sub.id, sub.title, sub.short_link)
            else:
                pass
    except IOError as e:
        print ("[x] Error " + str(e))
    except ValueError as e:
        print ("[x] Error " + str(e))
    except Exception as e:
        print ("[x] Error " + str(e))


print ('*' * 80 + """
*
*    Welcome to MentionBot0.9a. I scan reddit for keywords and save
*    them to a database. Why? I don't know!
*
*    To exit, press CTRL+c.
*
*    github : https://github.com/MyBagofTricks/MentionBot
""" + '*' * 80 + "\n")

r = praw.Reddit(user_agent)
r.login(redlogin, redpass)
usesql = initialize_db()

try:
    while True:
        run_bot()
        sleep(time_sleep)
except KeyboardInterrupt, SystemExit:
    print ("\n[*] Exiting Mentionbot.\n[*] Goodbye!")
