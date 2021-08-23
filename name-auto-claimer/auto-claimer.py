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


def main(username: str, delay: int, proxies_file: str, credentials: str, bearer: str, no_availability_check: bool):
    has_errors: bool = False
    proxies: list[str] = list()

    if not credentials is None and not bearer is None:
        message(
            f'{Fore.LIGHTRED_EX}You cannot use both a bearer token and credentials.')
        has_errors = True
    elif credentials is None and bearer is None:
        message(
            f'{Fore.LIGHTRED_EX}You must specify either a bearer token or credentials.')
        has_errors = True

    if not credentials is None:
        account = credentials.split(':')
        if len(account) != 2:
            message(
                f'{Fore.LIGHTRED_EX}Accounts must be in the following format: "username:password".')
            has_errors = True
        else:
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
        if not no_availability_check:
            for proxy in proxies:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")

                if is_available(username, proxy):
                    message(
                        f'{Fore.LIGHTGREEN_EX}{username}{Fore.RESET} is available! ({current_time})')

                    print()

                    if bearer is None:
                        bearer = authenticate(email, password)
                        result: bool = change_name(username, bearer)
                    else:
                        result: bool = create_profile(username, bearer)

                    if result:
                        message(f'{Fore.LIGHTGREEN_EX}Changed name!')
                    else:
                        message(
                            f'{Fore.LIGHTRED_EX}Was not able to change name.')
                        print()

                    post_webhook(username)

                    return

                else:
                    message(
                        f'{Fore.LIGHTRED_EX}{username}{Fore.RESET} is not available. ({current_time})')

                time.sleep(delay)
        else:
            if bearer is None:
                current_time = int(time.time())

                # after 20 hours we reset the bearer
                end_time = current_time + (60 * 60 * 20)

                bearer = authenticate(email, password)
                while (int(time.time()) < end_time):
                    result: bool = change_name(username, bearer)

                    if result:
                        message(f'{Fore.LIGHTGREEN_EX}Changed name!')
                        post_webhook(username)

                        return

                    time.sleep(delay)

            else:
                while True:
                    result: bool = create_profile(username, bearer)

                    if result:
                        message(f'{Fore.LIGHTGREEN_EX}Changed name!')
                        post_webhook(username)

                        return

                    time.sleep(delay)


def message(message: str):
    print(f'{Fore.RESET}{message}{Fore.RESET}')


def is_available(username: str, proxy: str) -> bool:
    endpoint = 'https://api.mojang.com/users/profiles/minecraft/'

    proxy_dictionary = {
        'http': proxy,
    }

    try:
        response = requests.get(
            f'{endpoint}{username}', proxies=proxy_dictionary)

        status_code = response.status_code

        if status_code != 200:
            return True
        return False

    except Exception:
        message(f'{Fore.LIGHTRED_EX}Exception given, retrying...')

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


def create_profile(username: str, bearer: str) -> bool:
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': f'Bearer {bearer}'}

    json = {'profileName': f'{username}'}

    response = requests.post(
        f'https://api.minecraftservices.com/minecraft/profile/', headers=headers, json=json)

    print(response.text)
    print()
    if response.status_code == 200:
        return True

    return False


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
        'content': '<@537321481940500480> <@229030852607213569>',
        'embeds': [
            {
                'title': f'{username} has dropped!',
                'color': 0XFFD728,
                'description': '\nName has dropped!',
            }
        ]
    }

    for _ in range(10):
        requests.post(WEBHOOK, json=webhook_design)
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Repeatedly attempt to claim a Minecraft username that is predicted to be dropping')
    parser.add_argument('username', type=str,
                        help='the username to attempt to auto-claim')
    parser.add_argument('delay', type=int,
                        help='the delay between each request')
    parser.add_argument('proxies', type=str,
                        help='the proxies file')
    parser.add_argument('--credentials', '-c', type=str,
                        help='the username:password combo')
    parser.add_argument('--bearer', '-b', type=str,
                        help='the bearer token')
    parser.add_argument('--no-availability-check', '-n', action='store_true',
                        help='stop checking for name availability and just send namechange requests')

    args = parser.parse_args()

    username: str = args.username
    delay: int = args.delay
    proxies_file: str = args.proxies
    credentials: str = args.credentials
    bearer: str = args.bearer
    no_availability_check: bool = args.no_availability_check

    main(username, delay, proxies_file,
         credentials, bearer, no_availability_check)
