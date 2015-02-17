"""  To do:
- Add optional plain text file support instead of MySQL
- Add option to send an account a notification via reddit message."""
import praw, time, MySQLdb
from datetime import datetime
from sys import argv
from configobj import ConfigObj
config = ConfigObj('mentionbot.setup')

subid_array = []
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
stars = "**********************************************************************\n"

def mysqlempty():
    clear = raw_input('    Clear the database? [y/n]?: ')
    if clear in ('y','Y','yes','YES'):
        print "[*] Clearing database..."
        db = MySQLdb.connect(dbhost,dbuser,dbpass,dbname,charset='utf8')
        cursor = db.cursor()
        cursor.execute("DELETE FROM %s" % dbtable)
        db.commit()
        db.close()
    else:
        print "[-] Not clearing database"

def mysqlpopulate():
    print(stars+"    Populating existing thread(s) from %s: %s..." % (dbname,dbtable))
    db = MySQLdb.connect(dbhost,dbuser,dbpass,dbname,charset='utf8')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM %s" % dbtable)
    results = cursor.fetchall()
    for row in results:
        subid = row[0]
        subid_array.append(subid)
    db.close()
    print(stars+"    %s database loaded. %s post(s) already populated.") \
        % (dbname,len(subid_array))
 
def  run_bot():
    now = str(datetime.now())
    print "    Scanning /r/%s for keyword(s) %s" % (subname,now)
    subreddit = r.get_subreddit(subname)
    for sub in subreddit.get_new(limit=100):
        title_text = sub.selftext.title()
        has_keyword = any(string in title_text for string in keywords)
        if sub.id not in subid_array and has_keyword:
            print "[*] POST ADDED! Link: %s | %s..." % \
            (sub.short_link,sub.title[0:30])
            subid_array.append(sub.id)
            db = MySQLdb.connect(dbhost,dbuser,dbpass,dbname,charset='utf8')
            cursor = db.cursor()
            cursor.execute("INSERT INTO %s(subid, title, link) VALUES\
            (%%s,%%s,%%s)" % dbtable,(sub.id, sub.title, sub.short_link))
            db.commit()
            db.close()

# Program Begins 
print(stars+"""
    Welcome to MentionBot0.2. I scan reddit for keywords and save them 
    to a database.
 
    That's all for now...

"""+stars)
r = praw.Reddit(user_agent)
r.login(redlogin,redpass)
mysqlempty()
mysqlpopulate()
while True:
    run_bot()
    print("    Sleeping for %s seconds..." % time_sleep)
    time.sleep(time_sleep)
