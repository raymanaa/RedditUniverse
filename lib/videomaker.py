import os
import shutil
import random
import subprocess
import math
import collections

import cv2
"""from PIL import Image, ImageSequence
import numpy"""  # For the GIFEING PART

from lib.errors import Handler


class VideoMaker(Handler):
    """Handles all the video making."""

    def __init__(self, TTS_Location, musicLocation, imagesLocationFolder,
                 frames, dimensions):
        self.TTS_Location = TTS_Location
        self.musicLocation = musicLocation
        self.imagesLocationFolder = imagesLocationFolder
        self.output_name = "OutNoMusic.mp4"
        self.out_video_location = os.path.join(self.imagesLocationFolder,
                                               self.output_name)
        self.video_toUpload_location = os.path.join(self.imagesLocationFolder,
                                                    "OutMusic.mp4")
        self.frames = frames
        self.dimensions = dimensions

    def concat_images(self, times_needed):
        ims = []
        for f in os.listdir(self.imagesLocationFolder):
            if f.endswith('png') or f.endswith('gif'):
                ims.append(f)
        ims = sorted(ims)
        # Define the codec and create VideoWriter object
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        out_video = cv2.VideoWriter(self.out_video_location, codec,
                                    self.frames, self.dimensions)

        for image in ims:
            if image.endswith('png'):
                print('##Adding {} to the mix.'.format(image))
                time_needed = times_needed[image]
                image_path = os.path.join(self.imagesLocationFolder, image)
                frame = cv2.imread(image_path)

                num_frames = self.frames * time_needed
                while num_frames >= 0:
                    out_video.write(frame)
                    num_frames -= 1
                print('Added {} to the video.'.format(image))

                ##########################
                # Check the V1 Old File for the GIF CREATION.
                ##########################
        cv2.destroyAllWindows()
        out_video.release()

    def choose_music(self):
        try:
            self.musicLocation = os.path.join(os.getcwd(), self.musicLocation)
            musicFolder = [
                os.path.join(self.musicLocation, x)
                for x in os.listdir(self.musicLocation)
            ]
            random.shuffle(musicFolder)
            with open("music.txt", "w+") as f:
                for line in musicFolder:
                    f.write("file '" + line + "'\n")
            return True
        except Exception as e:
            self.handle(e)
            return False

    def add_music(self):

        # ffmpeg -i videoWithNoMusic.avi -i audio.mp3 -codec copy output.mp4
        if self.choose_music():
            subprocess.check_call(
                'ffmpeg -i'.split() + [self.out_video_location] +
                '-f concat -safe 0 -i'.split() + ['music.txt'] +
                ['-shortest', "-y", "-af" , "volume=0.4", "-vcodec", "copy"] +
                [self.video_toUpload_location]) # "-acodec", "copy", 

            print('Finished adding music, New file : ',
                  self.video_toUpload_location)

    def add_TTS(self, timeDict):
        '''Add text to speech to video.'''
        '''ffmpeg -i {self.video_toUpload_location} {-i AudioFiles} -filter_complex "[{ID}]adelay={Value}|{Value}[s{ID}];[0:a][{ID_List}]amix=3[ttsMix]" -map 0:v -map [ttsMix] -c:v copy {TTS_VideoFileLoc}.mp4'''
        if (not timeDict):
            return
        timeDict = collections.OrderedDict(sorted(timeDict.items()))
        TTS_VideoFileLoc = os.path.join(self.TTS_Location, "OutMusic.mp4")

        ID = 0  # Used to generate variables needed for ffmpeg
        # Lists used in the complex filter
        iList = []
        adelaySTR = ''
        amixSTR = ''
        for key, value in timeDict.items():
            ID += 1
            iList += ['-i', os.path.join(self.TTS_Location, key)]
            value = 1000 * int(math.ceil(value))
            adelaySTR += f'[{ID}]adelay={value}[s{ID}];'
            amixSTR += f'[s{ID}]'

        ffmpegCMDList = f'ffmpeg -i {self.video_toUpload_location}'.split(
        ) + iList + [
            f'-filter_complex',  adelaySTR + f'[0:a]' + amixSTR +
            f'amix={ID+1}[ttsMix]'
        ] + f'-map 0:v -map [ttsMix] -c:v copy {TTS_VideoFileLoc}'.split()
        print(ffmpegCMDList)
        subprocess.check_call(ffmpegCMDList)

        shutil.move(TTS_VideoFileLoc, self.video_toUpload_location)
        print('##Finished adding TextToSpeech, New file : ',
              self.video_toUpload_location)

    def calculate_time_needed(self, text):
        ''' Calculate the amount of time needed to read the text.'''

        wpm = 134  # readable words per minute

        # average number of chars in a word
        word_length = sum(list(map(lambda x: len(x), text.split(' ')))) // len(
            text.split(' '))
        words = len(text) / word_length
        words_time = int(((words / wpm) * 60))

        delay = 1  # milliseconds before user starts reading the notification
        bonus = 1  # extra time

        return int(delay + words_time + bonus)

    def gif_concat_video(self, gif):
        subprocess.check_call("ffmpeg -r 1/5 -i".split() + gif +
                              "-vcodec mpeg4 -y movie.mp4".split())
        """ -r : the framerate (each image will be held for 5 seconds )
            -i : input files with the format : imgxx.jpg
            -y : output video """
