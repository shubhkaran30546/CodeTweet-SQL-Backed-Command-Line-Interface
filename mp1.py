import sqlite3
import time
import sys

connection = None
cursor = None

def connect(path):

    '''Connects to the database.
        Args: 
            path - (String) The name of the database.
        Returns:
            None
    '''

    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def disconnect():
    connection.close()

def define_tables():
    '''Creates tables within the database.
        Args: 
            None
        Returns:
            None
    '''

    global connection, cursor
    
    cursor.execute('''DROP TABLE IF EXISTS includes''')
    cursor.execute('''DROP TABLE IF EXISTS lists''')
    cursor.execute('''DROP TABLE IF EXISTS retweets''')
    cursor.execute('''DROP TABLE IF EXISTS mentions''')
    cursor.execute('''DROP TABLE IF EXISTS hashtags''')
    cursor.execute('''DROP TABLE IF EXISTS tweets''')
    cursor.execute('''DROP TABLE IF EXISTS follows''')
    cursor.execute('''DROP TABLE IF EXISTS users''')
    
    users_query=   '''
                        CREATE TABLE users (
                                usr INTEGER,
                                pwd TEXT,
                                name TEXT,
                                email TEXT,
                                city TEXT,
                                timezone FLOAT,
                                PRIMARY KEY (usr)
                                );
                    '''

    follows_query=  '''
                        CREATE TABLE follows (
                                flwer       INTEGER,
                                  flwee       INTEGER,
                                  start_date  DATE,
                                  PRIMARY KEY (flwer,flwee),
                                  FOREIGN KEY (flwer) references users,
                                  FOREIGN KEY (flwee) references users
                                );
                    '''

    tweets_query= 	'''
                        CREATE TABLE tweets (
                                tid	        int,
                                writer      int,
                                tdate       date,
                                text        text,
                                replyto     int,
                                primary key (tid),
                                foreign key (writer) references users,
                                foreign key (replyto) references tweets
                                );
                    '''
    
    hashtags_query= '''
                        CREATE TABLE hashtags (
                                term        text,
                                  primary key (term)
                                );
                    '''
    
    mentions_query= '''
                        CREATE TABLE mentions (
                                tid         int,
                                term        text,
                                primary key (tid,term),
                                foreign key (tid) references tweets,
                                foreign key (term) references hashtags
                                );
                    '''
    
    retweets_query= '''
                        CREATE TABLE retweets (
                                usr         int,
                                tid         int,
                                rdate       date,
                                primary key (usr,tid),
                                foreign key (usr) references users,
                                foreign key (tid) references tweets
                                );
                    '''
    
    lists_query=    '''
                        CREATE TABLE lists (
                                lname        text,
                                owner        int,
                                primary key (lname),
                                foreign key (owner) references users
                                );
                    '''
    
    includes_query= '''
                        CREATE TABLE includes (
                                lname       text,
                                member      int,
                                primary key (lname,member),
                                foreign key (lname) references lists,
                                foreign key (member) references users
                                );
                    '''
    
    cursor.execute(users_query)
    cursor.execute(follows_query)
    cursor.execute(tweets_query)
    cursor.execute(hashtags_query)
    cursor.execute(mentions_query)
    cursor.execute(retweets_query)
    cursor.execute(lists_query)
    cursor.execute(includes_query)
    connection.commit()

    return

