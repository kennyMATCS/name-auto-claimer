import argparse

from colorama import Fore, init
init()


def main(username: str, delay: int, proxies_file: str):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Repeatedly attempt to claim a Minecraft username that is predicted to be dropping')
    parser.add_argument('username', type=str,
                        help='the username to attempt to auto-claim')
    parser.add_argument('delay', type=str,
                        help='the password file')
    parser.add_argument('--proxies', type=str,
                        help='the proxies file')
    args = parser.parse_args()

    username: str = args.username
    delay: int = args.delay
    proxies_file: str = args.proxies

    main(username, delay, proxies_file)
