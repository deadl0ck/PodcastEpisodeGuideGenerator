import logging
import re

from podcasts.common.podcast_utils import BasePodcastUtils

ad_markers = ["🛠"]

episode_markers = [
    "This [w|W]eek [I|i]n Retro Podcast \\d+",
    "This [w|W]eek [I|i]n Retro \\d+",
    "TWiR Podcast \\d+",
    "TWiR Ep \\d+",
    "TWiR Episode \\d+",
    "This Week in Retro Podcast Episode \\d+",
]

lines_to_ignore = [
    "Yellow On Blue!",
    "This week's episode is not for those of a nervous disposition, you have been warned!\n\n"
    "Actually its fine, its just Dave in a scary mask.",
    "🛠 Check out PCBWay at https://pcbway.com/ for all your PCB needs! 🛠",
    "PCB Way Project Link: https://www.pcbway.com/project/shareproject/ZX_Nuvo_3_7da4cf60.html",
]

logger = logging.getLogger(__name__)


class TWIRUtils(BasePodcastUtils):
    @staticmethod
    def extract_description(full_desc: str) -> str:
        no_notes_text = "[No detailed show notes for this episode]"
        for ignore in lines_to_ignore:
            if ignore in full_desc:
                full_desc = full_desc.replace(ignore, "").strip()

        lines = full_desc.replace("\n\n", "\n").split("\n")

        return_value = lines[0]
        for marker in ad_markers:
            if marker in lines[0]:
                return_value = lines[1] if len(lines) > 1 else ""
        if return_value.startswith("🏆"):
            return no_notes_text

        if return_value.strip() == "":
            return no_notes_text
        return return_value.strip()

    @staticmethod
    def extract_episode_number(title: str) -> tuple[int, str]:
        episode_details = ""
        for expr in episode_markers:
            match = re.search(expr, title)
            if match is not None:
                episode_details = match.group()
                break
        if episode_details == "":
            return -1, ""

        return BasePodcastUtils.extract_first_number(episode_details), episode_details

    @staticmethod
    def tidy_up_title(title: str) -> str:
        remove_text = ""
        for expr in episode_markers:
            match = re.search(expr, title)
            if match is not None:
                remove_text = match.group()
                break
        if remove_text == "":
            return title
        new_title = title.replace(remove_text, "").strip()

        if new_title.endswith("|") or new_title.endswith("-"):
            new_title = new_title[:len(new_title) - 1].strip()

        if new_title.startswith("|") or new_title.startswith("-"):
            new_title = new_title[1:].strip()

        logger.debug('[Title: %s][New Title: %s]', title, new_title)
        return new_title
