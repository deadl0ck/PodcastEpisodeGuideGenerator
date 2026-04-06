from bs4 import BeautifulSoup

from html_utils import HTMLUtils
from page_constants import *
from pdf_writer import PDFWriter
from reportlab.lib.units import cm
import pickle
import os

COVER_IMAGE_WIDTH = 500
UNWANTED_TEXT_CHECK = True
REMOVED_EPISODE_IMAGE = "http://retroasylum.com/wp-content/uploads/2015/05/RA_error.png"
PICKLE_EPISODE_FILE = "episodes-cache.pkl"

all_pages = HTMLUtils.get_all_pages(START_URL)

episode_cache = {}

if os.path.exists(PICKLE_EPISODE_FILE):
    with open(PICKLE_EPISODE_FILE, "rb") as f:
        episode_cache = pickle.load(f)

for current_page in all_pages:
    print(f'Getting data for {current_page}')
    current_html = HTMLUtils.get_html_from_url(current_page)
    soup = BeautifulSoup(current_html, 'html.parser')
    episodes = HTMLUtils.get_episodes_from_page(soup, list(episode_cache.keys()))
    # all_episodes.extend(HTMLUtils.get_episodes_from_page(soup))
    for e in episodes:
        if e.url not in episode_cache.keys():
            episode_cache[e.url] = e

episode_cache = dict(sorted(episode_cache.items(), key=lambda kv: kv[1].url, reverse=True))

# Save the cache
with open(PICKLE_EPISODE_FILE, "wb") as f:
    pickle.dump(episode_cache, f)

# if UNWANTED_TEXT_CHECK:
#     for episode in episode_cache:
#         episode.check_for_potential_removal_text()
    # sys.exit()

writer = PDFWriter()
writer.write_cover()
writer.write_toc(list(episode_cache.values()))

for episode in episode_cache.values():
    retry = True
    retry_count = 0
    while retry:
        try:
            skip_episode = PDFWriter.removal_text_present(episode.description, episode.cover)

            if skip_episode:
                print(f'Skipping Episode : {episode.to_string()}')
                retry = False
                continue

            print(f'{episode.title}')
            print(f'Processing Cover: {episode.cover}')
            writer.create_bookmark(episode.title)
            # if episode.cover == "http://retroasylum.com/wp-content/uploads/2024/02/328.png":
            #     print("Here!")
            writer.insert_image_from_ulr_centred(episode.cover, COVER_IMAGE_WIDTH, episode.url)
            writer.write_text_to_page_centered_x(f'(Click image above to jump to episode Webpage)',
                                                 29.2 * cm - 24 * cm,
                                                 SUB_HEADING_FONT,
                                                 SUB_HEADING_FONT_SIZE,
                                                 SUBTLE_TEXT_COLOUR)
            writer.write_heading_to_page_centered(episode.title, 29.7 * cm - 1 * cm)
            writer.write_text_to_page_centered_x(f'(Click image below to jump to episode MP3)',
                                                 29.2 * cm - 26 * cm,
                                                 SUB_HEADING_FONT,
                                                 SUB_HEADING_FONT_SIZE,
                                                 SUBTLE_TEXT_COLOUR)
            writer.write_listen_image(episode.mp3)
            writer.write_heading_to_page_centered(episode.title, 29.7 * cm - 1 * cm)
            writer.write_sub_heading_to_page(episode.description, 29.2 * cm - 1 * cm)
            writer.insert_jump_to_toc_link()
            writer.new_page()
            retry = False
        except Exception as e:
            print(f'EXCEPTION !! Thrown processing:\n{episode.to_string()}')
            print(f'EXCEPTION DETAILS\n=================\n{e}\n=================\n')
            retry_count += 1
            if retry_count > 5:
                SystemExit(1)
writer.save_and_close_pdf()

print("All done !")