def insert_data():
    '''Populates the Database with data.
        Args: 
            None
        Returns:
            None
    '''

    global connection, cursor

    insert_users =  '''
                        INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES
                            (1, '123', 'Chris', 'chris@gmail.com', 'Edmonton', -7.0),
                            (2, '321', 'Shuhb', 'shuhb@gmail.com', 'Edmonton', -7.0),
                            (3, '123', 'Brandon', 'brandon@gmail.com', 'Edmonton', -7.0),
                            (4, '321', 'Jas', 'jas@gmail.com', 'Edmonton', -7.0),
                            (5, 'hi', 'man', 'man@gmail.com', 'a', -7.0),
                            (6, 'hi', 'ram', 'man@gmail.com', 'a', -7.0),
                            (7, 'hi', 'fam', 'man@gmail.com', 'a', -7.0),
                            (8, 'hi', 'fama', 'mana@gmail.com', 'a', -7.0);
                    '''
    
    insert_follows =    '''
                        INSERT INTO follows (flwer, flwee, start_date) VALUES
                            (1, 2, '2023-01-01'),
                            (1, 3, '2022-02-15');
                        '''
    
    insert_tweets = '''
                        INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES
                            (1, 2, '2023-10-29', 'Hello!', 2),
                            (2, 3, '2023-10-29', 'Go Oilers!', NULL),
                            (3, 3, '2023-10-30', 'Go Oilers world!', NULL),
                            (4, 3, '2023-10-31', 'Go Oilers!', NULL),
                            (5, 3, '2023-10-29', "It's cold outside.", NULL),
                            (6, 3, '2023-10-20', "It's hot outside.", NULL),
                            (7, 3, '2023-11-02', 'I love Edmonton.', NULL),
                            (8, 2, '2023-10-30', 'Peace!', NULL),
                            (9, 1, '2023-10-30', 'School sucks!', NULL);
                    '''
    
    insert_retweets = 	'''
                        INSERT INTO retweets (usr, tid, rdate) VALUES
                            (3, 1, '2023-10-31'),
                            (2, 2, '2023-10-30'),
                            (2, 3, '2023-10-31'),
                            (2, 4, '2023-11-01'),
                            (2, 5, '2023-10-31'),
                            (2, 6, '2023-11-01');
                         '''

    cursor.execute(insert_users)
    connection.commit()
    cursor.execute(insert_follows)
    connection.commit()
    cursor.execute(insert_tweets)
    connection.commit()
    cursor.execute(insert_retweets)
    connection.commit()

    return

def show_tweet_info(usr, iteration):
    '''Returns tweet/retweet information of users being followed by a user. Includes the tid, tweet writer's usr, tdate, and tweet text if it was a tweet as well as replyto and retweet date if it was a retweet.
        Only returns 5 tweets/retweets ordered by date. If the iteration increases, the subsequent 5 tweets/retweets will be shown.
        Args: 
            usr - (Int) The user's id, this is the follower.
            iteration - (Int) The iteration of tweets being shown. 0 is the first 5 set of tweets, 1 is the next 5, ect.
        Returns:
            cursor.fetchall() - A set containing all the tweet/retweet information.
    '''

    global connection, cursor
    
    query = """
    SELECT t.tid, t.writer, t.tdate, t.text, t.replyto, 'Tweet' AS tweet_type
    FROM tweets t
    WHERE t.writer IN (
    SELECT flwee
    FROM follows, users
    WHERE flwer = ?
    )
    UNION ALL
    SELECT r.tid, r.usr AS writer, r.rdate AS tdate, '' AS text, r.tid AS replyto, 'Retweet' AS tweet_type
    FROM retweets r
    WHERE r.usr IN (
    SELECT flwee
    FROM follows
    WHERE flwer = :usr
    )
    ORDER BY tdate DESC
    LIMIT 5 OFFSET ?;"""
 
    cursor.execute(query, (usr, usr, iteration * 5))

    return cursor.fetchall()

def search_for_tweets(keywords, iteration):
    '''Returns tweets that contain a keyword in the text. Will display the tid, tweet writer's usr, tdate and tweet text.
        Args:
            keywords - (String) A string of words to be searched.
            iteration - (Int) The iteration of the tweets being shown. 0 is the first 5 set of tweets, 1 is the next 5, etc.
        Returns:
            all_results - (List) A list of the results of the search, limited to 5 tweets in total.
    '''
    
    global connection, cursor

    list_words = keywords.split()
    all_results = []

    query = """
    SELECT DISTINCT t.tid, t.writer, t.tdate, t.text
    FROM tweets t
    LEFT JOIN mentions m ON t.tid = m.tid
    WHERE """

    conditions = []
    parameters = []
    offset = iteration * 5

    for word in list_words:
        if word.startswith('#'):
            conditions.append("m.term = ?")
            parameters.append(word)
        else:
            conditions.append("t.text LIKE ?")
            parameters.append('%' + word + '%')

    if conditions:
        query += " OR ".join(conditions)
        query += " ORDER BY t.tdate DESC LIMIT 5 OFFSET ?;"
        parameters.append(offset)

        cursor.execute(query, parameters)
        all_results = cursor.fetchall()

    return all_results



