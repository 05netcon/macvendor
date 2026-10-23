from __future__ import annotations
import os
import sys
import logging
import requests


OUI_URL = 'http://standards-oui.ieee.org/oui.txt'
LOCATIONS = [
    os.path.expanduser('~/.cache/mac-vendors.txt'),
    f'{sys.prefix}/cache/mac-vendors.txt',
    f'{os.path.dirname(__file__)}/../../cache/mac-vendors.txt',
    f'{os.path.dirname(__file__)}/../../../cache/mac-vendors.txt',
]
DELIMITERS = (':', '-', '.')

prefixes: dict[str: str] = None


class InvalidMacError(Exception):
    pass


class VendorNotFoundError(KeyError):
    def __init__(self, mac: str) -> None:
        self.mac = mac

    def __str__(self) -> str:
        return f'Имя вендора для мак адреса {self.mac} не обнаружено'


def format_value(value: str) -> str:
    mac: str = value.upper()
    for delimiter in DELIMITERS:
        mac = mac.replace(delimiter, '')
    try:
        int(mac, 16)
    except ValueError:
        raise InvalidMacError(f'{mac} содержит недопустимые символы')
    if len(mac) > 12:
        raise InvalidMacError(f'{mac} не верный мак адрес')
    return mac


def find_vendors_list() -> str:
    for location in LOCATIONS:
        if os.path.exists(location):
            return location


def update_vendors(url: str = OUI_URL) -> None:
    logging.log(logging.DEBUG, 'Скачиваем список мак адресов вендоров')
    with requests.Session() as session:
        with session.get(url) as response:
            with open(LOCATIONS[0], mode='wb') as f:
                global prefixes
                prefixes = {}
                while True:
                    line = response.content.readline()
                    if not line:
                        break
                    if b'(base 16)' in line:
                        prefix, vendor = (
                            i.strip() for i in line.split(b'(base 16)', 1)
                        )
                        prefixes[prefix] = vendor
                        f.write(prefix + b':' + vendor + b'\n')


def load_vendors():
    global prefixes
    prefixes = {}
    vendors_location: str = find_vendors_list()
    if vendors_location:
        logging.log(
            logging.DEBUG,
            f'Загружаем список вендоров из {vendors_location}'
        )
        with open(vendors_location, mode='rb') as f:
            for line in (f.read()).splitlines():
                prefix, vendor = line.split(b':', 1)
                prefixes[prefix] = vendor
    else:
        try:
            os.makedirs('/'.join(LOCATIONS[0].split('/')[:-1]))
        except OSError:
            pass
        update_vendors()
    logging.log(
        logging.DEBUG,
        f'Список вендоров успешно загружен: {len(prefixes)} записей'
    )


def lookup(mac: str) -> str:
    mac = format_value(mac)
    if not prefixes:
        load_vendors()
    if type(mac) is str:
        mac = mac.encode('utf8')
    try:
        return prefixes[mac[:6]].decode('utf8')
    except KeyError:
        raise VendorNotFoundError(mac.decode('utf8'))


def main() -> None:
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} [MAC-Address]')
        sys.exit()
    else:
        mac: str = sys.argv[1]
        try:
            vendor: str = lookup(mac)
        except Exception:
            vendor: str = 'Неизвестный вендор'
        print(f'Мак адрес: \t{mac}')
        print(f'Имя вендора: {vendor}')


if __name__ == '__main__':
    main()
