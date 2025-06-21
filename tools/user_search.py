"""
This module allows you to search for usernames across a wide list of social media, gaming,
professional, entertainment, and NSFW websites. The tool also supports optional TOR usage
and deep analysis using Google Dorking techniques.

Core Features:
- Username checks on over 150 websites (including NSFW sites optionally)
- Optional TOR proxy support for anonymity
- Automatic saving of results to a text file
- Option to extend analysis with Google Dorking
"""

import requests
import random
from core.save_data import save_data
from tools.g_dorking import multi_search, gg_connection
from core.agents import agents
from core.display import (
    prRed, prGreen, prCyan, prYellow, maRed, maBlue, maCyan,
    maYellow, maOrange, maMagenta, maGreen, maPink,
    maBold, maUnderline, maBlack, maLightBlue, maLightGreen, maLightYellow,
    maBrown, maTeal, maSkyBlue,
    backRed, display_extra, display_error,
    display_validate, display_info, display_question, happy, sad,
    angry, pointing, nervous, surprised, waiting, write_effect,
    wait_out, space_between, between_tag, check_key
)

def ask_connect():
    """
    Asks the user whether they want to use the Tor network for anonymity.

    Returns:
        requests or requests.Session: A requests session, optionally configured with Tor proxy.
    """

    sel = str(input(f"\n{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
    if check_key(sel):
        from core.socks_connect import get_tor_connection
        ses = get_tor_connection()
        return ses
    else: return requests



def make_search(connection, nickname, list):
    """
    Perform HTTP requests on a list of URLs using the specified nickname to determine if user exists.

    Parameters:
        connection (requests or Session): HTTP client to use.
        nickname (str): The username to search for.
        list (list): List of (site_name, url) tuples.
    """

    equals = True
    number = 0
    global file
    file = f"data/users/users_{nickname}_results.txt"

    for title, url in list:
        try:
            select_agent = agents()
            web = connection.get(url=url, headers=select_agent, timeout=20)
        except requests.exceptions.Timeout:
            write_effect(f'\n{display_error} Timeout exceeded with the site: {maRed(title)}', 0.02)
            space_between()
        except requests.exceptions.ConnectionError:
            write_effect(f"\n{display_error} Can't connect with the site: {maRed(title)}", 0.02)
            space_between()
        except requests.exceptions.RequestException as err:
            write_effect(f"\n{display_error} Another has ocurred with the site: {maRed(title)}, {maRed(err)}", 0.02)
            space_between()

        if web.status_code == 200:
            if equals:
                write_effect(f'\n{display_validate} {maGreen("Confirmed users...")} {maGreen(surprised)}\n', 0.03)
                save_data(file, f'\nConfirmed users of: {nickname}\n', None, 'a', None)
                equals = False

            write_effect(f'{display_extra} {maBold("Site")}: {maBold(title)}', 0.0005)
            write_effect(f'{display_info} {maCyan("URL")}: {maUnderline(url)}', 0.0005)

            if nickname in web.text:
                nick_green = f"User '{nickname}' found in the website."
                write_effect(f'{display_validate} {maGreen(nick_green)}', 0.005)
                user_save = f'{title}: {url}'
                save_data(file, None, user_save, 'a', None)
                number += 1

            else:
                nick_yellow = f"User {nickname} no exists or is a ××False Positive××"
                write_effect(f'{display_question} {maYellow(nick_yellow)}', 0.005)

            space_between()

    total_results = len(list)
    write_effect(f"\n{display_info} User '{maBold(nickname)}' found on {maGreen(number)} websites of {maCyan(total_results)} {maGreen(happy)}", 0.03)
    save_data(file, None, None, "a", True)



def execute_user():
    """
    Entry point function to execute the user search process.
    Handles input of nickname, selection of TOR, regular and NSFW site search,
    and optional deep analysis using Google Dorking.
    """

    print(f"{display_info} Enter a user like: john_doe\n{display_info} Don't use spaces in the username!")

    nickname = input(f'\n×××{maRed("[")}{maBold("SPY-USERNAME")}{maRed("]")}---> ').strip()
    if not nickname: raise Exception(f"{display_error} You can't leave the username empty! {maRed(angry)}")
    if " " in nickname: raise Exception(f"{display_error} Error, the nickname can't have spaces! example: john_doe")

    type = ask_connect()

    wait_out(0.3)
    write_effect(f'\n{maYellow("Searching user:")} {maYellow(nickname)}{maYellow("...")}', 0.05)

    websites = [ # You can make your custom list if you want like: tech websites.
        ('YouTube', f'https://m.youtube.com/@{nickname}'),
        ('Instagram', f'https://www.instagram.com/{nickname}'),
        ('Facebook', f'https://www.facebook.com/{nickname}'),
        ('Reddit', f'https://www.reddit.com/user/{nickname}'),
        ('Snapchat', f'https://www.snapchat.com/add/{nickname}'),
        ('TikTok', f'https://www.tiktok.com/@{nickname}'),
        ('Bluesky', f'https://bsky.app/profile/{nickname}'),
        ('Fiverr', f'https://www.fiverr.com/{nickname}'),
        ('Discord', f'https://discord.com/users/{nickname}'),
        ('Spotify', f'https://open.spotify.com/user/{nickname}'),
        ('SoundCloud', f'https://m.soundcloud.com/{nickname}'),
        ('Twitch', f'https://m.twitch.tv/{nickname}/home'),
        ('Roblox', f'https://www.roblox.com/user.aspx?username={nickname}'),
        ('Xbox Gamertag', f'https://xboxgamertag.com/search/{nickname}'),
        ('Xbox Profile', f'https://account.xbox.com/en-US/Profile?gamertag={nickname}'),
        ('PlayStation', f'https://my.playstation.com/profile/{nickname}'),
        ('Minecraft', f'https://minecraftuuid.com/?search={nickname}'),
        ('Lichess', f'https://lichess.org/@/{nickname}'),
        ('Chess.com', f'https://www.chess.com/member/{nickname}'),
        ('Osu!', f'https://osu.ppy.sh/users/{nickname}'),
        ('Fortnite', f'https://fortnitetracker.com/profile/all/{nickname}'),
        ('Steam', f'https://steamcommunity.com/id/{nickname}'),
        ('Twitter', f'https://x.com/{nickname}'),
        ('Pinterest', f'https://pin.it/{nickname}'),
        ('LinkedIn', f'https://www.linkedin.com/in/{nickname}'),
        ('Trello', f'https://trello.com/{nickname}'),
        ('Tumblr', f'https://www.tumblr.com/{nickname}'),
        ('Flickr', f'https://www.flickr.com/people/{nickname}'),
        ('Blogger', f'https://www.blogger.com/profile/{nickname}'),
        ('Dribbble', f'https://dribbble.com/{nickname}'),
        ('Medium', f'https://medium.com/@{nickname}'),
        ('Bitbucket', f'https://bitbucket.org/{nickname}'),
        ('Behance', f'https://www.behance.net/{nickname}'),
        ('Venmo', f'https://venmo.com/{nickname}'),
        ('Tagged', f'https://secure.tagged.com/profile/{nickname}'),
        ('Badoo', f'https://badoo.com/en/profile/{nickname}'),
        ('GitHub', f'https://github.com/{nickname}'),
        ('GitLab', f'https://gitlab.com/{nickname}'),
        ('HackerNews', f'https://news.ycombinator.com/user?id={nickname}'),
        ('Dailymotion', f'https://www.dailymotion.com/{nickname}'),
        ('Bilibili', f'https://www.bilibili.tv/en/space/{nickname}'),
        ('Mastodon', f'https://mastodon.social/@{nickname}'),
        ('Goodreads', f'https://www.goodreads.com/user/show/{nickname}'),
        ('Wattpad', f'https://www.wattpad.com/user/{nickname}'),
        ('Weibo', f'https://m.weibo.cn/u/{nickname}'),
        ('QQ Music', f'https://i.y.qq.com/n2/m/share/profile_v2/{nickname}'),
        ('Quora', f'https://www.quora.com/profile/{nickname}'),
        ('Academia', f'https://independent.academia.edu/{nickname}'),
        ('About.me', f'https://about.me/{nickname}'),
        ('Strava', f'https://www.strava.com/athletes/{nickname}'),
        ('Brainly', f'https://brainly.com/app/profile/{nickname}'),
        ('Crunchyroll', f'https://www.crunchyroll.com/es/news/author/{nickname}'),
        ('DeviantArt', f'https://www.deviantart.com/{nickname}'),
        ('Duolingo', f'https://www.duolingo.com/profile/{nickname}'),
        ('PayPal', f'https://www.paypal.me/{nickname}'),
        ('CashApp', f'https://cash.app/${nickname}'),
        ('Ko-Fi', f'https://ko-fi.com/{nickname}'),
        ('Patreon', f'https://www.patreon.com/{nickname}'),
        ('Peach', f'https://peach.cool/@{nickname}'),
        ('Ravelry', f'https://www.ravelry.com/people/{nickname}'),
        ('Bandcamp', f'https://bandcamp.com/{nickname}'),
        ('Mixcloud', f'https://www.mixcloud.com/{nickname}'),
        ('8Tracks', f'https://8tracks.com/{nickname}'),
        ('ReverbNation', f'https://www.reverbnation.com/{nickname}'),
        ('Newgrounds', f'https://{nickname}.newgrounds.com'),
        ('Kongregate', f'https://www.kongregate.com/accounts/{nickname}'),
        ('MeetMe', f'https://www.meetme.com/member/{nickname}'),
        ('MySpace', f'https://myspace.com/{nickname}'),
        ('Gab', f'https://gab.com/{nickname}'),
        ('Minds', f'https://www.minds.com/{nickname}'),
        ('MeWe', f'https://mewe.com/i/{nickname}'),
        ('Grindr', f'https://www.grindr.com/{nickname}'),
        ('Depop', f'https://www.depop.com/{nickname}'),
        ('Poshmark', f'https://poshmark.com/closet/{nickname}'),
        ('Vinted', f'https://www.vinted.com/member/{nickname}'),
        ('Grailed', f'https://www.grailed.com/{nickname}'),
        ('Letterboxd', f'https://letterboxd.com/{nickname}'),
        ('Couchsurfing', f'https://www.couchsurfing.com/people/{nickname}'),
        ('Classmates.com', f'https://www.classmates.com/profile/{nickname}'),
        ('XING', f'https://www.xing.com/profile/{nickname}'),
        ('BlackPlanet', f'https://www.blackplanet.com/{nickname}'),
        ('Gaia Online', f'https://www.gaiaonline.com/profiles/{nickname}'),
        ('Tagged', f'https://www.tagged.com/profile/{nickname}'),
        ('Meetup', f'https://www.meetup.com/members/{nickname}'),
        ('MyHeritage', f'https://www.myheritage.com/member-{nickname}'),
        ('CafeMom', f'https://www.cafemom.com/profile/{nickname}'),
        ('Nextdoor', f'https://nextdoor.com/profile/{nickname}'),
        ('ResearchGate', f'https://www.researchgate.net/profile/{nickname}'),
        ('LiveJournal', f'https://www.livejournal.com/userinfo.bml?user={nickname}'),
        ('Xanga', f'https://www.xanga.com/{nickname}'),
        ('Weebly', f'https://www.weebly.com/{nickname}'),
        ('Wix', f'https://www.wix.com/{nickname}'),
        ('Geocities', f'https://www.geocities.ws/{nickname}'),
        ('Fotolog', f'https://www.fotolog.com/{nickname}'),
        ('Buzznet', f'https://www.buzznet.com/{nickname}'),
        ('CaringBridge', f'https://www.caringbridge.org/visit/{nickname}'),
        ('EyeEm', f'https://www.eyeem.com/u/{nickname}'),
        ('Fotki', f'https://public.fotki.com/{nickname}'),
        ('Fotolog', f'https://www.fotolog.com/{nickname}'),
        ('Foursquare', f'https://foursquare.com/user/{nickname}'),
        ('Habbo', f'https://www.habbo.com/profile/{nickname}'),
        ('Hi5', f'https://www.hi5.com/{nickname}'),
        ('Kiwibox', f'https://www.kiwibox.com/{nickname}'),
        ('Last.fm', f'https://www.last.fm/user/{nickname}'),
        ('LiveJournal', f'https://www.livejournal.com/userinfo.bml?user={nickname}'),
        ('Mixi', f'https://mixi.jp/show_friend.pl?id={nickname}'),
        ('Mocospace', f'https://www.mocospace.com/{nickname}'),
        ('MyAnimeList', f'https://myanimelist.net/profile/{nickname}'),
        ('MyHeritage', f'https://www.myheritage.com/member-{nickname}'),
        ('PatientsLikeMe', f'https://www.patientslikeme.com/members/{nickname}'),
        ('Periscope', f'https://www.pscp.tv/{nickname}'),
        ('Plurk', f'https://www.plurk.com/{nickname}'),
        ('Renren', f'https://www.renren.com/{nickname}'),
        ('ResearchGate', f'https://www.researchgate.net/profile/{nickname}'),
        ('Skyrock', f'https://www.skyrock.com/members/{nickname}'),
        ('SoundClick', f'https://www.soundclick.com/{nickname}'),
        ('Stage 32', f'https://www.stage32.com/profile/{nickname}'),
        ('StumbleUpon', f'https://www.stumbleupon.com/stumbler/{nickname}'),
        ('Taringa!', f'https://www.taringa.net/{nickname}'),
        ('The Dots', f'https://the-dots.com/users/{nickname}'),
        ('TripAdvisor', f'https://www.tripadvisor.com/members/{nickname}'),
        ('Untappd', f'https://untappd.com/user/{nickname}'),
        ('Vero', f'https://www.vero.co/{nickname}'),
        ('Viadeo', f'https://www.viadeo.com/p/{nickname}', ),
        ('Vine', f'https://vine.co/{nickname}'),
        ('VK', f'https://vk.com/{nickname}'),
    ]

    nsfw_websites = [
        ('OnlyFans', f'https://onlyfans.com/{nickname}'),
        ('Pornhub', f'https://www.pornhub.com/users/{nickname}'),
        ('XNXX', f'https://www.xnxx.com/profiles/{nickname}'),
        ('RedTube', f'https://www.redtube.com/users/{nickname}'),
        ('YouPorn', f'https://www.youporn.com/user/{nickname}'),
        ('CamSoda', f'https://www.camsoda.com/{nickname}'),
        ('Chaturbate', f'https://chaturbate.com/{nickname}'),
        ('MyFreeCams', f'https://profiles.myfreecams.com/{nickname}', ),
        ('LiveJasmin', f'https://www.livejasmin.com/en/user/{nickname}'),
        ('FetLife', f'https://fetlife.com/users/{nickname}'),
        ('ManyVids', f'https://www.manyvids.com/Profile/{nickname}'),
        ('NaughtyAmerica', f'https://www.naughtyamerica.com/pornstar/{nickname}'),
        ('BangBros', f'https://bangbros.com/model/{nickname}'),
        ('Mofos', f'https://www.mofos.com/model/{nickname}'),
        ('DigitalPlayground', f'https://www.digitalplayground.com/model/{nickname}'),
        ('Kink', f'https://www.kink.com/model/{nickname}'),
        ('MetArt', f'https://www.metart.com/model/{nickname}'),
        ('Twistys', f'https://www.twistys.com/model/{nickname}'),
        ('SuicideGirls', f'https://www.suicidegirls.com/girls/{nickname}'),
        ('Eros', f'https://www.eros.com/{nickname}'),
        ('Rule34', f'https://rule34.xxx/index.php?page=account&s=profile&uname={nickname}'),
        ('Furaffinity', f'https://www.furaffinity.net/user/{nickname}'),
        ('e621', f'https://e621.net/users/{nickname}')
    ]

    make_search(type, nickname, websites)
    adult_search = str(input(f"\n{display_question} Do you want to search user {maBold(nickname)} in {maMagenta('NSFW')} websites? ({maGreen('y')}/{maRed('n')}): "))
    if check_key(adult_search): make_search(type, nickname, nsfw_websites)

    ask_input = str(input(f"\n{display_question} Do you want to make a search the user {maBold(nickname)} using Google Dorks? ({maGreen('y')}/{maRed('n')}): "))

    if check_key(ask_input):
        sel = str(input(f"{display_question} Do you want to use a Tor network for this module? ({maGreen('y')}/{maRed('n')}): ")).strip()
        tor = check_key(sel)
        if tor: gg_connection(True)

        wait_out(0.5)

        ls_search_user = [
           (f'descr="{nickname}"', 10, 3),
           (f'descr="{nickname}"&docs', 10, 3),
           (f'descr="{nickname}"&email', 10, 3),
           (f'descr="{nickname}"&phone', 10, 3),
           (f'descr="{nickname}"&adr', 10, 3),
           (f'descr="{nickname}"&dbase', 10, 3)
        ]

        multi_search(1, ls_search_user, file, tor)
