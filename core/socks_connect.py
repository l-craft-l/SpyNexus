import requests
from core.display import display_error, display_question, maRed

def get_tor_connection():
    session = requests.session()
    session.proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }
    try:
        test = session.get(url="https://check.torproject.org/", timeout=20)
    except requests.exceptions.ConnectionError:
        raise Exception(f"{display_error} Error, can't connect to the website... Are you connected to the Tor network?")
    except requests.exceptions.RequestException as err:
        raise Exception(f"{display_error} Error in the Tor network, {maRed(err)}")
    return session