def showNumberRetweets(tid):
    global connection, cursor 

    query = """
    SELECT COUNT(*)
    FROM retweets
    WHERE tid = ?;
    """
    cursor.execute(query, (tid,))
    result = cursor.fetchone()


    return result

def showNumberReplies(tid):
    global connection, cursor 

    query = """
    SELECT COUNT(*)
    FROM tweets
    WHERE replyto = ?;
    """
    cursor.execute(query, (tid,))
    result = cursor.fetchone()

    return result

def search_usr(usrs, curr_user, page = 1):
    '''
    Searches for a user and provides a list of matching users ordered by name and then by city.
    The function also prompts the user to view the profile of the searched user.

    Args:
        usrs : The search keyword entered by the current user.
        curr_user (int): The user_id of the user who is performing the search.

    Returns:
        None

    This function allows the current user to search for other users using a keyword and displays a list
    of matching users, sorted by name and then by city. The user is also prompted to view the profile of
    the searched user.'''

    # connection = sqlite3.connect('./mini_project_1.db')
    # cursor = connection.cursor()

    global cursor,connection
    curr_date = time.strftime("%Y-%m-%d")
    cursor.execute("SELECT usr, name, city FROM users WHERE name LIKE ? OR city LIKE ?", ('%' + usrs + '%', '%' + usrs + '%'))
    matching_users = cursor.fetchall()

    if not matching_users:
        print("No matching users found.")
        return 1
    name_matching = []
    city_matching = []
    for user in matching_users:
        if usrs.lower() in user[1].lower():
            name_matching.append(user)
        else:
            city_matching.append(user)

    # Combine and ct city matching users based on city length
    city_matching.sort(key=lambda user: len(user[2]))

    # Combine the two lists and provide pagination
    combined_users = name_matching + city_matching

    # Display 5 users at a time based on the page parameter
    users_to_display = combined_users[(page - 1) * 5:page * 5]
    while True:
        for idx, user in enumerate(users_to_display, start=1):
            print(f"{idx}. User: {user[0]}, Name: {user[1]}, City: {user[2]}")
            
        # Check if there are more users to show
        if len(combined_users) > page * 5:
            choice = int(input("Do you want to see more users(6) or select any one of the users above(1-5) or go back (-1)?: "))
            if choice == 6:
                
                search_usr(usrs, curr_user, page+1)
                #print("yayay")
            elif 0<choice<=5:
                try:
                    selected_user_index = int(input("Select a user (enter the number) or to go back keep pressing (-1) until you reach the main menu: ")) - 1
                
                    if 0 <= selected_user_index < len(users_to_display):
                        selected_user = users_to_display[selected_user_index]
                        usr = selected_user[0]

                        # Retrieve user information
                        cursor.execute("SELECT COUNT(DISTINCT tid) FROM tweets WHERE writer = ?", (usr,))
                        tweet_count = cursor.fetchone()[0]

                        cursor.execute("SELECT COUNT(DISTINCT flwee) FROM follows WHERE flwer = ?", (usr,))
                        following_count = cursor.fetchone()[0]

                        cursor.execute("SELECT COUNT(DISTINCT flwer) FROM follows WHERE flwee = ?", (usr,))
                        followers_count = cursor.fetchone()[0]

                        cursor.execute("SELECT tid, tdate, text FROM tweets WHERE writer = ? ORDER BY tdate DESC LIMIT 3", (usr,))
                        recent_tweets = cursor.fetchall()

                        print(f"User: {usr}")
                        print(f"Name: {selected_user[1]}")
                        print(f"City: {selected_user[2]}")
                        print(f"Number of Tweets: {tweet_count}")
                        print(f"Number of Following: {following_count}")
                        print(f"Number of Followers: {followers_count}")

                        for tweet in recent_tweets:
                            print(f"Tweet ID: {tweet[0]}, Date: {tweet[1]}, Text: {tweet[2]}")
                        
                        x = input("""do you want to follow the user(f) or see more tweets(s) or go back(b)?(f/s/b)
                                upon selecting (s), you will be sent back if there are no more tweets to display.: """)
                        if x.lower() == 'f':
                            cursor.execute('''INSERT INTO follows (flwer, flwee, start_date) VALUES 
                                        (?, ?, ?)''', (curr_user, usr, curr_date))
                            connection.commit()
                            print("followed")
                        if x.lower() == 's':
                            cursor.execute("SELECT tid, tdate, text FROM tweets WHERE writer = ? ORDER BY tdate", (usr,))
                            more_tweets = cursor.fetchall()
                            for tweet in more_tweets:
                                print(f"Tweet ID: {tweet[0]}, Date: {tweet[1]}, Text: {tweet[2]}")
                        if x.lower() == 'b':
                            return search_usr(usrs, curr_user, page = 1)
                    if selected_user_index == -2:
                        return -1
                except:
                    print("You inputted an invalid user or you are already following the user.")
            else:
                
                return
        else:
            return
        # Prompt for selecting a user
        
        #connection.close()

