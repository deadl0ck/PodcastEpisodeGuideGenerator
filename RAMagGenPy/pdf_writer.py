import os
from os.path import expanduser

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from image_cache import ImageCache
from page_constants import *

home = expanduser("~")

PDF_LOCATION = f'{home}{os.path.sep}Desktop'
PDF_NAME = "RAEpisodeGuide.pdf"
MAIN_COVER_IMAGE = "images/RACover.png"
MAIN_COVER_TEXT = "Retro Asylum".upper()
MAIN_COVER_TEXT_SUB = "Episode Guide".upper()
DEFAULT_FONT_BOLD = "Helvetica-Bold"
DEFAULT_FONT = "Helvetica"
PAGE_HEIGHT = 30
PAGE_WIDTH = 21
COVER_FONT_SIZE = 36
COVER_FONT_COLOUR = colors.black
TOC_FONT_SIZE = 10
TOC_FONT_COLOUR = colors.black
TOC_TEXT = "Table Of Contents"
TOC_SPACING_DELTA = 0.25
HEADING_FONT = "Helvetica-Bold"
HEADING_FONT_SIZE = 20
SUB_HEADING_FONT = "Helvetica-Bold"
SUB_HEADING_FONT_SIZE = 12
SUB_HEADING_X = 15
SUB_HEADING_Y_DELTA = 0.5
SUB_HEADINGS_LETTERS_PER_LINE = 90
HEADING_FONT_COLOUR = colors.black
LISTEN_IMAGE = "https://i.ibb.co/YPjDW5q/Listen-Image.png"
LISTEN_IMAGE_WIDTH = 80
LISTEN_IMAGE_Y = 1


