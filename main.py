# main.py
# Driver script for bot
# Author: Andy Ren (ren-andy)

import re
import time
import configparser
import praw
from uwaterlooapi import UWaterlooAPI
from modules.goose_bot import goose_bot

# Bot name string goes here.
# Must match the [section name] in praw.ini 
bot_name= "BOT NAME HERE"

def get_config_keys(section_name, key_name):
    config = configparser.ConfigParser()
    config.read('./config.ini')
    key_value = config[section_name][key_name]
    return key_value
    

def main(): 
    uw_key = get_config_keys("uw_key", "uwaterloo_api_key")
    goose = goose_bot(bot_name, uw_key)
    r_uwaterloo = goose.bot.subreddit("uwaterloo")

    r_uwaterloo_stream = r_uwaterloo.stream.submissions(pause_after=-1)
    inbox_stream = goose.bot.inbox.stream(pause_after=-1)
    while True: 
        for submission in r_uwaterloo_stream:
            if submission is None: 
                break
            # Note: submission replies require a second "content_type" parameter.
            # This is because the parameter is used as a flag for the class methods to work.
            if goose.check_match(submission): # Check if there are courses mentioned.
                goose.submission_reply(submission, "courses") # Make a reply to the course. 
                time.sleep(540.0) # 9 minute rate limit sleeper.   

        for inbox_msg in inbox_stream:
            if inbox_msg is None:
                break
            if isinstance(inbox_msg, praw.models.Comment): # Check if inbox_msg is a comment. 
                goose.inbox_reply(inbox_msg) # Pass the comment into the reply method.
                time.sleep(180.0) # 3 minute rate limit sleeper.


if __name__ == "__main__":
    main()