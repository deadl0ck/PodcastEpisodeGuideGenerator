# qow_constants.py
# Reddit API credentials and subreddit configuration for QoW scraping.
# Credentials are loaded via EnvVarUtils so env var handling is centralised.
# To create a Reddit app: https://www.reddit.com/prefs/apps (type: script)

# The subreddit and search query used to find QoW posts
SUBREDDIT_NAME = 'thisweekinretro'
REDDIT_QUERY = 'title:"Question of the"'

REPLACEMENT_LIST = {
    "This week we looked at a list of 10": "What is your most important innovation in gaming? Can you tell us why?",
    "SEGA have been looking for somebody": "We wondered if you were to be a games archivist which company would it be for and what series of games would you focus on.",
    "We were talking about owning digital": "What does your Steam pile of shame look like? Share your stats with us.",
    "Are we being grumpy old men when we": "As parents, tell us about your kids gaming habits and how they compare to yours when you were their age.",
    "Do you remember Chris?": "What in retro do you have an irrational hatred of? What has bugged you for years, or even just days, what do you know you're overreacting to but just can't get over?",
    "Time to show off the stuff that you might not be able to show off else where.": "As you may have seen, Chris was over the moon that the winners of Lego Masters Australia signed his box of reissue space Lego. Is there anythign that you would like to show off?",
    "Last week we talked about recreating some art from an early build of an art package which had no save function, the only record of the images were photos of the screen.": "We want to know if you have ever recreated anything you made back in the day which was perhaps lost over the years or maybe you simply wanted to update it? Is there something that you made that you would like future generations to discover?",
    "Before we get to this week's question don't forget": "Can you name any knockoff arcade games that you had on your home micro or console?",
    "We were talking about how a Japanese Minister wants to end any reliance on old tech with the humble floppy disk firmly in his sights.": "This week we ask you what retro tech would you declare war on? Anything you really want to see disappear and why?",
    "It took a little bit of thought but we finally got to question about sealed retro tech and games?": "It took a little bit of thought but we finally got to question about sealed retro tech and games? Simply put, should they be opened?",
    "After the sad passing of Oliver Frey": "After the sad passing of Oliver Frey we recalled some of his magazine covers that stood out to us. We asked what are your favourite pieces of his work. Have any of those old Crash, Zzap 64 or Amtix covers stuck in your mind since you were young? Were you a fan of his comic book work?",
    "This week we talked about the Fighting Fantasy books and Chris mentioned the Lone Wolf books too.": "We wondered if you have any gaming book recollections? Did the books we mentioned appear in your country or did you have a series of books that we didn't mention, please let us know.",
    "This week it isn't a game related question for a change.": "We want to know, in terms of productivity software which product did you find it the hardest to let go of?  Any platform, any genre of software whether spreadsheet, art package or music maker.",
    "This week's question is one I think we could all answer.": "Which game have you played that you think could/should be made into a movie and/or which movie deserves its own game?",
    "As we take a break for a week we leave you with our question of the week.": "What IT related pranks have you pulled. Created a fake virus or swapped keyboard around? Have you ever got one over on friends, family or work colleagues using tech? Did you own up or were you caught?",
    "This week we took a look at a short Simpsons point and click game in the style of the old LucasArts adventures.": "What was your favorite adventure game?",
}

# Episodes that are known to have no Community Question of the Week.
# The PDF generation skips the QoW section for these episodes.
VALID_MISSING_QOW = {
    75: "Dave was a last minute fill in so there was no Question of the Week",
    105: "Out-take Special 1 - No Question of the Week",
    106: "Out-take Special 2 - No Question of the Week",
    152: "2023 Unseen Bits - No Question of the Week"
}