def compose(usr, text):
    '''
    Compose a tweet and store it in the database.

    Args:
        usr : The user_id of the user composing the tweet.
        tdate : The date when the tweet is posted.
        text (str): The content of the tweet.

    Returns:
        None

    This function creates a new tweet with the provided user, date, and text content. The tweet is stored in the database.'''

    # connection = sqlite3.connect('./mini_project_1.db')
    # cursor = connection.cursor()

    global cursor,connection
    tdate = time.strftime("%Y-%m-%d")
    cursor.execute("SELECT MAX(tid) FROM tweets")
    latest_tid = cursor.fetchone()[0]
    new_tid = latest_tid + 1
    
    cursor.execute("INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, ?, ?, NULL)", (new_tid, usr, tdate, text))
    connection.commit()

    # Extract hashtags from the tweet content
    hashtags = [word for word in text.split() if word.startswith('#')]

    # Insert hashtags into the Hashtags Table if they don't exist
    for hashtag in hashtags:
        hashtag_text = hashtag[1:]  # Remove the '#' symbol
        cursor.execute("INSERT OR IGNORE INTO hashtags (hashtag_text) VALUES (?)", (hashtag_text,))
        # Get the hashtag_id
        cursor.execute("SELECT hashtag_id FROM hashtags WHERE hashtag_text = ?", (hashtag_text,))
        hashtag_id = cursor.fetchone()[0]

        # Link the tweet to the hashtags in the Mentions Table
        cursor.execute("INSERT INTO mentions (tid, term) VALUES (?, ?)", (new_tid, hashtag_text))

        connection.commit()
    
