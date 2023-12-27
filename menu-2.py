#Login first
import mp1
import getpass
import sys


replyAndRetweet = """
To reply to this tweet, type "Reply"
To retweet this tweet, type "Retweet"
To go back, type anything except the above two
"""
menuitems = """
Type the following to:

1-5. Show the detail of the numbered tweet
6.   Search for tweets.
7.   Search for users.
8.   Compose a tweet.
9.   List Followers.
10.  Logout.

Type "Next" to go to the next page of tweets
Type "Back" to go to the previous page of tweets

    """

message = """
Enter the tweet number to show its details.
Type "Next" to go to the next page of tweets.
Type "Back" to go to the previous page of tweets.
Type "Main Menu" to go to the main menu.
    """

def SecondMenu(usr,page,selection):
    if 0<int(selection)<=5:
        tweet = mp1.show_tweet_info(usr,page)
        tweetId = tweet[int(selection)-1][0]
        for i in mp1.showNumberRetweets(tweetId):
            print ("Number of retweets:", i)   
        for i in mp1.showNumberReplies(tweetId):
            print("Number of replies:", i)
        print(replyAndRetweet)
        reply_retweet = input("Please enter what you would like to do: ")
        if reply_retweet == "Retweet":
                mp1.retweet(usr,tweetId)
        elif reply_retweet == "Reply":
                text = input("Please input the reply text:\n ")
                mp1.reply(usr, text, tweetId)
                print("You have replied to the selected tweet.\n")
        else:
            return -1
        
        
def MenuSearchForTweets(keywords,iterations,selection,usr):
    if 0<int(selection)<=5:
        tweet = mp1.search_for_tweets(keywords,iterations)
        tweetId = tweet[int(selection)-1][0]
        for i in mp1.showNumberRetweets(tweetId):
            print ("Number of retweets:", i)   
        for i in mp1.showNumberReplies(tweetId):
            print("Number of replies:", i)
        print(replyAndRetweet)
        reply_retweet = input("Please enter what you would like to do: ")
        if reply_retweet == "Retweet":
            mp1.retweet(usr,tweetId)
        elif reply_retweet == "Reply":
            text = input("Please input the reply text:\n ")
            mp1.reply(usr, text, tweetId)
            print("You have replied to the selected tweet.\n")                
        else:
            return -1
            

def menu(usr, page):
    print("")
    print("Main Menu")
    print("")
    print("Tweets by the people you follow in the format (tid, usr, date, text, reply/retweet of, type(retweet/tweet)):")
    print("")
    for i in range(len(mp1.show_tweet_info(usr,page))):
        print(str(i+1) + ".",mp1.show_tweet_info(usr,page)[i])
    print(menuitems)
    x = input("Please select one of the above options: ")
    try:
        if 0<int(x)<=5:
            counter = 0
            while counter != -5:
                if (SecondMenu(usr,page,x) == -1):
                    counter = -5
                    menu(usr,0)
        if int(x) == 6:
            counter = 0
            y = input("Please enter a string with keywords separated by spaces. This is case-insensitive: ")
            print("")
            print("The tweets that match the specified description are:")
            print("")
            
            while counter != -5:
                listTweetSearch = mp1.search_for_tweets(y,counter)
                for i in range(len(listTweetSearch)):
                    print(str(i+1) + ". " + "Tweet Text:" + listTweetSearch[i][3] + " Tweet Date:"+listTweetSearch[i][2]+" By user:" + str(listTweetSearch[i][0])) 
                
                print(message)
                option = input("Please choose an option: ")
                print("")
                try:
                    MenuSearchForTweets(y,counter,option,usr)
                        
                except:
                    if option == "Next":
                        counter = counter + 1
                        for i in mp1.search_for_tweets(y,counter):
                            print(i)
                    elif option == "Back" and counter >0:
                        counter = counter - 1
                        for i in mp1.search_for_tweets(y,counter):
                            print(i)
                    elif option == "Back" and counter == 0:
                        print("\nYou cannot go back further\n")
                    elif option == "Main Menu":
                        counter = -5
                        menu(usr,0)
                    else:
                        print("The option you have selected does not exist. Please try again.")

        elif int(x) == 7:
            userSearchId = str(input("Please enter a keyword to search the users for: "))
            if mp1.search_usr(userSearchId, usr, page = 1) == 1:
                menu(usr,0)
            
            
        elif int(x) == 8:
            #Compose a tweet
            tweet_text = input("Please enter the text you want to have in your tweet:\n")
            mp1.compose(usr,tweet_text)
            print("You have composed and posted your tweet.")
            menu(usr,page)
    

        elif int(x) == 9:
            if mp1.list_followers(usr) == -1:
                menu(usr,0)
            
                
            #List followers
            callFunction = True
        elif int(x) == 10:
            return

    except:
        if x == "Next":
            try:
                menu(usr,page+1)
            except:
                print("You have reached the end of tweets of the people you follow.")
        elif x == "Back" and (page-1) >= 0 :
            menu(usr,page-1)
        elif (page-1) < 0:
            print("You have reached the very first page.")
            menu(usr,page)
         
def main(logged_in = False):
    user_input = 0

    while(user_input != 3 and logged_in == False):
        mp1.display()
        user_input = int(input("Select one of the above: "))

        if (user_input == 1):
            usr = input("Please enter your user id: ")
            pwd = getpass.getpass("Please enter your password: ")
            # pwd = input("Please enter your password: ")
            login_result = mp1.login(usr, pwd)

            if login_result == 0:
               menu(usr,0)
            elif login_result == 1:
                print("User not found")
            elif login_result == 2:
                print("Incorrect Password")

        if (user_input == 2):
            mp1.register()

        if user_input ==3:
            mp1.disconnect()
            print("You have exited the application.")


mp1.main()

#mp1.search_usr("a",1)
#mp1.list_followers(2)
main()
#mp1.reply(1,"HAHAHAHAHAHAHAHA",1)
