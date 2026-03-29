"""Fetch and normalize TWIR Community Question of the Week entries from Reddit."""

from __future__ import annotations

import logging
import re
from typing import Any

import praw

from env_var_utils import (
    EnvVarUtils,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_PASSWORD,
    REDDIT_USER_AGENT,
    REDDIT_USERNAME,
)
from podcasts.twir.page_constants import NULL_LINK
from podcasts.twir.qow.qow_cache import QOWCache
from podcasts.twir.qow.qow_constants import REDDIT_QUERY, REPLACEMENT_LIST, SUBREDDIT_NAME
from podcasts.twir.qow.question_of_the_week import QOW

logger = logging.getLogger(__name__)


class QuestionOfTheWeekProcessor:
    """Scrape, normalize, and cache Community Question of the Week entries."""

    def __init__(self) -> None:
        self.reddit = praw.Reddit(
            client_id=EnvVarUtils.get_env_var(REDDIT_CLIENT_ID),
            client_secret=EnvVarUtils.get_env_var(REDDIT_CLIENT_SECRET),
            username=EnvVarUtils.get_env_var(REDDIT_USERNAME),
            password=EnvVarUtils.get_env_var(REDDIT_PASSWORD),
            user_agent=EnvVarUtils.get_env_var(REDDIT_USER_AGENT)
        )
        self.questions = []
        self.episodes_and_questions: dict[int, QOW] = {}
        self.episode_cache = QOWCache()

    @staticmethod
    def __extract_question(title: str, text: str) -> str:
        if text.strip() == "":
            text = title
        lines = text.splitlines()
        non_blank_lines = [line.strip() for line in lines if line.strip()]
        text = "\n".join(non_blank_lines)

        if (":" in title or "-" in title) and title.strip().endswith("?"):
            text = title

        lines = text.splitlines()
        if len(lines) > 1 and (
                lines[0].strip() == "" or
                lines[0].endswith("!") or
                lines[0].endswith("...") or
                lines[0].endswith(":") or
                lines[0].endswith("this episode is") or
                len(lines[0]) < 15):
            text = "\n".join(lines[1:])
        return_text = ""
        if ":" in title and "eek: Episode" not in title:
            return_text = title.split(":")[1].strip()
        if "- W" in title:
            return_text = "W" + title.split("- W")[1].strip()
        if "- Is" in title:
            return_text = "Is " + title.split("- Is")[1].strip()
        if "\n" not in text:
            return_text = text.strip("*")
        else:
            return_text = text.split("\n")[0].strip("*")

        pattern = r'\*(.*?)\*'
        return_text = re.sub(pattern, r'\1', return_text)

        return_text = return_text.replace("TWiR Community Question of the Week: ", "")
        return_text = return_text.replace("Community Question of the Week - ", "")
        return_text = return_text.replace("Community Question of the Week: ", "")
        return_text = return_text.replace("Community Question of the Week- ", "")
        return_text = return_text.replace("Community Question of the Weeks - ", "")

        return_text = return_text.replace("(https://preview.redd.it/6b55y9p8pp091.png?width=1200&format=png&auto="
                                          "webp&s=f2d9761156fa794352ffc85f789e13f41f1b4c4c)", "")
        return_text = return_text.replace("[Its all about Ocean this week", "Its all about Ocean this week")
        return_text = return_text.replace("logo mean to you?]", "logo mean to you?")

        return return_text.strip()

    @staticmethod
    def __extract_episode_number(text: str) -> int | None:
        match = re.search(r'Episode\s+(\d+)', text)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def __replace_badly_formed_questions(question_to_check: str) -> str:
        """Replace known malformed question texts with curated fixed values."""
        for item in REPLACEMENT_LIST:
            if item in question_to_check:
                return REPLACEMENT_LIST[item]
        return question_to_check

    @staticmethod
    def __add_missing_episodes() -> list[QOW]:
        """Return hardcoded fallback QoW entries for episodes missing Reddit posts."""
        return_list: list[QOW] = []

        q = QOW("What video game art or music would you like to put in a museum for all to enjoy?",
                "What video game art or music would you like to put in a museum for all to enjoy?",
                32,
                NULL_LINK)
        return_list.append(q)

        q = QOW("Why do you think classic micros are under-represented in the speedrunning community?",
                "Why do you think classic micros are under-represented in the speedrunning community?",
                39,
                "https://www.reddit.com/r/thisweekinretro/comments/nsrjsj/why_do_you_think_classic_micros_are/")
        return_list.append(q)

        q = QOW("Community Question: What was your best charity shop, car boot, or dumpster diving find?",
                "What was your best charity shop, car boot, or dumpster diving find?",
                44,
                "https://www.reddit.com/r/thisweekinretro/comments/ohfa44/community_question_what_was_your_best_charity/")
        return_list.append(q)

        return return_list

    def __store_to_dict(self) -> None:
        """Store scraped questions in a sorted episode-number mapping and cache it."""
        data: dict[int, QOW] = {}
        for e in self.questions:
            data[e.episode_number] = e

        self.episodes_and_questions = dict(sorted(data.items()))
        self.episode_cache.update_cache(self.episodes_and_questions)

    def process_qow(self) -> None:
        """Fetch QoW entries from Reddit, normalize them, and update the cache."""
        logger.info('Processing Question of the Week - please wait....')
        subreddit = self.reddit.subreddit(SUBREDDIT_NAME)
        query = REDDIT_QUERY
        results = subreddit.search(query, sort='new', limit=1000)

        for post in results:
            if post.title in self.episode_cache.episodes_by_title:
                self.questions.append(self.episode_cache.episodes_by_title[post.title])
                continue
            post_title = post.title.replace('"', '""').replace("’", "'")
            question = QuestionOfTheWeekProcessor.__extract_question(post.title,
                                                                     post.selftext).replace("’", "'")
            episode_number = QuestionOfTheWeekProcessor.__extract_episode_number(post_title)

            question = QuestionOfTheWeekProcessor.__replace_badly_formed_questions(question)
            qow = QOW(title=post_title, question=question, episode_number=episode_number, url=post.url)

            if qow.episode_number > 0:
                self.questions.append(qow)
        self.questions.extend(QuestionOfTheWeekProcessor.__add_missing_episodes())
        self.__store_to_dict()
        logger.info('Finished processing question of the week')