def reply(usr, text, reply_to):
    '''
    Create a reply to a tweet.

    Args:
        usr : The user_id of the user composing the reply.
        tdate : The date and time of the reply.
        text (str): The content of the reply.
        reply_to (int): The ID of the tweet to which this reply is responding.

    Returns:
        None'''
    global cursor,connection
    # tdate = time.strftime("%Y-%m-%d")
    # c1 = compose(usr, text)
    # cursor.execute("UPDATE tweets SET replyto = :reply_tid WHERE writer = :usr1 AND tid = :c2", {"reply_tid": reply_to, "usr1": usr, "c2": c1})
    # connection.commit()
    #connection.close()

    #
    tdate = time.strftime("%Y-%m-%d")
    cursor.execute("SELECT MAX(tid) FROM tweets")
    latest_tid = cursor.fetchone()[0]
    new_tid = latest_tid + 1
    
    cursor.execute("INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, ?, ?, NULL)", (new_tid, usr, tdate, text))
    connection.commit()

    # Extract hashtags from the tweet content
    hashtags = [word for word in text.split() if word.startswith('#')]

    # Insert hashtags into the Hashtags Table if they don't exist
    for hashtag in hashtags:
        hashtag_text = hashtag[1:]  # Remove the '#' symbol
        cursor.execute("INSERT OR IGNORE INTO hashtags (hashtag_text) VALUES (?)", (hashtag_text,))
        # Get the hashtag_id
        cursor.execute("SELECT hashtag_id FROM hashtags WHERE hashtag_text = ?", (hashtag_text,))
        hashtag_id = cursor.fetchone()[0]

        # Link the tweet to the hashtags in the Mentions Table
        cursor.execute("INSERT INTO mentions (tid, term) VALUES (?, ?)", (new_tid, hashtag_text))

        connection.commit()
    #
    cursor.execute("SELECT COUNT(*) FROM tweets WHERE tid = ?", (reply_to,))
    if cursor.fetchone()[0] == 0:
        print("The tweet you're replying to doesn't exist.")
        return

    # Update the tweet's reply_to field with the reply's ID
    cursor.execute("UPDATE tweets SET replyto = ? WHERE tid = ?", (reply_to, new_tid))
    connection.commit()

def retweet(usr, tid):
    '''Retweets a tweet
    
    Args: 
        usr : The usr_id of the user retweeting the tweet
        tid : Tweet id of the tweet which is being retweeted
    Returns : None'''
    #connection = sqlite3.connect('./mini_project_1.db')
    #cursor = connection.cursor()
    global cursor,connection
    # rdate = time.strftime("%Y-%m-%d")
    # cursor.execute("INSERT INTO retweets (usr, tid, rdate) VALUES (?, ?, ?) ", (usr, tid, rdate))
    # connection.commit()
    # print("You have retweeted the selected tweet.")
    #connection.close()

    res = cursor.execute("SELECT * FROM tweets t WHERE t.tid = ?", (tid,))
    existing_tweet = res.fetchone()
    if existing_tweet:
        rdate = time.strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO retweets (usr, tid, rdate) VALUES (?, ?, ?) ", (usr, tid, rdate))
    else:
        print("Tweet not found. Retweet failed.")
    connection.commit()
    #connection.close()


def list_followers(curr_user):
    global connection, cursor
    allFollowerListQuery = """
    SELECT * FROM follows
    where flwee = ?
    """
    cursor.execute(allFollowerListQuery,(curr_user,))
    result = cursor.fetchall()
    listFollowers = []
    for i in result:
        listFollowers.append(i[0])
    if len(listFollowers)>0:
        for i in range(len(listFollowers)):
            print(str(i +1)+". " + str(listFollowers[i]))
        selected_user_index = int(input("Select a user (enter the number that is to the left) or type -1 to return to menu: "))
        selected_user_index = selected_user_index - 1
        if selected_user_index == -2:
            return -1
        if 0<=selected_user_index<len(listFollowers):
            
            selected_user = listFollowers[selected_user_index]
            cursor.execute("SELECT COUNT(DISTINCT tid) FROM tweets WHERE writer = ?", (selected_user,))
            tweet_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT flwee) FROM follows WHERE flwer = ?", (selected_user,))
            following_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT flwer) FROM follows WHERE flwee = ?", (selected_user,))
            followers_count = cursor.fetchone()[0]

            cursor.execute("SELECT tid, tdate, text FROM tweets WHERE writer = ? ORDER BY tdate DESC LIMIT 3", (selected_user,))
            recent_tweets = cursor.fetchall()

            cursor.execute("SELECT name, city FROM users WHERE usr = ?;", (selected_user,))
            info = cursor.fetchall()

            print(f"User: {selected_user}")
            print(f"Name: {info[0][0]}")
            print(f"City: {info[0][1]}")
            print(f"Number of Tweets: {tweet_count}")
            print(f"Number of Following: {following_count}")
            print(f"Number of Followers: {followers_count}")
            curr_date = time.strftime("%Y-%m-%d")
            for tweet in recent_tweets:
                print(f"Tweet ID: {tweet[0]}, Date: {tweet[1]}, Text: {tweet[2]}")
                x = input("do you want to follow the user(f) or see more tweets(s) or go back(b)?(f/s/b): ")
                if x.lower() == 'f':
                    cursor.execute('''INSERT INTO follows (flwer, flwee, start_date) VALUES 
                                (?, ?, ?)''', (curr_user, selected_user, curr_date))
                    connection.commit
                    print("followed")
                    return -1

                if x.lower() == 's':
                    cursor.execute("SELECT tid, tdate, text FROM tweets WHERE writer = ? ORDER BY tdate", (selected_user,))
                    more_tweets = cursor.fetchall()
                    for tweet in more_tweets:
                        print(f"Tweet ID: {tweet[0]}, Date: {tweet[1]}, Text: {tweet[2]}")
                if x.lower() == 'b':
                    return -1
        else:
            print("Invalid selection. Please select a valid user.")             
        list_followers(curr_user)
    else:
        print("You have no followers")

