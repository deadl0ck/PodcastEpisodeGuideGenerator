# question_of_the_week.py
# Defines the QOW data model and a hardcoded question->episode mapping for early episodes.

QUESTIONS_AND_EPISODES = {
    "What is your all time favorite Christmas gaming memory?": 60,
    "Which ZX Spectrum artist is your favorite?": 59,
    "What game caused you the most psychological damage?": 58,
    "Apple II or BBC Micro--which was the better machine?": 57,
    "What are your Windows XP Memories?": 56,
    "What retro chip would you like to see a FPGA made of?": 55,
    "What should Atari do to salvage their brand?": 54,
    "Are there any special purpose applications you're still using on your 8 or 16 bit micro?": 53,
    "What did Sinclair computers mean to you?": 52,
    "What game caused you to move from the Amiga or ST to PC?": 51,
    "Do you care if your children like the games you're into?": 50,
    "What should the collective noun for retro fans be?": 49,
    "What do you think of the A500 Mini?": 48,
    "What would it take for you to buy a Commodore Smartphone?": 47,
    "What classic game would you like to see in TATE mode?": 46,
    "Would you consider investing in specific video games as part of your retirement fund?": 45,
    "What was your best charity shop, car boot, or dumpster diving find?": 44,
    "Which computer made you?": 43,
    "What would your dream retro computer museum contain?": 42,
    "What old hobby have you rediscovered, or new hobby have you started during the pandemic?": 41,
    "Whether streaming or a la carte, what would persuade you to buy into a retro gaming ecosystem?": 40,
    "Why do you think classic micros are under-represented in the speedrunning community?": 39,
    "What games company would you like to go back in time and see a fly on the wall documentary made about, and why?": 38,
    "What game do you remember playing as a child that you have been unable to track down as an adult?": 37,
    "What classic video game would you like to see supersized?": 36,
    "What is your favorite Sega arcade game?": 35,
    "What was your first experience with the internet?": 34,
    "What do you think is the most valuable British video game?": 33,
    "What video game art or music would you like to put in a museum for all to enjoy?": 32,
    "What development studio would you like to see come out of retirement to produce a new game for a retro computer or console?": 31,
    "What game would you like to see remade as a point and click adventure?": 30,
    "Is Zelda an RPG?": 29,
    "What do you think is the most aesthetically pleasing computer design of all time?": 28,
    "What was your favorite arcade and what do you remember about it?": 27,
    "What was the worst video game you ever purchased?": 26,
    "What was the most value for money you got from any video game?": 25,
}


class QOW:
    def __init__(self, title: str, question: str, episode_number: int | None, url: str) -> None:
        self.title = title
        self.question = question
        if episode_number is None:
            self.episode_number = self.__get_correct_number()
        else:
            self.episode_number = episode_number

        if self.episode_number == 328:
            self.episode_number = 238
        self.url = url

    def __get_correct_number(self) -> int:
        if self.question in QUESTIONS_AND_EPISODES:
            return QUESTIONS_AND_EPISODES[self.question]
        return -1
