from PIL import Image, ImageSequence
import os
import random
import urllib

from lib.errors import Handler
from lib.formatter import Formatter

urllib.request.URLopener.version = '''Mozilla/5.0 (Windows NT 6.1)
                                    AppleWebKit/537.36 (KHTML, like Gecko)
                                    Chrome/35.0.1916.153
                                    Safari/537.36 SE 2.X MetaSr 1.0'''


class RTYImage(Formatter, Handler):
    """Image class: handles the formatting of the image through Formatter
    class."""

    def __init__(self, image_name, image_location, image_url,
                 Formatted_images_location, base_size, text,
                 font_name_and_location):
        Formatter.__init__(self, 0, 1)
        self.image_name = image_name
        self.image_location = image_location
        self.image_url = image_url
        self.Formatted_images_location = Formatted_images_location
        self.base_size = base_size
        self.text = text
        self.font_name_and_location = font_name_and_location

    def format_image(self):

        # Add the same image as a blurred background and a resized foreground.
        print('Formatting : ', self.image_location)

        try:
            if os.name == 'nt':
                image_name_extension = self.image_location.split('\\')[-1]
            else:
                image_name_extension = self.image_location.split('/')[-1]

            image_name = image_name_extension.split('.')[-2]
            image_extension = image_name_extension.split('.')[-1]

            self.font_size = random.randint(48, 55)

            if image_extension != 'gif':
                im = Image.open(self.image_location)
                output_image = self.still_img_manipulation(im, self.base_size)
                output_image = self.add_text(
                    output_image, self.text, self.font_name_and_location,
                    self.font_size, (1080 - self.font_size) - 40)
                output_image.save(
                    os.path.join(self.Formatted_images_location,
                                 image_name + '.png'))

            elif image_extension == 'gif':
                im = Image.open(self.image_location)
                frames = []

                for frame in ImageSequence.Iterator(im):
                    temp = self.still_img_manipulation(frame.copy(),
                                                       self.base_size)
                    temp = self.add_text(temp, self.text,
                                         self.font_name_and_location, 40,
                                         (1080 - self.font_size) - 40)
                    frames.append(temp)

                frames[0].save(
                    os.path.join(self.Formatted_images_location,
                                 image_name_extension),
                    save_all=True,
                    append_images=frames[1:])

            return True

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("Formatting of ", self.image_location, " failed.")
            self.handle(e)
            return False

    def download_image(self):

        # Downloads the image.
        try:
            print('\nDownloading : ', self.image_location)
            urllib.request.urlretrieve(self.image_url, self.image_location)

            return True

        except KeyboardInterrupt:
            raise

        except Exception as e:
            print("Download of ", self.image_location, " failed.")
            self.handle(e)

            return False
