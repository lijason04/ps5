# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

from abc import abstractmethod
from abc import ABC
import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz
import collections
collections.Callable = collections.abc.Callable

#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1

# TODO: NewsStory
class NewsStory(object):

    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate
    def get_guid(self):
        return self.guid
    def get_title(self):
        return self.title    
    def get_description(self):
        return self.description
    def get_link(self):
        return self.link
    def get_pubdate(self):
        return self.pubdate

#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS

# Problem 2
# TODO: PhraseTrigger
class PhaseTrigger(Trigger):
    def __init__(self, phrase):
        for str in string.punctuation:
            phrase = phrase.replace(str, " ")
        self.phrase = phrase.lower()
    def is_phrase_in(self, other):
        other = other.lower()
        for str in string.punctuation:
            other = other.replace(str, " ")
        other = other.split()
        compareString = ""
        for str in other:
            compareString += str + " "
        return self.phrase + " " in compareString



# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhaseTrigger):
    def __init__(self, phrase):
        super().__init__(phrase)
    def evaluate(self, story):
        return self.is_phrase_in(story.get_title())

        
# Problem 4
# TODO: DescriptionTrigger
class DescriptionTrigger(PhaseTrigger):
    def __init__(self, phrase):
        super().__init__(phrase)
    def evaluate(self, story):
        return self.is_phrase_in(story.get_description())
# TIME TRIGGERS

# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.

class TimeTrigger(Trigger):
    def __init__(self, timeStr):
        self.time = datetime.strptime(timeStr, "%d %b %Y %H:%M:%S").replace(tzinfo=pytz.timezone("EST"))

# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def __init__(self, timeStr):
        super().__init__(timeStr)
    def evaluate(self, story):
        if (self.time > story.get_pubdate().replace(tzinfo=pytz.timezone("EST"))):
            return True
        return False
class AfterTrigger(TimeTrigger):
    def __init__(self, timeStr):
        super().__init__(timeStr)
    def evaluate(self, story):
        if (self.time < story.get_pubdate().replace(tzinfo=pytz.timezone("EST"))):
            return True
        return False
# COMPOSITE TRIGGERS

# Problem 7
# TODO: NotTrigger
class NotTrigger(Trigger):
    def __init__(self, ActTrigger) -> None:
        self.ActTrigger = ActTrigger
    def evaluate(self, story):
        return not self.ActTrigger.evaluate(story)
# Problem 8
# TODO: AndTrigger
class AndTrigger(Trigger):
    def __init__(self, ActTrigger0, ActTrigger1) -> None:
        self.ActTrigger0 = ActTrigger0
        self.ActTrigger1 = ActTrigger1
    def evaluate(self, story):
        return  self.ActTrigger0.evaluate(story) and self.ActTrigger1.evaluate(story)
# Problem 9
# TODO: OrTrigger
class OrTrigger(Trigger):
    def __init__(self, ActTrigger0, ActTrigger1) -> None:
        self.ActTrigger0 = ActTrigger0
        self.ActTrigger1 = ActTrigger1
    def evaluate(self, story):
        return  self.ActTrigger0.evaluate(story) or self.ActTrigger1.evaluate(story)

#======================
# Filtering
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    altStories = []
    print(1)
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story) == True:
                altStories.append(story)
    print(2)
    return altStories



#======================
# User-Specified Triggers
#======================
# Problem 11


def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    trigger_dict = {}
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            line = line.split(',')
        
            if ("t" in line[0]):
                triggerActual = -1
                if(line[1] == ('TITLE')):
                    triggerActual = TitleTrigger(line[2])
                elif(line[1] == ('DESCRIPTION')):
                    triggerActual = DescriptionTrigger(line[2])
                elif(line[1] == ('BEFORE')):
                    triggerActual = BeforeTrigger(line[2])
                elif(line[1] == ('AFTER')):
                    triggerActual = AfterTrigger(line[2])
                elif(line[1] == ('NOT')):
                    triggerActual = NotTrigger(trigger_dict[line[2]])
                elif(line[1] == ('AND')):
                    triggerActual = AndTrigger(trigger_dict[line[2]], trigger_dict[line[3]])
                elif(line[1] == ('OR')):
                    triggerActual = OrTrigger(trigger_dict[line[2]], trigger_dict[line[3]])
                else:
                    print('hi')
                    triggerActual = -1
                trigger_dict[line[0]] = triggerActual
            elif "ADD" in line[0]:
                triggerList = []
                for name in line:
                    if name == "ADD": continue
                    triggerList.append(trigger_dict[name])
                return triggerList
                 
    return trigger_dict


SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    print(-2)
    try:
        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line 
        triggerlist = read_trigger_config('triggers.txt')
        print(-3)
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        print(6)
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            print(245)
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")
            print(24)
            # Get stories from Yahoo's Top Stories RSS news feed
           # stories.extend(process("http://news.yahoo.com/rss/topstories"))
            print(441)
            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
    
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

