# MentionBot 0.9.5a
This script searches reddit for keywords in self posts and records any
hits into an SQL database. It's handy for tracking topics, social media
notifications, and data analysis.

# Requirements
 - python 3.5+ (2.7 should still work) 
 - pymysql - For interacting with the database: 
      https://github.com/PyMySQL/PyMySQL/
 - PRAW - Reddit API Wrapper. Install here: 
      here: https://praw.readthedocs.org/en/v2.1.20/
 - MySQL or compatible database to store records.

# Setup
1. MySQL:
  * Create a user with access to a new database
  * create a table named 'posts' with the columns: 
    * subid (TEXT or VARCHAR(10+))
    * title (TEXT or VARCHAR(255))
    * link (TEXT or VARCHAR(30+)) 
    * author (TEXT or VARCHAR(20+))
    * Posix Time (INT)
2. Open 'settings.py' and enter your configuration.
3. Run Mentionbot using 'python mentionbot.py'.

# Future plans
This project is essentially retired. Its functionality will
be integrated into an upcoming cache of reddit tools.
