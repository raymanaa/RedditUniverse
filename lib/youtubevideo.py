import subprocess
import os
from lib.videomaker import VideoMaker
from gtts import gTTS
from mutagen.mp3 import MP3


class YoutubeVideo(VideoMaker):
    """docstring for YoutubeVideo"""
    PRIVACY_STATUS = "public"

    def __init__(self,
                 TTS_Location,
                 musicLocation,
                 imagesLocationFolder,
                 frames,
                 dimensions,
                 subreddit,
                 uploadYoutubeFileLoc="/home/RTY/upload_youtube.py"):
        VideoMaker.__init__(self, TTS_Location, musicLocation,
                            imagesLocationFolder, frames, dimensions)

        self.youtube_desc = ""
        self.youtube_title = ""
        self.current_videoTime = 0
        self.subreddit = subreddit

        self.img_titles = {}
        self.img_authors = {}
        self.img_urls = {}
        self.img_times = {}

        self.uploadYoutubeFileLoc = uploadYoutubeFileLoc

    def create_title(self):
        if not (self.youtube_title):
            self.youtube_title = "Aww snap!" + ' /r/' + str(self.subreddit)
        else:
            self.youtube_title += ' /r/' + str(self.subreddit)  # pass
        print('------------\nTitle : ', self.youtube_title, '\n------------')

    def textToSpeech(self, submission_text, TTS_Name):
        tmpTTS_FileLoc = os.path.join(self.TTS_Location, 'TMP' + TTS_Name)   
        TTS_FileLoc = os.path.join(self.TTS_Location, TTS_Name)
        
        gTTS(submission_text, lang='en-us', slow=False).save(tmpTTS_FileLoc)
        subprocess.check_call('ffmpeg -i {} -af volume=4 {}'.format(tmpTTS_FileLoc, TTS_FileLoc).split())
        return (MP3(TTS_FileLoc).info.length)

    def addSocialMedia(self):
        self.youtube_desc += """\n\n\nFollow us on:
        Facebook: https://fb.me/RedditUniverse
        Twitter:(Not Added yet)
        Instagram:(Not Added yet)"""
        print("Video Description is set.")

    def addAuthors(self):
        self.youtube_desc += "Big thanks to the authors of these posts :\n"
        self.youtube_desc += ", ".join(
            [x for x in list(self.img_authors.values())])

    def upload_to_youtube(self,
                          category="22",
                          keywords="",
                          privacyStatus=PRIVACY_STATUS):
        # VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

        self.addAuthors()
        self.addSocialMedia()
        self.create_title()

        subprocess.check_call([
            "python3", self.uploadYoutubeFileLoc, "--file",
            self.video_toUpload_location, "--title", self.youtube_title,
            "--description", self.youtube_desc, "--category", category,
            "--keywords", keywords, "--privacyStatus", privacyStatus
        ])
