def print_title():
    print ('\n' * 80 +  '*' * 80 +  """
   _____                 __  .__             __________        __
  /     \   ____   _____/  |_|__| ____   ____\______   \ _____/  |_
 /  \ /  \_/ __ \ /    \   __\  |/  _ \ /    \|    |  _//  _ \   __\\
/    Y    \  ___/|   |  \  | |  (  <_> )   |  \    |   (  <_> )  |
\____|__  /\___  >___|  /__| |__|\____/|___|  /______  /\____/|__|
        \/     \/     \/                    \/       \/
Verison 0.95a

********************************************************************************

Welcome to Mentionbot! This simple bot scans Reddit for keywords, then
writes the results to a MySQL database.

    Get the latest version at: http://github.com/MyBagofTricks

Requirements:
    - python 3.5 (older versions should still work)
    - pyMySQL - https://github.com/PyMySQL/PyMySQL/
    - PRAW - https://praw.readthedocs.org/en/v2.1.20/
    - MySQL compatible database with
        - database named 'mentionbot'
        - table named 'posts'
        - user created with all privileges to the table

********************************************************************************
""")

def print_add(link, title):
    print ("[+] POST ADDED! | {} | {}...".format(link, title[0:35]))

def print_clear():
    print ("[-] Clearing database...")

def print_not_clear():
    print ("[-] Database was not cleared.")

def print_populating():
    print ("[-] Populating existing threads.")

def print_loaded(done):
    print ("[+] Database successfully loaded. {} post(s) already populated.\n"
           .format(done))

def run_msg(c_time, red_sub):
    print ("[-] {} Scanning {} for keyword(s)".format(c_time, red_sub))

def error_gen(e):
    print ("[x] ERROR! {}".format(e))

def error_nosql(e):
    print ("[x] ERROR! {}\n[x] You are currently using Mentionbot without "
           "a database.\n[x] This mode is mostly for testing and not very "
           "useful.".format(e))

def error_exit():
    print ("\n[*] Exiting Mentionbot.\n[*] Goodbye!")
