import asyncio
import json
import os
import tkinter
from tkinter import filedialog
import time
from typing import NoReturn
import ctypes

from colorama import Fore, Back, Style
import requests
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from pandas import Timestamp

from codeparts import checkers, PCSS
from codeparts.data import Constants

check = checkers.checkers()


class system():
    def __init__(self) -> None:
        self.num = 0
        self.proxylist = []
        self.proxy = set()

        path = os.getcwd()
        self.parentpath = os.path.abspath(os.path.join(path, os.pardir))

    @staticmethod
    def get_region(token: str, entt: str, proxy: dict):
        session = requests.Session()
        try:
            headers = {
                'X-Riot-Entitlements-JWT': entt,
                'Authorization': 'Bearer {}'.format(token)
            }
            response = session.put(
                Constants.REGION_URL, headers=headers, proxies=proxy)

            response = response.json()
            reg = 'N/A'
            lvl = ''
            #input(response)

            return reg, lvl
        except Exception as e:
            return 'N/A', 'N/A'

    @staticmethod
    def get_region2(account, proxy: dict) -> None:
        # reg + country
        session = requests.Session()
        headers = {"User-Agent": f"RiotClient/{Constants.RIOTCLIENT} %s (Windows;10;;Professional, x64)",
                   "Pragma": "no-cache",
                   "Accept": "*/*",
                   "Content-Type": "application/json",
                   "Authorization": f"Bearer {account.token}"}
        userinfo = session.post(
            Constants.USERINFO_URL, headers=headers).json()
        try:
            try:
                region = userinfo['region']['id']
                fixedregion = Constants.LOL2REG[region]
                country = userinfo['country'].upper()
            except:
                country = userinfo['country'].upper()
                cou3 = Constants.A2TOA3[country]
                fixedregion = Constants.COU2REG[cou3]
            fixedregion = fixedregion.lower()
            progregion = fixedregion
            if fixedregion == 'latam' or fixedregion == 'br':
                progregion = 'na'
        except Exception as e:
            # input(e)
            fixedregion = 'N/A'

        # lvl
        try:
            headers = {
                'X-Riot-Entitlements-JWT': account.entt,
                'Authorization': 'Bearer {}'.format(account.token)
            }
            response = session.get(f"https://pd.{progregion}.a.pvp.net/account-xp/v1/players/{account.puuid}", headers=headers)
            lvl = response.json()['Progress']['Level']
            #input(lvl)
        except Exception as e:
            lvl = 'N/A'

        account.region = fixedregion
        account.country = country
        account.lvl = lvl

    @staticmethod
    def load_settings():
        try:
            f = open('system\\settings.json')
            data = json.load(f)
            f.close()
            return data
        except:
            print("can't find settings.json\nplease download it from my github\n")
            return False

    @staticmethod
    def edit_settings():
        while True:
            os.system('cls')
            f = open('system\\settings.json', 'r+')
            data = json.load(f)
            deffile = data['default_file']
            max_rlimits = data['max_rlimits']
            rlimit_wait = data['rlimit_wait']
            cooldown = data['cooldown']
            webhook = data['webhook']
            print_sys = data['print_sys']
            create_folder = data['new_folder']
            proxyscraper = data['proxyscraper']
            menu_choices = [
                Separator(),
                f'Default File: {deffile}',
                f'RLimits to skip an acc: {max_rlimits}',
                f'Wait if there is a RLimit (seconds): {rlimit_wait}',
                f'Wait between checking accounts (seconds): {cooldown}',
                f'Create folder for every check: {create_folder}',
                f'Discord Webhook: {webhook}',
                f'Print system info: {print_sys}',
                'Discord Webhook Settings',
                f'Proxy Scraper URL: {proxyscraper}',
                Separator(),
                'Exit'
            ]
            edit = inquirer.select(
                message="Please select an option you want to edit:",
                choices=menu_choices,
                default=menu_choices[0],
                pointer='>'
            ).execute()
            if edit == menu_choices[1]:
                root = tkinter.Tk()
                file = filedialog.askopenfile(parent=root, mode='rb', title='select file with accounts (login:password)',
                                              filetype=(("txt", "*.txt"), ("All files", "*.txt")))
                root.destroy()
                if file == None:
                    filename = 'None'
                else:
                    filename = str(file).split("name='")[1].split("'>")[0]
                data['default_file'] = filename
            elif edit == menu_choices[2]:
                new_rlimits = input(
                    'enter the number of riot limits to skip this account (min 1) >>>')
                if int(new_rlimits) < 1 or int(new_rlimits) > 999:
                    return
                try:
                    data['max_rlimits'] = int(new_rlimits)
                except:
                    print('u have to type a num from 1 to 999 (3 recommended)')
                    return
            elif edit == menu_choices[3]:
                new_maxrlimits = input(
                    'enter the number of seconds to wait if there is a riot limit (min 1) >>>')
                if int(new_maxrlimits) < 1 or int(new_maxrlimits) > 99999:
                    return
                try:
                    data['rlimit_wait'] = int(new_maxrlimits)
                except:
                    print('u have to type a num from 1 to 99999 (30 recommended)')
                    return
            elif edit == menu_choices[4]:
                new_cd = input(
                    'enter the number of seconds to wait between checking accounts (min 0) >>>')
                if int(new_cd) < 0 or int(new_cd) > 99999:
                    return
                data['cooldown'] = int(new_cd)
            elif edit == menu_choices[5]:
                createfolder = [
                    Separator(),
                    'Yes',
                    'No'
                ]
                newfolder = inquirer.select(
                    message='do you want to create a new folder every time u start the checker?',
                    choices=createfolder,
                    default=createfolder[0],
                    pointer='>'
                ).execute().replace('Yes', 'True').replace('No', 'False')
                data['new_folder'] = newfolder
            elif edit == menu_choices[6]:
                newwebhook = input(
                    'ented the discotd webhook to use (leave it empty if u dont wanna use it): ')
                data['webhook'] = newwebhook
            elif edit == menu_choices[7]:
                printinfo = [
                    Separator(),
                    'Yes',
                    'No'
                ]
                newinfo = inquirer.select(
                    message='print system info (e.g. riot limits)?',
                    choices=printinfo,
                    default=printinfo[0],
                    pointer='>'
                ).execute().replace('Yes', 'True').replace('No', 'False')
                data['print_sys'] = newinfo
            elif edit == menu_choices[8]:
                dwsttngs = [
                    inquirer.checkbox(
                        "What to send in discord webhook?",
                        choices=["tempbanned accounts", "accounts without skins", "accounts with only wayfinder shorty",
                                 "stats (once per 5 minutes)", "accounts with unknown region"],
                        long_instruction="space to pick. enter to finish",
                        disabled_symbol='[X]',
                        enabled_symbol=f"[Y]",
                        pointer='>'
                    ).execute()
                ]
                data['dw_settings'] = dwsttngs
            elif edit == menu_choices[9]:
                default_scraperurl = 'https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all'
                newscraperurl = ''
                newscraperurl = input(
                    'Enter URL From Which (HTTP) Proxies Will Be Scraped, Leave Empty To Use ProxySrape: ')

                if len(newscraperurl) == 0:
                    newscraperurl = default_scraperurl
                data['proxyscraper'] = newscraperurl
            else:
                return
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            f.close()

    def load_proxy(self):
        with open(f"{self.parentpath}\\proxy.txt", "r") as f:
            file_lines1 = f.readlines()
            if len(file_lines1) == 0:
                return
            for line1 in file_lines1:
                self.proxy.add(line1.strip())

        for i in list(self.proxy):
            if '.' in i:
                self.proxylist.append({
                    'http': f'http://{i}',
                    'https':f'http://{i}'
                })

        return self.proxylist

    def getproxy(self, proxlist):
        try:
            if proxlist == None:
                return None
            elif len(proxlist) == 0:
                return None
            if self.num > len(proxlist)-1:
                self.num = 0
            nextproxy = proxlist[self.num]
            self.num += 1
        except Exception as e:
            # input(e)
            nextproxy = None
        return nextproxy

    @staticmethod
    def center(var: str, space: int = None):  # From Pycenter
        if not space:
            space = (os.get_terminal_size().columns -
                     len(var.splitlines()[int(len(var.splitlines())/2)])) / 2
        return "\n".join((' ' * int(space)) + var for var in var.splitlines())

    @staticmethod
    def get_spaces_to_center(var: str, space: int = None):
        if not space:
            space = (os.get_terminal_size().columns -
                     len(var.splitlines()[int(len(var.splitlines())/2)])) / 2
        return ' '*int(space)

    @staticmethod
    def getmillis():
        return round(time.time() * 1000)

    def checkproxy(self):
        try:
            with open(f"{self.parentpath}\\proxy.txt", "r") as f:
                proxylist = f.readlines()
        except FileNotFoundError:
            input('cant find your proxy file. press enter to return')
            return

        proxychecker = PCSS.ProxyChecker()
        proxychecker.main(proxylist)
        good = asyncio.run(proxychecker.check_proxies())

        if inquirer.confirm(
            message="Do you want to delete the bad ones?", default=True
        ).execute():
            with open(f"{self.parentpath}\\proxy.txt", "w") as f:
                f.write('\n'.join(good))
        print(f'{Back.RED}THIS TOOL CHECKS WHETHER THE CHECKER CAN CONNECT TO\nYOUR PROXIES OR NOT.{Back.RESET}\n\
{Back.RED}IT DOES NOT GUARANTEE THEY WILL WORK\nIN THE MAIN CHECKER BECAUSE RIOT BANS PUB PROXIES{Back.RESET}')
        input('press enter to return')
        os.system('mode 120,30')

    @staticmethod
    def convert_to_preferred_format(sec):
        sec = sec % (24 * 3600)
        hour = sec // 3600
        sec %= 3600
        min = sec // 60
        sec %= 60
        return "%02d:%02d:%02d" % (hour, min, sec)

    @staticmethod
    def progressbar(pr, ttl):
        if ttl == 0:
            print(f'{Back.RED}YOU DO NOT HAVE ACCOUNTS IN THIS FILE{Back.RESET}')
            os._exit(0)
        percent = 100*(pr/ttl)
        bar = f'{Fore.LIGHTGREEN_EX}━{Fore.RESET}' * \
            int(percent)+f'{Fore.LIGHTRED_EX}━{Fore.RESET}'*int(100-percent)
        return f'{Fore.LIGHTCYAN_EX}[{bar}{Fore.LIGHTCYAN_EX}]{Fore.LIGHTCYAN_EX} {percent:.2f}%{Fore.RESET}'

    def load_assets(self):
        # skinlist
        with requests.get('https://valorant-api.com/v1/weapons/skins/') as r:
            data = json.loads(r.text)
            with open(f'{self.parentpath}\\src\\assets\\skins.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, sort_keys=False, indent=4)

        # user agent
        with requests.get('https://valorant-api.com/v1/version') as r:
            data = r.json()
            Constants.RIOTCLIENT = data['data']['riotClientBuild']

    @staticmethod
    def set_console_title(title: str) -> NoReturn:
        ctypes.windll.kernel32.SetConsoleTitleW(title)


class Account:
    errmsg: str = None
    logpass: str = None
    code: int = None
    token: str = None
    entt: str = None
    puuid: str = None
    unverifiedmail: bool = None
    banuntil: Timestamp = None
    region: str = None
    country: str = None
    lvl: int = None
    rank: str = None
    skins: str = None
    NightShop:str = None
    vp: int = None
    rp: int = None
    lastplayed: Timestamp = None
