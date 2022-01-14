import random
import re
import shutil
import os
import time

from lib.youtubevideo import YoutubeVideo
from lib.reddit_api import RedditAPI
from lib.image import RTYImage
from lib.errors import Handler
from lib.targetsubredditorganizer import SubRedditOrganizer as SubRedditGiver


class MagicMaker(Handler):
    """HeavyLifts and manages everything between all the classes.
    Downloads images, uses the Image class to format them."""

    def __init__(self, base_size, reddit_download_location,
                 Formatted_images_location, total_videoTime,
                 img_download_limit, redditFilter, targetSubReddits,
                 extensions, font_name_and_locationm, TTS_Location,
                 musicFolder, frames):
        self.name_counter = 0

        self.base_size = tuple(base_size)  # Tuple
        self.default_download_location = reddit_download_location
        self.default_formatted_location = Formatted_images_location
        self.reddit_download_location = ""
        self.Formatted_images_location = ""
        self.total_videoTime = total_videoTime
        self.img_download_limit = img_download_limit
        self.redditFilter = redditFilter
        self.targetSubReddits = TARGETSUBREDDITS  # List
        self.extensions = extensions  # List
        self.font_name_and_location = font_name_and_location
        self.DefaultTTS_Location = TTS_Location
        self.musicFolder = musicFolder
        self.frames = frames

        # LOG:
        self.LogYT_desc = 'Credits to all reddit posts :\n'

    def extensionCheck(self, extension, extensions):
        if not (extension.lower() in extensions):
            return False
        return True

    def titleTxtReplace(self, patternList, text):
        for pattern in patternList:
            text =  re.sub(pattern, "", text)
        return text

    def createFolder(self, folder_path):
        if not os.path.exists(folder_path):
            print("Creating : {}...".format(folder_path))
            os.makedirs(folder_path)

    def add_log(self, title):
        with open('Titles.txt', 'a+') as titles_file:
            titles_file.write('\n' + title)
            titles_file.write('\nVideo Desc :\n')
            titles_file.write(self.LogYT_desc)

    def run(self):
        # testt = 18
        # while testt:
        # testt -= 1
        # targetSubReddit = SubRedditGiver(
        # self.targetSubReddits, "/home/RTY/TargetSubReddits.txt").getTargetSubR()
        for targetSubReddit in self.targetSubReddits:
            self.redditAPI = RedditAPI(targetSubReddit, self.redditFilter,
                                       self.img_download_limit)

            self.reddit_download_location = os.path.join(
                self.default_download_location, targetSubReddit)
            self.createFolder(self.reddit_download_location)

            self.Formatted_images_location = os.path.join(
                self.default_formatted_location, targetSubReddit)
            self.createFolder(self.Formatted_images_location)

            self.TTS_Location = os.path.join(self.DefaultTTS_Location,
                                             targetSubReddit)
            self.createFolder(self.TTS_Location)

            try:

                yt_video = YoutubeVideo(
                    self.TTS_Location,
                    self.musicFolder,
                    self.Formatted_images_location,
                    self.frames,
                    self.base_size,
                    targetSubReddit,
                    uploadYoutubeFileLoc=r"/home/RTY/upload_youtube.py",
                )

                self.name_counter = 0
                TTS_ID = 0  # ID for the text to speech mp3 File
                TTS_Timestamp = 0
                TTS_TimestampDict = {}
                GTTSError = False 
                for submission in self.redditAPI.submissions_iterator():
                    TTS_ID += 1
                    TTS_Name = "{}_{}.mp3".format(targetSubReddit, TTS_ID)
                    img_extension = submission.url.split('/')[-1].split('.')[
                        -1]
                    if not self.extensionCheck(img_extension, self.extensions):
                        img_extension = submission.url.split('/')[-1].split(
                            '.')[-1]
                    if not self.extensionCheck(img_extension, self.extensions):
                        continue
                    if submission.author in ["squid50s"]:
                        continue

                    self.name_counter += 1

                    submission_text = str(submission.title)
                    submission_text = self.titleTxtReplace([r"(?i)psbattle:", r"\[(?i)[OC]\]", r"\[(?i)[Image]\]", r"\[([0-9]{1,})x([0-9]{1,})\]"], submission_text)

                    img_name = 'img{:0>3d}'.format(self.name_counter) + ".png"

                    # Image Class:
                    rty_image = RTYImage(
                        image_name=img_name,
                        image_location=os.path.join(
                            self.reddit_download_location, img_name),
                        image_url=submission.url,
                        Formatted_images_location=self.
                        Formatted_images_location,
                        base_size=self.base_size,
                        text=submission_text,
                        font_name_and_location=self.font_name_and_location)

                    if not (rty_image.download_image()):
                        continue

                    if not (rty_image.format_image()):
                        continue

                    if (yt_video.youtube_title == "") and (
                            len(submission_text) + len(' /r/') +
                            len(targetSubReddit) <= 65):
                        yt_video.youtube_title = submission_text
                        # yt_video.create_title(submission_text, targetSubReddit)
                    
                    TTS_Name = rty_image.image_name.split(".")[0] + '.mp3'
                    needed_time = yt_video.calculate_time_needed(
                        rty_image.text)
                    """ Adding the time needed to display the image to the
                    dictionnary."""
                    yt_video.img_times[rty_image.image_name] = needed_time
                    try:

                        yt_video.img_times[rty_image.image_name] += yt_video.textToSpeech(submission_text, TTS_Name)
                        TTS_TimestampDict[TTS_Name] = yt_video.current_videoTime  
                    except Exception as e:
                        pass
                    yt_video.current_videoTime += yt_video.img_times[
                        rty_image.image_name]

                    yt_video.img_titles[rty_image.image_name] = rty_image.text
                    yt_video.img_authors[rty_image.image_name] = str(
                        submission.author)
                    yt_video.img_urls[rty_image.image_name] = submission.url

                    print('Updating Description...')
                    self.LogYT_desc += str(
                        submission.permalink) + '" --' + str(
                            submission.author) + '\n'

                    if yt_video.current_videoTime >= self.total_videoTime:
                        break

                yt_video.concat_images(yt_video.img_times)

                yt_video.add_music()
                yt_video.add_TTS(TTS_TimestampDict)

                self.add_log(str(yt_video.youtube_title))

                yt_video.upload_to_youtube()
                # This includes adding the thanks to the Authors and Social
                # Media.
                """ PS !!!! Change 'Python3' inside YoutubeVideo upload module to :
                                    Python3 for linux
                                    Python for my windows.
                """

            except Exception as e:
                continue




