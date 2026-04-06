import requests

from bs4 import BeautifulSoup

from episode import Episode


class HTMLUtils:
    @staticmethod
    def get_html_from_url(url: str) -> str:
        return requests.get(url).text

    @staticmethod
    def get_all_pages(start_url: str) -> list:
        next_page_url = start_url
        all_pages = [start_url]

        while next_page_url != "":
            current_html = HTMLUtils.get_html_from_url(next_page_url)
            next_page_url = ""
            soup = BeautifulSoup(current_html, 'html.parser')
            my_divs = soup.find_all("div", {"class": "wp-pagenavi"})
            for div in my_divs:
                anchors = div.find_all("a")
                for anchor in anchors:
                    if "nextpostslink" in anchor.get("class"):
                        next_page_url = anchor.get("href")
                        all_pages.append(next_page_url)
                        break
                if next_page_url != "":
                    break

        return all_pages

    @staticmethod
    def get_episodes_from_page(soup: any, episode_urls: list) -> list:
        all_episodes = []
        my_divs = soup.find_all("div", {
            "class": "simple-grid-grid-post-thumbnail simple-grid-grid-post-block"})

        for div in my_divs:
            anchors = div.find_all("a")
            anchor = anchors[0]
            main_page = anchor.get("href")
            # if main_page == "https://retroasylum.com/2026/02/07/episode-363-a-chat-with-the-caulfields-making-films-focused-on-video-games-computer-technology/":
            #     episode_urls.remove(main_page)
            if main_page in episode_urls:
                return all_episodes
            if main_page == "https://retroasylum.com/2016/01/04/bytesize-episode-5-zx-spectrum-visual-compendium/":
                pic = "https://retroasylum.com/wp-content/uploads/2016/01/RASpeccyBitesizeCover.png"
                title = "Bytesize Episode 5: ZX Spectrum Visual Compendium"
            else:
                images = div.find_all("img")
                image = images[0]
                title = image.get("title")
                # pic_small = image.get("src")
                # pic = pic_small[:pic_small.rindex("-")] + pic_small[pic_small.rindex("."):]
                # if pic.endswith("wp.png"):
                #     pic = pic_small
            details = HTMLUtils.get_details(main_page)

            episode = Episode(main_page, details[2], title, details[0], details[1])
            all_episodes.append(episode)
            print(episode.to_string())

        return all_episodes

    @staticmethod
    def get_details(url: str) -> tuple:
        description = None
        mp3 = None
        current_html = HTMLUtils.get_html_from_url(url)
        soup = BeautifulSoup(current_html, 'html.parser')

        my_divs = soup.find_all("div", {"class": "entry-content simple-grid-clearfix"})
        description = ""
        for div in my_divs:
            paragraphs = div.find_all("p")
            for p in paragraphs:
                description = p.get_text().strip()
                if description != "":
                    break
            # paragraph = paragraphs[0]
            # description = paragraph.get_text()

            mp3 = None
            anchors = div.find_all("a")
            for a in anchors:
                link = a.get("href")
                if link is not None and (link.endswith(".mp3") or "drive.google.com" in link):
                    mp3 = link
                    break

        if description == "":
            print("Whoops")

        cover = None
        my_divs = soup.find_all("div", {"class": "wp-block-image is-style-default"})
        if len(my_divs) == 0:
            my_divs = soup.find_all("div", {"class": "wp-block-image"})
        if len(my_divs) == 0:
            my_divs = soup.find_all("div", {"class": "entry-content simple-grid-clearfix"})
        for div in my_divs:
            images = div.find_all("img")
            if len(images) > 0:
                cover = images[0].get("src")
                if cover is not None:
                    break

        if cover is None:
            print("Whoops ! No Cover image found")

        return description, mp3, cover
