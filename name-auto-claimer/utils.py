def get_proxy(proxy: str) -> str:
    http = 'http://'

    def has_three_zeroes(p: str):
        total = 0
        for c in p:
            if c == '.':
                total = total + 1
        if total == 3:
            return True
        return False

    def is_port(p: str):
        if p.isnumeric():
            number = int(p)
            if not number > 65535 and not number < 0:
                return True
        return False

    split = proxy.split(':')

    if len(split) == 1:
        if not has_three_zeroes(split[0]):
            return 'bad_proxy'

        return http + split[0]

    if len(split) == 2:
        if not has_three_zeroes(split[0]):
            return 'bad_proxy'

        if is_port(split[1]):
            return http + split[0] + ':' + split[1]
        return 'bad_proxy'

    if len(split) == 3:
        return http + split[1] + ':' + split[2] + '@' + split[0]

    if len(split) == 4:
        print('hey')
        if is_port(split[1]):
            return http + split[2] + ':' + split[3] + '@' + split[0] + ':' + split[1]
        return 'bad_proxy'

    return 'bad_proxy'
