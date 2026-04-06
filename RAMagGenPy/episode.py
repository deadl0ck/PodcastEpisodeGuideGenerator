from page_constants import *
from nltk.tokenize import word_tokenize

NUM_TOKENS_EITHER_SIDE_OF_TEXT = 3


class Episode:
    def __init__(self,
                 url: str,
                 cover: str,
                 title: str,
                 description: str,
                 mp3: str):
        self.url: str = url
        self.cover: str = cover
        self.title: str = title
        self.description = description
        self.mp3 = mp3

    def to_string(self) -> str:
        data = f'Episode URL : {self.url}\n'
        data += f'Cover Image : {self.cover}\n'
        data += f'Title       : {self.title}\n'
        data += f'Description : {self.description}\n'
        data += f'MP3         : {self.mp3}\n'
        return data

    def check_for_potential_removal_text(self):

        for current_text in POTENTIAL_REMOVAL_TEXT:
            # if self.title == "Episode 164 – Revival 2017: Paul Rose":
            #     print("HERE")
            text_to_check = [self.title, self.description, self.url]
            for current_details_to_check in text_to_check:
                if current_text.lower() in current_details_to_check.lower():
                    print('--------------------------------------------------------------')
                    Episode.show_unwanted_text(current_details_to_check)
                    print(f'Episode Webpage    : {self.url}')
                    print(f'Episode Title      : {self.title}')
                    print(f'Episode Description: {self.description}')

    @staticmethod
    def show_unwanted_text(text):
        tokens = word_tokenize(text)
        for idx, token in enumerate(tokens):
            for current_text in POTENTIAL_REMOVAL_TEXT:
                if token.lower().strip() == current_text.lower().strip():
                    start = idx - NUM_TOKENS_EITHER_SIDE_OF_TEXT
                    end = idx + NUM_TOKENS_EITHER_SIDE_OF_TEXT
                    if start < 0:
                        start = 0
                    if end > len(tokens):
                        end = len(tokens) - 1
                    text = []
                    for j in range(start, end):
                        text.append(tokens[j])
                    print(f'Potential problem  : [ {" ".join(text)}]')