if __name__ == "__main__":

    TARGETSUBREDDITS = [
        "pics", "aww", "blackmagicfuckery", "GetMotivated", "photoshopbattles",
        "funny", "BlackPeopleTwitter", "mildlyinteresting", "starterpacks",
        "WhitePeopleTwitter", "interestingasfuck", "NatureIsFuckingLit", "Art",
        "space", "food", "GetMotivated", "EarthPorn", "OldSchoolCool"
    ]
    random.shuffle(TARGETSUBREDDITS)

    # -------------------------------------------------------------------------
    # VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
    PRIVACY_STATUS = "public"

    # -------------------------------------------------------------------------
    #   ------------ REDDIT AND VIDEO VARS -------------
    base_size = [1920, 1080]
    img_download_limit = 500
    reddit_download_location = '/root/RTY/downloaded'
    Formatted_images_location = '/root/RTY/results'
    musicFolder = "/home/RTY/music"
    TTS_Location = "/home/RTY/TTS"
    font_name_and_location = 'big_noodle_titling.ttf'
    total_videoTime = 60 * round(random.uniform(1, 2), 2)  # In seconds
    frames = 25

    redditFilter = 'hot'

    extensions = set(['jpg', 'png', 'bmp', 'jpeg'])

    # -------------------------------------------------------------------------
    #   ------------ Removing folders for a new execution -------------

    try:
        print('Removing : ', reddit_download_location)
        shutil.rmtree(reddit_download_location)
    except Exception as e:
        print(e)
    try:
        print('Removing : ', Formatted_images_location)
        shutil.rmtree(Formatted_images_location)
    except Exception as e:
        print(e)

    try:
        print('Removing : ', TTS_Location)
        shutil.rmtree(TTS_Location)
    except Exception as e:
        print(e)
    print()
    # -------------------------------------------------------------------------

    RedditToYoutubeALGO = MagicMaker(
        base_size, reddit_download_location, Formatted_images_location,
        total_videoTime, img_download_limit, redditFilter, TARGETSUBREDDITS,
        extensions, font_name_and_location, TTS_Location, musicFolder, frames)
    RedditToYoutubeALGO.run()
