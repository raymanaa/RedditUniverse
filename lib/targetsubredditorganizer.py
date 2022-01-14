import os


class SubRedditOrganizer:
    def __init__(self, targetsubreddits, targetsubredditsFileLocation):
        self.targetsubreddits = targetsubreddits
        self.targetsubredditsFileLocation = targetsubredditsFileLocation

    def getTargetSubR(self):
        if not os.path.exists(self.targetsubredditsFileLocation):
            with open(self.targetsubredditsFileLocation, 'w+'):
                pass

        f = open(self.targetsubredditsFileLocation, 'r+')
        data = f.readlines()
        try:
            self.targetsubreddit = data.pop().strip() 
            while (self.targetsubreddit == ""):
                self.targetsubreddit = data.pop().strip()
            
            f.truncate(0)
            f.seek(0)
            f.writelines(data)
            f.close()
            return self.targetsubreddit
        except IndexError as e:
            f.truncate(0)
            f.seek(0)
            f.writelines([x + "\n" for x in self.targetsubreddits])
            f.close()
            return self.getTargetSubR()