class PDFWriter:
    def __init__(self):
        self.canvas = Canvas(f'{PDF_LOCATION}{os.path.sep}{PDF_NAME}', pagesize=A4)
        self.image_cache = ImageCache()

    @staticmethod
    def remove_unwanted_text(text: str) -> str:
        if PDFWriter.removal_text_present(text, ""):
            return "--- Tape Loading Error ---"
        return text

    @staticmethod
    def removal_text_present(text: str, cover_url: str) -> bool:
        if cover_url.endswith("RA_error.png"):
            return True

        for current_text in TEXT_TO_REMOVE:
            if current_text.lower() in text.lower():
                return True
        return False

    def new_page(self):
        self.canvas.showPage()

    def write_listen_image(self, link_url: str):
        if link_url is None or link_url == "":
            return
        page_width, page_height = A4
        image_x = (page_width - LISTEN_IMAGE_WIDTH) / 2
        self.insert_image_from_ulr_with_link(LISTEN_IMAGE,
                                             LISTEN_IMAGE_WIDTH,
                                             image_x,
                                             LISTEN_IMAGE_Y,
                                             link_url,
                                             show_boundary=False)

    def write_text_to_page(self,
                           text: str,
                           font_name: str,
                           font_size: int,
                           font_colour: any,
                           x_cm: int,
                           y_cm: float):
        text = PDFWriter.remove_unwanted_text(text)
        canvas_text = self.canvas.beginText(x_cm * cm, y_cm * cm)
        canvas_text.setFont(font_name, font_size)
        canvas_text.setFillColor(font_colour)
        canvas_text.textLine(text)
        self.canvas.drawText(canvas_text)

    def write_heading_to_page_centered(self, text: str, y_cm: int):
        text = PDFWriter.remove_unwanted_text(text)
        font_size = HEADING_FONT_SIZE
        if len(text) > 50:
            font_size = HEADING_FONT_SIZE - 2
        if len(text) > 60:
            font_size = HEADING_FONT_SIZE - 4

        text_width = self.canvas.stringWidth(text, HEADING_FONT, font_size)
        page_width, page_height = A4
        text_x = (page_width - text_width) / 2
        canvas_text = self.canvas.beginText(text_x, y_cm)
        canvas_text.setFont(HEADING_FONT, font_size)
        canvas_text.setFillColor(HEADING_FONT_COLOUR)
        canvas_text.textLine(text)
        self.canvas.drawText(canvas_text)

    def write_sub_heading_to_page(self, text: str, y_cm: int):
        text = PDFWriter.remove_unwanted_text(text)
        if text.strip() == "":
            return

        lines = PDFWriter.split_into_multiline(text)
        for line in lines:
            canvas_text = self.canvas.beginText(SUB_HEADING_X, y_cm)
            canvas_text.setFont(SUB_HEADING_FONT, SUB_HEADING_FONT_SIZE)
            canvas_text.setFillColor(HEADING_FONT_COLOUR)
            canvas_text.textLine(line)
            self.canvas.drawText(canvas_text)
            y_cm -= SUB_HEADING_Y_DELTA * cm

    @staticmethod
    def split_into_multiline(text: str) -> list:
        text = PDFWriter.remove_unwanted_text(text)
        current_text = text
        lines = []
        while current_text != "":
            if len(current_text) >= SUB_HEADINGS_LETTERS_PER_LINE:
                last_space = current_text[:SUB_HEADINGS_LETTERS_PER_LINE].rindex(" ")
                lines.append(current_text[:last_space])
                current_text = current_text[last_space:].strip()
            else:
                lines.append(current_text)
                break

        return lines

    def write_cover(self):
        print('Writing main cover')
        cover_image = ImageReader(MAIN_COVER_IMAGE)
        self.canvas.drawImage(cover_image, 30, 100, 525, 725, preserveAspectRatio=True)

        # self.write_text_to_page(MAIN_COVER_TEXT, DEFAULT_FONT_BOLD, COVER_FONT_SIZE, COVER_FONT_COLOUR, 3, 26)
        self.write_text_to_page(MAIN_COVER_TEXT_SUB, DEFAULT_FONT_BOLD, COVER_FONT_SIZE, COVER_FONT_COLOUR, 5, 3)

        self.new_page()

    def write_toc(self, episodes: list):
        x = 1
        current_y = PAGE_HEIGHT - 1
        self.canvas.bookmarkPage(TOC_BOOKMARK)
        self.write_text_to_page(TOC_TEXT, DEFAULT_FONT_BOLD, TOC_FONT_SIZE + 4, TOC_FONT_COLOUR, 8, current_y)
        current_y -= TOC_SPACING_DELTA

        for episode in episodes:
            skip_episode = PDFWriter.removal_text_present(episode.description, episode.cover)

            if current_y < 1:
                current_y = PAGE_HEIGHT - (TOC_SPACING_DELTA * 3)
                self.new_page()

            current_y -= TOC_SPACING_DELTA
            if skip_episode:
                toc_info = "   [ Episode removed ]"
                self.write_text_to_page(f'{toc_info}',
                                        DEFAULT_FONT_BOLD,
                                        TOC_FONT_SIZE,
                                        TOC_FONT_COLOUR,
                                        x,
                                        current_y)
            else:
                toc_info = f'{episode.title}'
                self.write_text_with_link(f'{toc_info}',
                                          DEFAULT_FONT_BOLD,
                                          TOC_FONT_SIZE,
                                          TOC_FONT_COLOUR,
                                          x,
                                          current_y,
                                          toc_info)

            current_y -= TOC_SPACING_DELTA
        self.new_page()

    # def insert_image_from_ulr_with_link(self, image_url: str, required_width: int, image_x: int, image_y: int,
    #                                     link_url: str = None, show_boundary: bool = True):
    #
    #     if image_url.startswith("http") or image_url.startswith("file"):
    #         response = requests.get(image_url)
    #         image = Image.open(io.BytesIO(response.content))
    #     else:
    #         image = ImageReader(image_url)
    #
    #     # Convert it if we need to
    #     image_format = image_url[image_url.rindex(".") + 1:].lower()
    #     if image_format == "jpg" or image_format == "jpeg":
    #         a = np.asarray(image)
    #         image = Image.fromarray(a)
    #         image_format = "png"
    #
    #     width_percent = (required_width / float(image.size[0]))
    #     height_size = int((float(image.size[1]) * float(width_percent)))
    #     image = image.resize((required_width, height_size), Image.NEAREST)
    #
    #     tmp = tempfile.NamedTemporaryFile()
    #     image.save(tmp.name, format=image_format)
    #     resized_image = ImageReader(tmp)
    #
    #     self.canvas.drawImage(resized_image, image_x, image_y, required_width, height_size, preserveAspectRatio=True,
    #                           showBoundary=show_boundary)
    #
    #     if image_url is not None and image_url.strip() != "":
    #         link_rect = (int(image_x), int(image_y), (int(image_x) + required_width), (int(image_y) + height_size))
    #         self.canvas.linkURL(link_url, link_rect, relative=0, thickness=0)
    #
    # def insert_image_from_ulr_centred(self, url: str, required_width: int, link_url: str = None):
    #     response = requests.get(url)
    #     image = Image.open(io.BytesIO(response.content))
    #
    #     image_format = image.format
    #     if image.format == "JPEG":
    #         image_format = image.format
    #         a = np.asarray(image)
    #         image = Image.fromarray(a)
    #
    #     width_percent = (required_width / float(image.size[0]))
    #     height_size = int((float(image.size[1]) * float(width_percent)))
    #     image = image.resize((required_width, height_size), Image.NEAREST)
    #     image.format = image_format
    #
    #     tmp = tempfile.NamedTemporaryFile()
    #     tmp_name = tmp.name + "." + image.format
    #     image.save(tmp_name, format=image.format)
    #     resized_image = ImageReader(tmp_name)
    #
    #     page_width, page_height = A4
    #     image_x = (page_width - required_width) / 2
    #     image_y = (page_height - height_size) / 2
    #     self.canvas.drawImage(resized_image, image_x, image_y, required_width, height_size, preserveAspectRatio=True,
    #                           showBoundary=True)
    #
    #     if link_url is not None and link_url.strip() != "":
    #         link_rect = (int(image_x), int(image_y), (int(image_x) + required_width), (int(image_y) + height_size))
    #         self.canvas.linkURL(link_url, link_rect, relative=0, thickness=0)
    def insert_image_from_ulr_with_link(
            self,
            image_url: str,
            required_width: int,
            image_x: int,
            image_y: int,
            link_url: str = None,
            show_boundary: bool = True,
    ):
        img, width, height = self.image_cache.get_imagereader_with_conversion(
            image_url,
            mode="width",
            target_size=required_width,
        )

        self.canvas.drawImage(
            img,
            image_x,
            image_y,
            width,
            height,
            preserveAspectRatio=True,
            showBoundary=show_boundary,
        )

        if link_url and image_url and image_url.strip():
            link_rect = (
                int(image_x),
                int(image_y),
                int(image_x + width),
                int(image_y + height),
            )
            self.canvas.linkURL(link_url, link_rect, relative=0, thickness=0)

    def insert_image_from_ulr_centred(
            self,
            url: str,
            required_height: int,
            link_url: str = None,
    ):
        img, width_size, height_size = self.image_cache.get_imagereader_with_conversion(
            url,
            mode="height",
            target_size=required_height,
        )

        page_width, page_height = A4
        image_x = (page_width - width_size) / 2
        image_y = (page_height - height_size) / 2

        self.canvas.drawImage(
            img,
            image_x,
            image_y,
            width_size,
            height_size,
            preserveAspectRatio=True,
            showBoundary=True,
        )

        if link_url and url and url.strip():
            link_rect = (
                int(image_x),
                int(image_y),
                int(image_x + width_size),
                int(image_y + height_size),
            )
            self.canvas.linkURL(link_url, link_rect, relative=0, thickness=0)

    def save_and_close_pdf(self):
        self.canvas.save()

    def create_bookmark(self, bookmark_name: str):
        self.canvas.bookmarkPage(bookmark_name)

    def insert_jump_to_toc_link(self):
        self.write_text_with_link('[Jump to TOC]',
                                  TOC_FONT,
                                  TOC_FONT_SIZE,
                                  SUBTLE_TEXT_COLOUR,
                                  18,
                                  0.3,
                                  TOC_BOOKMARK)

    def write_text_with_link(self,
                             text: str,
                             font_name: str,
                             font_size: int,
                             font_colour: any,
                             x_cm: int,
                             y_cm: int,
                             url: str):
        self.write_text_to_page(text, font_name, font_size, font_colour, x_cm, y_cm)
        if text.strip() == "" or url == NULL_LINK:
            return
        link_rect = PDFWriter.__get_text_rect([text], x_cm, y_cm, y_cm + TOC_JUMP_FONT_HEIGHT)
        if url.startswith("http"):
            self.canvas.linkURL(url, link_rect, relative=0, thickness=0)
        else:
            self.canvas.linkRect("Click to jump to episode", url, link_rect, relative=0, thickness=0)

    @staticmethod
    def __get_text_rect(text_list: list, x_pos: int, start_y: int, end_y: float) -> tuple:
        x1 = x_pos * cm
        y1 = start_y * cm
        # Get max line length
        max_line_length = 0
        for line in text_list:
            if len(line) > max_line_length:
                max_line_length = len(line)
        x2 = x1 + (max_line_length * TOC_JUMP_FONT_WIDTH) * cm  # Approximate character width
        y2 = end_y * cm
        return x1, y1, x2, y2

    def write_text_to_page_centered_x(self,
                                      text: str,
                                      y_cm: int,
                                      font: str,
                                      font_size: int,
                                      font_colour: colors.HexColor):
        text_width = self.canvas.stringWidth(text, font, font_size)
        page_width, page_height = A4
        text_x = (page_width - text_width) / 2
        canvas_text = self.canvas.beginText(text_x, y_cm)
        canvas_text.setFont(font, font_size)
        canvas_text.setFillColor(font_colour)
        canvas_text.textLine(text)
        self.canvas.drawText(canvas_text)
