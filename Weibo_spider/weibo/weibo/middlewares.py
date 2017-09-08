# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import logging
import random
from Weibo_spider.weibo.weibo.cookies import initCookie, updateCookie, removeCookie, random_cookies
from Weibo_spider.common import USER_AGENTS
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from scrapy.exceptions import IgnoreRequest
import redis
import json
import os
logger = logging.getLogger(__name__)

class UserAgentMiddleware(object):
    """随机切换User-Agent"""
    def process_request(self, request, spider):
        agent, cookies = random_cookies()
        request.headers["User-Agent"] = agent
        request.cookies = cookies


class CookiesMiddleware(RetryMiddleware):
    """维护登录的Cookie"""
    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)
        self.rconn = settings.get("RCONN", redis.Redis(crawler.settings.get('REDIS_HOST', 'localhsot'), crawler.settings.get('REDIS_PORT', 6379)))
        initCookie(self.rconn, crawler.spider.name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_requset(self, request, spider):
        redisKeys = self.rconn.keys()
        while len(redisKeys) > 0:
            elem = random.choice(redisKeys)
            if "weibo:Cookies" in elem:
                cookie = json.loads(self.rconn.get(elem))
                request.cookies = cookie
                request.meta["accountText"] = elem.split("Cookies:")[-1]
                agent = random.choice(USER_AGENTS)
                request.headers["User-Agent"] = agent
                break
            else:
                redisKeys.remove(elem)

    def process_response(self, request, response, spider):
        if response.status in [300, 301, 302, 303]:
            try:
                redirect_url = response.headers["location"]
                if "login.weibo" in redirect_url or "login.sina" in redirect_url:
                    logger.warning("其中一个cookies已经失效了，去更新...")
                    updateCookie(request.meta['accountText'], self.rconn, spider.name)
                elif "weibo.cn/security" in redirect_url:
                    logger.warning("改账号被限制，正在移除...")
                    removeCookie(request.meta['accountText'], self.rconn, spider.name)
                elif "weibo.cn/pub" in redirect_url:
                    logger.warning(
                        "Redirect to 'http://weibo.cn/pub'!( Account:%s )" % request.meta["accountText"].split("--")[0])
                    reason = response_status_message(response.status)
                    # 重试
                    return self._retry(request, reason, spider) or response
            except Exception as e:
                raise IgnoreRequest
        elif response.status in [403, 414]:
            logger.error("%s! Stopping..." % response.status)
            os.system("pause")
        else:
            return response