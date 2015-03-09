#!/usr/bin/python


"""
################################
          Mentionbot
###############################

This is Mentionbot, a simple script which scans reddit.com for
keywords and stores them in a database.

LICENSED UNDER GPL. See LICENSE for details. 


"""

import praw 
import MySQLdb
from time import sleep, localtime, strftime
from sys import argv
from configobj import ConfigObj
config = ConfigObj('mentionbot.setup')
subid_array = []
usesql = True
keywords = config['keywords']
dbhost = config['dbhost']
dbuser = config['dbuser']
dbpass = config['dbpass']
dbname = config['dbname']
dbtable = config['dbtable']
redlogin = config['redlogin']
redpass = config['redpass']
subname = config['subname']
user_agent = config['user_agent']
time_sleep = int(config['time_sleep'])

class MySQL:

    def addpost(self, id, title, link):
        print "[+] POST ADDED! | %s | %s..." % (link, title[0:27])
        subid_array.append(id)
        db = MySQLdb.connect(dbhost, dbuser, dbpass, dbname, charset='utf8')
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO %s(subid, title, link) VALUES(%%s, %%s, %%s)"
            % dbtable, (id, title, link))
        db.commit()
        db.close()

    @staticmethod
    def empty():
        clear = raw_input('[-] Clear the database? [y/n]?: ')
        if clear in ('y', 'Y', 'yes', 'YES'):
            try:
                db = MySQLdb.connect(
                    dbhost, dbuser, dbpass, dbname, charset='utf8')
                cursor = db.cursor()
                cursor.execute("DELETE FROM %s" % dbtable)
                db.commit()
                db.close()
            except Exception, e:
                print "[x] Error = " + str(e)
        else:
             print "[-] Not clearing database"

    @staticmethod 
    def populate():
        try:
            print('*' * 72 +"\n[-] Populating existing thread(s) from %s >> %s"
                    % (dbname, dbtable))
            db = MySQLdb.connect(dbhost, dbuser, dbpass, dbname, charset='utf8')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM %s" % dbtable)
            results = cursor.fetchall()
            for row in results:
                subid = row[0]
                subid_array.append(subid)
            db.close()
            print('*'*72+"\n[+] %s database loaded. %s post(s) already "
                    + "populated.") % (dbname, len(subid_array))
        except Exception, e:
             print "[x] Error = " + str(e)


class Text:

    @staticmethod
    def empty():
        print "This only appears when empting text databases. No sql"

    @staticmethod
    def populate():
        print "This should only appear when populating array, no sql."


def initialize_db():
    if usesql is True:
        MySQL.empty()
        MySQL.populate()
    else:
        Text.empty()
        Text.populate()


def run_bot():
    print ("[-] " + strftime("%a, %y-%m-%d %H:%M:%S %Z ", localtime())
            + "Scanning /r/%s for keyword(s)" % subname)
    subreddit = r.get_subreddit(subname)
    for sub in subreddit.get_new(limit=100):
        title_text = sub.selftext.title()
        has_keyword = any(string in title_text for string in keywords)
        if sub.id not in subid_array and has_keyword and usesql is True:
            post = MySQL()
            post.addpost(sub.id,sub.title,sub.short_link)
        elif sub.id not in subid_array and has_keyword and usesql is False:
            print "This message shouldn't get triggered..."
        else:
            pass

print ('*'*72+"""

*    Welcome to MentionBot0.3. I scan reddit for keywords and save 
*    them to a database.

"""+'*'*72+"\n")

r = praw.Reddit(user_agent)
r.login(redlogin, redpass)
initialize_db()

while True:
    try:
        run_bot()
    except Exception, e:
        print "[x] Error = " + str(e)
    sleep(time_sleep)
