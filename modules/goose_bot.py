# modules/goose_bot.py 
# Author: Andy Ren (ren-andy)

import re
import praw
from uwaterlooapi import UWaterlooAPI

class goose_bot:
    """Goose bot class, performs actions for a reddit helper bot."""
    def __init__(self, bot_name, api_key):
        print("Logging in to reddit as " + bot_name
              + "...")
        self.bot = praw.Reddit(bot_name)
        print("Logged in as " + bot_name + "!")
        self.uw_key = api_key
        self.uw_api = UWaterlooAPI(api_key)

        self.sub_reply_txt = f'./modules/submission_replies_u_{bot_name}.txt'

##############################################################################
#                        UW COURSE COMMENTING METHODS                        # 
##############################################################################
    def _parse_uw_course_text(self, text):
        """Private method that parses specified text for a course code \n
           i.e: CS 136"""
        match = re.compile('[A-Za-z]{2,}\s?[0-9]{3}')
        course_tuple = re.findall(match, text)
        courses = []

        # Transfer tuple elements into array, removing any possible middle spacing
        for course in course_tuple: 
            course = course.replace(" ", "")
            courses.append(course)
        # Converting to dictionaries removes duplicate courses
        courses = list(dict.fromkeys(courses))
        return courses

    def _gen_uw_course_comment(self, text):
        """Generates a bot reply containing links to courses mentioned
           in a submission and its full title for context."""
        courses = self._parse_uw_course_text(text)
        reply_string = 'Honk! It looks like you mentioned a few university courses in your post!\n\n'
        matching = re.compile('[A-Za-z]{2,}|[0-9]{3}')

        # print url and a short course name descrip.
        for course in courses:
            program_course_array = re.findall(matching, course)
            program_name = program_course_array[0].upper()
            course_code = program_course_array[1]
            if self.uw_api.course(program_name, course_code):
                course = self.uw_api.course(program_name, course_code)
                reply_string += f'\n\n[{program_name} {course_code}]({course["url"]}): {course["title"]} \n\n'
            elif len(courses) == 1: 
                # If one element exists but does not match any course code,
                # no reply should be generated. 
                return ""
        reply_string += "\n\n---\n\n"
        reply_string += f"\n\nI am an automated goose &#x1f9a2; - you can contact my creators [here](https://www.reddit.com/message/compose/?to=/u/{self.bot.user.me().name})"
        return reply_string

##############################################################################
#                          SUBMISSION REPLY METHODS                          # 
##############################################################################
    def check_match(self, submission):
        """Checks if reddit submission title or text contains given content type,
           and if bot has already responded to post.\n
           Returns true if post matches content_type regex,
           and if no bot comment exists on post."""
        if re.search(r'[A-Za-z]{2,4}\s?[0-9]{3}', submission.title) or \
            re.search(r'[A-Za-z]{2,4}\s?[0-9]{3}', submission.selftext):
            if self._post_id_check(submission.id): # bot comment exists, and content match
                return False  
            else: 
                return True  # no bot comment exists, and matches specific content  
        # Insert any other string matches here... 
        else: 
            return False # no content match
    
    def submission_reply(self, submission, content_type="courses"): 
        """Replies to the submission, and adds the submission id to a txt document."""
        comment = ""
        # To check for both submission text and body for content, 
        # just concatenate them into the same string, separated by a space. 
        if content_type == "courses": # for course replies 
            comment = self._gen_uw_course_comment(submission.title + " " + submission.selftext)
        # Insert other content_type flagging here...

        if comment: # If generated comment is non-empty 
            print(f'Replying to post \"{submission.title}\" with id {submission.id}')
            submission.reply(comment)
            self._save_submission_id(submission.id)
                
    def _post_id_check(self, submission_id):
        """Private method to check if submission id exists in txt file"""
        try:
            read_comment_id = open(self.sub_reply_txt)
        except IOError:
            read_comment_id = open(self.sub_reply_txt, 'w+')
            read_comment_id.close()
            read_comment_id = open(self.sub_reply_txt, "r")
        readline_comment_id = read_comment_id.readlines()
        for line in readline_comment_id:
            if submission_id+ "\n" == str(line):
                read_comment_id.close()
                return True
        read_comment_id.close()
        return False # empty txt file or bot did not comment.  

    def _save_submission_id(self, submission_id):
        """Private method that adds submission id of which a reply 
           was made to into a txt document."""
        with open(self.sub_reply_txt, "a+") as write_comment_id:
            print(f'Saving {submission_id} to {self.sub_reply_txt}')
            write_comment_id.write(f'{submission_id}\n')

##############################################################################
#                              MENTION REPLIES                               # 
##############################################################################
    def inbox_reply(self, comment):
        """Replies to inbox mentions or comments replies on posts, when they match specific 
           words or phrases below."""
        if "good bot" in comment.body.lower():
            comment.reply(self._good_bot())
            comment.mark_read()
        elif "bad bot" in comment.body.lower():
            comment.reply(self._bad_bot())
            # add the user to a filter list
            comment.mark_read()
        elif "thank mr. goose" in comment.body.lower(): 
            comment.reply(self._thank_mr_goose())
            comment.mark_read()
        elif "bruh moment" == comment.body.lower() \
            or "bruh"== comment.body.lower():
            comment.reply(self._bruh_moment())
            comment.mark_read()
        else:
            return
        print(f'Replying to comment {comment.id}, found on the post ' +   
              f'\"{comment.submission.title}\", with id {comment.submission.id}') 

    def _good_bot(self):
        return 'honk honk! &#x1f9a2;'

    def _bad_bot(self):
        # put user on removal list
        return 'sad honk :('

    def _thank_mr_goose(self):
        return 'thank mr. goose <3'

    def _bruh_moment(self):
        return 'bruh moment'

##############################################################################
#                           String overload functions                        # 
##############################################################################
    def __repr__(self):
        return str({"Bot name":     self.bot.user.me().name,
                    "Bot ID":       self.bot.user.me().id,
                    "UW key":       self.uw_key,
                    "Bot karma":    self.bot.user.me().comment_karma,
                    "Bot creation": self.bot.user.me().created_utc})

    def __str__(self):
        return  f'Bot name:     {self.bot.user.me().name} \n' + \
                f'Bot ID:       {self.bot.user.me().id} \n' + \
                f'UW key:       {self.uw_key} \n' + \
                f'Bot karma:    {self.bot.user.me().comment_karma} \n' + \
                f'Bot creation: {self.bot.user.me().created_utc}'


