# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
from logging import Formatter, getLogger, StreamHandler
import hashlib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
from IPython import embed
import warnings
warnings.filterwarnings('ignore')

class Color(object):
    """
     utility to return ansi colored text.
    """
    colors = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
        'bgred': 41,
        'bggrey': 100
    }
    prefix = '\033['
    suffix = '\033[0m'

    def colored(self, text, color=None):
        if color not in self.colors:
            color = 'white'
        clr = self.colors[color]
        return (self.prefix+'%dm%s'+self.suffix) % (clr, text)


colored = Color().colored

class ColoredFormatter(Formatter):

    def format(self, record):
        message = record.getMessage()
        mapping = {
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bgred',
            'DEBUG': 'bggrey',
            'SUCCESS': 'green'
        }
        clr = mapping.get(record.levelname, 'white')
        return colored(record.levelname, clr) + ': ' + message

log = logging.getLogger("HashingCheck")
log.setLevel(logging.INFO)
handler = StreamHandler()
formatter = ColoredFormatter()
handler.setFormatter(formatter)
log.addHandler(handler)
log.info("Logger initialized")

logging.SUCCESS = 25  # between WARNING and INFO
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
setattr(log, 'success', lambda message, *args: log._log(logging.SUCCESS, message, args))

log.info("This script will check if your password is easily found in a hash-table! \n")

password = input("Input password suggestion: ").encode()
log.info("Hashing MD5...")
m  = hashlib.md5()
m.update(password)
pw_md5 = m.hexdigest()

log.info("Hashing SHA-1...")
hash_object = hashlib.sha1(password)
pw_sh1 = hash_object.hexdigest()

log.info("Configuring webdriver...")
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_argument("--ignore-certificate-errors")


driver = webdriver.Chrome(options=options)
log.info(f"Reverse searching MD5 hash-value: {pw_md5}")
md5_safe = False
url = f"https://md5.gromweb.com/?md5={pw_md5}"
driver.get(url)
soup = BeautifulSoup(driver.page_source, features="html.parser")
driver.quit()
try:
    md5_hash = soup.find(class_="long-content hash").text
    md5_plainText = soup.find(class_="long-content string").text
except AttributeError:
    #No hash found
    log.info("No MD5 hash matched in DB!")
    md5_safe = True

driver = webdriver.Chrome(options=options)
log.info(f"Reverse searching SHA-1 hash-value: {pw_sh1}")
sha1_safe = False
url = f"https://sha1.gromweb.com/?hash={pw_sh1}"
driver.get(url)
soup = BeautifulSoup(driver.page_source, features="html.parser")
driver.quit()
try:
    sha1_hash = soup.find(class_="long-content hash").text
    sha1_plainText = soup.find(class_="long-content string").text
except AttributeError:
    #No hash found
    log.info("No SHA-1 hash matched in DB!")
    sha1_safe = True

if md5_safe and sha1_safe:
    log.success("No match found for MD5 or SHA-1 found; password seems secure!")
else:
    if not md5_safe:
        log.warning(f"Found MD5 match for {md5_hash} - reversed to '{md5_plainText}'!")
    if not sha1_safe:
        log.warning(f"Found SHA-1 match for {sha1_hash} - reversed to '{sha1_plainText}'!")
    log.error("This is not a safe password choice")
