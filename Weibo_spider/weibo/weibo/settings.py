# -*- coding: utf-8 -*-

# Scrapy settings for weibo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

from time import strftime, gmtime

BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'

DOWNLOADER_MIDDLEWARES = {
    "weibo.middlewares.UserAgentMiddleware": 401,
    "weibo.middlewares.CookiesMiddleware": 402,
}
ITEM_PIPELINES = {
    "weibo.pipelines.MongoDBPipleline": 403,
}


# Obey robots.txt rules
#ROBOTSTXT_OBEY = True

# 日志保存
fileName = strftime("%Y-%m-%d", gmtime())
LOG_FILE = "weiboSpider{0}.txt".format(fileName)

# 种子队列的信息
REDIE_URL = None
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# 去重队列的信息
FILTER_URL = None
FILTER_HOST = 'localhost'
FILTER_PORT = 6379
FILTER_DB = 0

DOWNLOAD_DELAY = 10  # 间隔时间
# LOG_LEVEL = 'INFO'  # 日志级别
CONCURRENT_REQUESTS = 1  # 默认为16
# CONCURRENT_ITEMS = 1
# CONCURRENT_REQUESTS_PER_IP = 1
REDIRECT_ENABLED = False