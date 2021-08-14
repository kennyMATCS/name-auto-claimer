import argparse
import requests
import time

from os.path import exists
from utils import get_proxy

from colorama import Fore, init
init()


def main(username: str, delay: int, proxies_file: str):
    has_errors: bool = False
    proxies: list[str] = list()

    if not exists(proxies_file):
        message(
            f'{Fore.LIGHTRED_EX}Could not find the proxies file called {proxies_file}.')
        has_errors = True
    else:
        with open(proxies_file) as file:
            read_lines = file.readlines()
            for i in range(0, len(read_lines)):
                l = read_lines[i]
                line = l.strip()

                proxy: str = get_proxy(line)
                if proxy == 'bad_proxy':
                    message(
                        f'{Fore.LIGHTRED_EX}{line} ({i + 1}) is not in a valid proxy format.')
                else:
                    proxies.append(proxy)

    for proxy in proxies:
        if is_available(username, proxy):
            message('{Fore.LIGHTCYAN_EX}{username} is available!')
        else:
            message('{Fore.LIGHTRED_EX}{username}{Fore.RESET}is not available!')

        time.sleep(delay)

    if has_errors:
        return


def message(message: str):
    print(f'{Fore.RESET}{message}')


def is_available(username: str, proxy: str) -> bool:
    endpoint = 'https://api.gapple.pw/status/'

    proxy_dictionary = {
        'http': proxy,
        'https': proxy.replace('http', 'https')
    }

    response = requests.get(f'{endpoint}{username}', proxies=proxy_dictionary)
    status_code = response.status_code

    if status_code == 200:
        return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Repeatedly attempt to claim a Minecraft username that is predicted to be dropping')
    parser.add_argument('username', type=str,
                        help='the username to attempt to auto-claim')
    parser.add_argument('delay', type=int,
                        help='interval between each request')
    parser.add_argument('proxies', type=str,
                        help='the proxies file')
    args = parser.parse_args()

    username: str = args.username
    delay: int = args.delay
    proxies_file: str = args.proxies

    main(username, delay, proxies_file)
