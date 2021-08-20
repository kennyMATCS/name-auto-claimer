import argparse
import requests
import time
import configparser

from datetime import datetime
from os.path import exists
from utils import get_proxy

from colorama import Fore, init
init()

config = configparser.ConfigParser()
config.read('config.ini')

WEBHOOK = config['discord']['webhook']
DELAY = int(config['delay']['interval'])


def main(username: str, proxies_file: str, credentials: str, bearer: str):
    has_errors: bool = False
    proxies: list[str] = list()

    if not credentials is None and not bearer is None:
        message(
            f'{Fore.LIGHTRED_EX}You cannot use both a bearer token and credentials.')
        has_errors = True
    elif credentials is None and bearer is None:
        message(
            f'{Fore.LIGHTRED_EX}You must specify either a bearer toekn or credentials.')
        has_errors = True

    if not credentials is None:
        account = credentials.split(':')
        email = account[0]
        password = account[1]

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

    if has_errors:
        return

    while True:
        for proxy in proxies:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            if is_available(username, proxy):
                message(
                    f'{Fore.LIGHTGREEN_EX}{username}{Fore.RESET} is available! ({current_time})')

                post_webhook(username)
                print()

                if bearer is None:
                    bearer = authenticate(email, password)

                result: bool = change_name(username, bearer)

                if result:
                    message(f'{Fore.LIGHTGREEN_EX}Changed name!')
                else:
                    message(f'{Fore.LIGHTRED_EX}Was not able to change name.')
                    print()

                return

            else:
                message(
                    f'{Fore.LIGHTRED_EX}{username}{Fore.RESET} is not available. ({current_time})')

            time.sleep(DELAY)


def message(message: str):
    print(f'{Fore.RESET}{message}{Fore.RESET}')


def is_available(username: str, proxy: str) -> bool:
    endpoint = 'https://api.mojang.com/users/profiles/minecraft/'

    proxy_dictionary = {
        'http': proxy,
    }

    response = requests.get(
        f'{endpoint}{username}', proxies=proxy_dictionary)

    status_code = response.status_code

    if status_code != 200:
        return True
    return False


def authenticate(email: str, password: str) -> str:
    authenticate_json = {'agent': {'name': 'Minecraft',
                                   'version': 1}, 'username': email, 'password': password}

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post('https://authserver.mojang.com/authenticate',
                             json=authenticate_json, headers=headers)

    print(response.text)
    print()
    if response.status_code == 200:
        json = response.json()
        bearer = json['accessToken']
        return bearer

    return 'none'


def change_name(username: str, bearer: str) -> bool:
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {bearer}'}

    response = requests.put(
        f'https://api.minecraftservices.com/minecraft/profile/name/{username}', headers=headers)

    print(response.text)
    print()
    if response.status_code == 200:
        return True

    return False


def post_webhook(username: str):
    webhook_design = {
        'embeds': [
            {
                'title': f'{username} has dropped!',
                'color': 0XFFD728,
                'description': f'<@537321481940500480> \nName has dropped!',
            }
        ]
    }
    requests.post(WEBHOOK, json=webhook_design)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Repeatedly attempt to claim a Minecraft username that is predicted to be dropping')
    parser.add_argument('username', type=str,
                        help='the username to attempt to auto-claim')
    parser.add_argument('proxies', type=str,
                        help='the proxies file')
    parser.add_argument('--credentials', type=str,
                        help='the username:password combo')
    parser.add_argument('--bearer' type=str,
                        help='the bearer token')
    args = parser.parse_args()

    username: str = args.username
    proxies_file: str = args.proxies
    credentials: str = args.credentials
    bearer: str = args.credentials

    main(username, proxies_file, credentials, bearer)