def display():
    #displays the login screen it gives the user various options to choose from
    print("")
    print("Login Screen")
    print("")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    print("")

def is_valid_email(email):
    #checks if valid email returns true if valid
    return "@" in email and "." in email

def register():
    #registers a user in database it also checks if the information the user entered is in the database
    #returns 1 if something is wrong
    global connection, cursor
    count_query = "SELECT COUNT(*) FROM users"
    cursor.execute(count_query)
    user_count = cursor.fetchone()[0]
    usr = user_count + 1
    name = input("Enter Name: ")
    pwd = input("Enter Password:")

    cursor.execute("SELECT COUNT(*) FROM users WHERE pwd = ?", (pwd,))
    if cursor.fetchone()[0] > 0:
        print("Password is taken")
        return 1

    email = input("Enter Email: ")

    if not is_valid_email(email):
        print("Invalid email.")
        return 1

    city = input("Enter City: ")
    timezone = input("Enter Timezone (-12.00 to 12.00): ")
    try:
        timezone = float(timezone)
        if not (-12.00 <= timezone <= 12.00):
            print("Timezone must be between -12.00 and 12.00.")
            return 1
    except ValueError:
        print("Invalid timezone format.")
        return 1

    register_user = '''
        INSERT INTO users (usr, pwd, name, email, city, timezone)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
    cursor.execute(register_user, (usr, pwd, name, email, city, timezone))
    connection.commit()
    print("User registered successfully with user id:", usr)
    return 0
    
def login(usr,pwd):
    #user enters their information this function checks if the pwd is unique and if the uid exists
    # if something is wrong it returns 1 
    
    global connection, cursor

    cursor.execute("SELECT pwd FROM users WHERE usr = ?", (usr,))
    result = cursor.fetchone()
    
    if result:
        stored_password = result[0]
        if pwd == stored_password:
            print("Login successful.")
        else:
            print("Incorrect password.")
            return 1
    else:
        print("User not found")
        return 1
    return 0
    

def main():
    global connection, cursor
    # path = "./mini_project_1.db"
    
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <database_name>")
        return

    path = sys.argv[1]
    
    connect(path)
    define_tables()
    connection.commit()
    # insert_data()    
    # connection.commit()
    #keywords = "oilers"
    #iteration = 0
    # all_entry = show_tweet_info(1, iteration)
    #all_entry = search_for_tweets(keywords, iteration)
    #print(all_entry)
    #for one_entry in all_entry:        
        #print(one_entry)
    #print(show_tweet_info(1, 0))
    # connection.close()
    return

if __name__ == "__main__":
    main()
