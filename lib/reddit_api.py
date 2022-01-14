import praw
import urllib

urllib.request.URLopener.version = '''Mozilla/5.0 (Windows NT 6.1)
                                    AppleWebKit/537.36 (KHTML, like Gecko)
                                    Chrome/35.0.1916.153
                                    Safari/537.36 SE 2.X MetaSr 1.0'''


class RedditAPI():
    """Uses the praw python package to get a fixed number of filtered
     submissions and then yields these submissions one by one."""

    def __init__(
            self,
            TargetSubReddit,
            Filter,
            img_download_limit,
            user_agent='python_praw:reddit_image_extractor:v1 (by /u/ka3bamlewi)'
    ):
        self.user_agent = user_agent
        self.TargetSubReddit = TargetSubReddit

        self.clID = '5Fm7DaBY3Y9yOw'
        self.clSEC = 'F7Ow1rOrl754Rr0ORolToFlmsrg'

        self.prawer = praw.Reddit(
            user_agent=self.user_agent,
            client_id=self.clID,
            client_secret=self.clSEC)
        self.submissions = getattr(
            self.prawer.subreddit(self.TargetSubReddit),
            Filter)(limit=img_download_limit)

        print("Initiated RedditAPI for /r/{} and got {} posts.".format(
            self.TargetSubReddit, img_download_limit))

    def submissions_iterator(self):
        """Yields a submission."""

        for self.submission in self.submissions:
            if self.submission.over_18 or self.submission.is_video:
                continue
            else:
                yield self.submission
