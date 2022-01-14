from PIL import Image, ImageFilter, ImageDraw, ImageFont
import numpy


class Formatter():
    """Formats a given image:
    Adds text, formats the text.
    """

    def __init__(self, w=0, h=1):
        self.w = w
        self.h = h

    def still_img_manipulation(self, PIL_image, base_size):
        # ------ Background Preparation ------
        bg = PIL_image.copy()
        bg = bg.convert("RGBA")

        bg_img_size = list(bg.size)
        """A tuple that holds the DIFFRENCE between the base dims and the img dims(needed for the resizing factor to determine which is smaller)."""
        factor_tuple = tuple(numpy.subtract(base_size, bg_img_size))
        """Get the index of the dimension that is the farthest away from the base size's dimensions (it's the biggest difference inside the tuple so "max".)"""
        index_bigger_diff = factor_tuple.index(max(factor_tuple))

        resize_factor = abs(base_size[index_bigger_diff] / float(
            bg_img_size[index_bigger_diff]))

        bg_w_resize = int(bg_img_size[self.w] * resize_factor)
        bg_w_resize = bg_w_resize if bg_w_resize >= base_size[self.
                                                              w] else base_size[
                                                                  self.w]

        bg_h_resize = int(bg_img_size[self.h] * resize_factor)
        bg_h_resize = bg_h_resize if bg_h_resize >= base_size[self.
                                                              h] else base_size[
                                                                  self.h]

        bg = bg.resize((bg_w_resize, bg_h_resize), Image.ANTIALIAS)
        bg = bg.filter(ImageFilter.GaussianBlur(20))
        # --
        # ------ Foreground Preparation ------
        fg = PIL_image.copy()
        fg = fg.convert("RGBA")
        fg_img_size = list(fg.size)

        index_smaller_diff = abs(index_bigger_diff - 1)

        # We need the smaller diffrence because we don't wont the image to
        # surpass the limits.
        resize_factor = abs(base_size[index_smaller_diff] / float(
            fg_img_size[index_smaller_diff]))

        fg_w_resize = int(fg_img_size[self.w] * resize_factor)
        fg_w_resize = fg_w_resize if fg_w_resize <= base_size[self.
                                                              w] else base_size[
                                                                  self.w]

        fg_h_resize = int(fg_img_size[self.w] * resize_factor)
        fg_h_resize = fg_h_resize if fg_h_resize <= base_size[self.
                                                              h] else base_size[
                                                                  self.h]

        fg = fg.resize((fg_w_resize, fg_h_resize), Image.ANTIALIAS)

        # Coordinates of the image.
        merging_tuple = (abs(bg.size[self.w] - fg.size[self.w]) // 2,
                         abs(bg.size[self.h] - fg.size[self.h]) // 2)

        L_dist = (base_size[self.w] - fg.size[self.w]) // 2
        l_dist = (base_size[self.h] - fg.size[self.h]) // 2
        #    print('L_dist : ', L_dist)
        #    print('l_dist : ', l_dist)

        bg.paste(fg, merging_tuple)

        A = merging_tuple[self.w] - L_dist  # Left              # -----B-----
        B = merging_tuple[self.h] - l_dist  # Top               # ---A---C---
        C = A + base_size[self.w]  # Right             # -----D-----
        D = B + base_size[self.h]  # Bottom

        return bg.crop((A, B, C, D))

    def format_text(self, text, image_w, text_w):
        textList = text.split(' ')
        len_textList = len(textList)
        newline_counter = (text_w // image_w) + 1
        """
            exp : if newline = 3:
                1st_iteration :
                    Insert inside textList at the position 1/3
                2nd_iteration :
                    Insert inside textList at the position 2/3
        """
        for newline_position in range(1, newline_counter):
            insert_position = ((newline_position * len_textList) //
                               newline_counter) + newline_position
            textList.insert(insert_position, '\n')

        nextText = ' '.join(textList)
        return nextText.replace(' \n ', '\n')

    def add_text(self,
                 PIL_image,
                 text,
                 font_name,
                 font_size=25,
                 vert_empty_space=75):
        """ PIL_image : The image object obtained from opening or manipulating
        an image using "pillow".
            text : The text to add (use "\n" to determine a new line).
            font_name : The location of the font (as a String).
            font_size : As an integer.
            vert_empty_space : The space between the top of the screen
        and the last line of the text."""

        draw = ImageDraw.Draw(PIL_image)
        # font = ImageFont.truetype(<font-file>, <font-size>)
        font = ImageFont.truetype(font_name, font_size)

        text_w, text_h = draw.textsize(text, font=font)
        if text_w > (PIL_image.size[self.w] - (PIL_image.size[self.w] // 10)):
            text = self.format_text(
                text,
                (PIL_image.size[self.w] - (PIL_image.size[self.w] // 10)),
                text_w)
            text_w, text_h = draw.textsize(text, font=font)

        x = (PIL_image.size[self.w] - text_w) / 2
        y = (PIL_image.size[self.h] - text_h) - vert_empty_space

        shadowcolor = "black"
        # thin border
        draw.multiline_text(
            (x - 1, y), text, font=font, align='center', fill=shadowcolor)
        draw.multiline_text(
            (x + 1, y), text, font=font, align='center', fill=shadowcolor)
        draw.multiline_text(
            (x, y - 1), text, font=font, align='center', fill=shadowcolor)
        draw.multiline_text(
            (x, y + 1), text, font=font, align='center', fill=shadowcolor)

        draw.multiline_text(
            (x, y), text, fill='white', font=font, align='center')

        return PIL_image
