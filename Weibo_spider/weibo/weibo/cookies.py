#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = 'jiangziwei'

import logging
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import redis
from Weibo_spider.weibo.weibo.settings import REDIS_HOST, REDIS_PORT
import random
import json
from Weibo_spider.common import USER_AGENTS

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人
"""
 0 表示从https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18) 登录以获取cookie
 1 表示从https://weibo.cn/login/   登录以获取Cookie
"""
COOKIE_STYLE = 0
PHANTOMJSPATH = '/Users/jiangziwei/phantomjs-2.1.1-macosx/bin/phantomjs'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
)
"""
    微博账号,填几个新浪微博账号
"""
myWeiBo = [
    {'no': '账号', 'pwd': '密码'},
]

def get_cookie(account, password):
    if COOKIE_STYLE == 0:
        return get_cookie_from_weibo_cn(account,password)
    elif COOKIE_STYLE == 1:
        return
    else:
        logger.error('COOKIE_STYLE Error!')

def get_cookie_from_weibo_cn(account, password):
    """通过weibo.cn登录获取cookie"""
    try:
        browser = webdriver.PhantomJS(executable_path=PHANTOMJSPATH,desired_capabilities=dcap)
        browser.get("https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=")
        # 页面是动态加载的，不等待截出来的图片是空白的
        deal_login_html(browser, account, password)
        cookie = {}
        while "登录" in browser.title:
            print('网差，还没跳转到')
            browser.refresh()
            deal_login_html(browser, account, password)
        if "我的首页" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
            logger.warning('账号：{0},获取登录Cookie成功'.format(account))
        return cookie
        # 进行登录操作
    except Exception as e:
        logger.error('Failed %s!' %e)
    finally:
        try:
            browser.quit()
        except Exception as e:
            pass


def deal_login_html(browser, account, password):
    time.sleep(1)
    html = browser.page_source
    # print(html)
    # browser.save_screenshot('aa.png')

    username = browser.find_element_by_xpath('//input[@id="loginName"]')
    username.clear()
    username.send_keys(account)

    psd = browser.find_element_by_xpath('//input[@id="loginPassword"]')
    psd.clear()
    psd.send_keys(password)
    browser.save_screenshot('commit.png')

    commit = browser.find_element_by_xpath('//a[@id="loginAction"]')
    commit.click()
    time.sleep(3)

    print(browser.title)
    # browser.save_screenshot('bb.png')


def toStr(s):
    return s.decode('utf-8')
def initCookie(rconn, spiderName):
    """获取所有提供的账号的登录Cookies, 存入Redis。 如果Redis已有该账号Cookies，就不再获取"""
    for weibo in myWeiBo:
        # 爬虫名:Cookies:账号--密码
        if rconn.get("%s:Cookies:%s--%s" % (spiderName, weibo["no"], weibo["pwd"])) is None:
            account = weibo["no"]
            password = weibo["pwd"]
            cookie = get_cookie(account,password)
            if len(cookie) > 0:
                rconn.set("%s:Cookies:%s--%s" % (spiderName, account, password), cookie)
        strCookies = list(map(toStr,rconn.keys()))
        logger.warning(strCookies)
        cookieNum = "".join(strCookies).count("weibo:Cookies")
        logging.warning("cookies总共有{0}个".format(cookieNum))
        if cookieNum == 0:
            logger.warning("Stopping...")
            os.system("pause")

def updateCookie(accountText, rconn, spiderName):
    """ 更新一个账号的Cookie """
    account = accountText.split("--")[0]
    password = accountText.split("--")[1]
    cookie = get_cookie(account, password)
    if len(cookie) > 0:
        logger.warning("The cookie of %s has been updated successfully!" % account)
        rconn.set("%s:Cookies:%s" % (spiderName, accountText), cookie)
    else:
        logger.warning("The cookie of %s updated failed! Remove it!" % accountText)
        removeCookie(accountText, rconn, spiderName)

def removeCookie(accountText, rconn, spiderName):
    """ 删除某个账号的Cookie """
    rconn.delete("%s:Cookies:%s" % (spiderName, accountText))
    cookieNum = "".join(rconn.keys()).count("weibo:Cookies")
    logger.warning("The num of the cookies left is %s" % cookieNum)
    if cookieNum == 0:
        logger.warning("Stopping...")
        os.system("pause")


def random_cookies():
    rconn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    redisKeys = rconn.keys()
    cookies = ''
    accountText = ''
    while len(redisKeys) > 0:
        elem = random.choice(redisKeys)
        if "weibo:Cookies" in elem.decode("utf-8"):
            cookie = rconn.get(elem).decode("utf-8")
            cookies = eval(cookie)
            # accountText = elem.split("Cookies:")[-1]
            break
        else:
            redisKeys.remove(elem)
    agent = random.choice(USER_AGENTS)
    return agent, cookies
