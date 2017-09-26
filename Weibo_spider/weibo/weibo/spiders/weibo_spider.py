#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = 'jiangziwei'

import requests
from bs4 import BeautifulSoup
from Weibo_spider.common import weiboID, CURRENT_DEPTH_NUM
from scrapy.http import Request, FormRequest
from scrapy.spiders import CrawlSpider
from Weibo_spider.weibo.weibo.items import InformationItem, TweetsItem, RelationshipsItem, SeedsItem
import re
import json
import logging
import pymongo


def get_response(url, **kwargs):
    cookies = kwargs['cookies'] if 'cookies' in kwargs.keys() else None
    header = kwargs['header'] if 'header' in kwargs.keys() else None
    proxies = kwargs['proxies'] if 'proxies' in kwargs.keys() else None
    s = requests.session()
    try:
        s = BeautifulSoup(s.get(url, proxies=proxies, headers=header, cookies=cookies).content, 'lxml')
        return s
    except Exception as e:
        print('Error', url, e)
        return None


# def get_pages(total, limit):
#     if total % limit > 0:
#         return int(total/limit) + 1
#     else:
#         return int(total/limit)
#
#
# def check_pages(pages, max_page):
#     if pages > max_page:
#         # print('页数过多，只能爬取到250页')
#         return max_page
#     else:
#         return pages

def check_uid(uid):
    clinet = pymongo.MongoClient("localhost", 27017)
    db = clinet["weibo"]
    information = db["Information"]
    result = list(information.find({'_id': "{0}".format(uid)}))
    if len(result) == 0:
        return True
    else:
        return False


def find_all_seeds(depth):
    try:
        clinet = pymongo.MongoClient("localhost", 27017)
        db = clinet["weibo"]
        seed = db["Seeds"]
        result = seed.distinct("uid", {"Depth_num": depth})
        result = list(result)
        return result
    except Exception as e:
        print("Error", e)
        return None


class Spider(CrawlSpider):
    name = "weibo"
    start_urls = list(set(weiboID))
    depth = CURRENT_DEPTH_NUM
    logging.getLogger("requests").setLevel(logging.WARNING)

    def start_requests(self):
        if self.depth > 1:
            seeds = find_all_seeds(self.depth)
            if seeds is not None:
                seeds = list(set(seeds))
                for uid in seeds:
                    result = check_uid(uid)
                    if result:
                        yield Request(url="https://weibo.cn/{0}/info".format(uid), callback=self.parse_information)
                    else:
                        logging.warning("uid: {0}  该用户已经抓取过".format(uid))
            else:
                logging.warning("当前层数没有种子用户")
        else:
            for uid in self.start_urls:
                result = check_uid(uid)
                if result:
                    yield Request(url="https://weibo.cn/{0}/info".format(uid), callback=self.parse_information)
                else:
                    logging.warning("uid: {0}  该用户已经抓取过".format(uid))
                    
    def parse_information(self, response):
        informationItem = InformationItem()
        html = BeautifulSoup(response.body, "lxml")
        uid = re.search(r'(\d+)/info', response.url).group(1)
        try:
            all_html = html.find_all('div', {'class': 'c'})
            info = None
            for aim in all_html:
                if info is None:
                    info = str(aim)
                else:
                    info += str(aim)
            # print(info)

            nickname = re.search(r'昵称[：:]?(.*?)<br/>', info)
            nickname = nickname.group(1) if nickname is not None else ''

            gender = re.search(r'性别[：:]?(.*?)<br/>', info)
            gender = gender.group(1) if gender is not None else ''

            place = re.search(r'地区[：:]?(.*?)<br/>', info)
            place = place.group(1) if place is not None else ''

            introduction = re.search(r'简介[：:]?(.*?)<br/>', info)
            introduction = introduction.group(1) if introduction is not None else ''

            birthday = re.search(r'生日[：:]?(.*?)<br/>', info)
            birthday = birthday.group(1) if birthday is not None else ''

            tag = re.search(r'标签[：:]?(.*?)<br/>', info)
            tag = tag.group(1) if tag is not None else None
            tag = re.findall(r'>(.*?)<', tag) if tag is not None else None
            if tag is not None:
                temp_arr = []
                for t in tag:
                    if t != '\xa0' and t != '更多&gt;&gt;':
                        temp_arr.append(t)
                tag = ','.join(temp_arr)
            else:
                tag = ''

            sex_orientation = re.search(r'性取向[：:]?(.*?)<br/>', info)
            sex_orientation = sex_orientation.group(1) if sex_orientation is not None else None
            if sex_orientation is not None:
                sex_orientation = '同性恋' if sex_orientation == gender else '异性恋'
            else:
                sex_orientation = ''

            sentiment = re.search(r'感情状况[：:]?(.*?)<br/>', info)
            sentiment = sentiment.group(1) if sentiment is not None else ''

            vip_level = re.search(r'会员等级[：:]?(.*?)<br/>', info)
            vip_level = re.search(r'(\d+)级.*?', vip_level.group(1)) if vip_level is not None else None
            vip_level = vip_level.group(1) if vip_level is not None else '0'

            authentication = re.search(r'认证[：:]?(.*?)<br/>', info)
            authentication = authentication.group(1) if authentication is not None else ''

            link = re.search(r'互联网[：:]?(.*?)<br/>', info)
            link = link.group(1) if link is not None else ''

            result = get_response('https://weibo.cn/attgroup/opening?uid={0}'
                                  .format(uid), cookies=response.request.cookies)
            texts = result.find('div', {'class': 'tip2'})
            if texts:
                tweets_num = texts.find('a', {'href': '/{0}/profile'.format(uid)})
                tweets_num = re.findall('微博\[(\d+)\]', tweets_num.text)[0] if tweets_num is not None else ''
                follows_num = texts.find('a', {'href': '/{0}/follow'.format(uid)})
                follows_num = re.findall('关注\[(\d+)\]', follows_num.text)[0] if follows_num is not None else ''
                fans_num = texts.find('a', {'href': '/{0}/fans'.format(uid)})
                fans_num = re.findall('粉丝\[(\d+)\]', fans_num.text)[0] if fans_num is not None else ''
            else:
                tweets_num = ''
                follows_num = ''
                fans_num = ''
            logging.warning('抓取完成========uid:{0} 个人信息'.format(uid))
            informationItem["_id"] = uid
            informationItem["NickName"] = nickname
            informationItem["Gender"] = gender
            informationItem["Place"] = place
            informationItem["Introduction"] = introduction
            informationItem["Birthday"] = birthday
            informationItem["Sex_orientation"] = sex_orientation
            informationItem["Sentiment"] = sentiment
            informationItem["Vip_level"] = vip_level
            informationItem["Authentication"] = authentication
            informationItem["Link"] = link
            informationItem["Tag"] = tag
            informationItem["Tweets_num"] = tweets_num
            informationItem["Follows_num"] = follows_num
            informationItem["Fans_num"] = fans_num

            data_follows = {
                'containerid': '231051_-_followers_-_%s' % uid,
                'page': '1',
                'luicode': '10000011',
                'lfid': '100505%s' % uid,
                'featurecode': '20000320'
            }
            meta_follows = {
                'type': 'follows',
                'current_page': 1,
                'uid': uid,
                'data': data_follows
            }
            data_fans = {
                'containerid': '231051_-_fans_-_%s' % uid,
                'type': 'uid',
                'value': '%s' % uid,
                'since_id': '1',
                'luicode': '10000011',
                'lfid': '100505%s' % uid,
                'featurecode': '20000320'
            }
            meta_fans = {
                'type': 'fans',
                'current_page': 1,
                'uid': uid,
                'data': data_fans
            }
            meta_tweets = {
                'current_page': 1,
                'uid': uid
            }
            yield informationItem
            yield FormRequest(url="https://m.weibo.cn/api/container/getIndex",
                              formdata=data_fans, callback=self.parse_relationship,
                              meta=meta_fans, dont_filter=True)
            yield FormRequest(url="https://m.weibo.cn/api/container/getIndex",
                              formdata=data_follows, callback=self.parse_relationship,
                              meta=meta_follows, dont_filter=True)
            yield Request(url="https://weibo.cn/%s/profile?filter=1&page=1" % (uid),
                          callback=self.parse_tweets, meta=meta_tweets, dont_filter=True)

        except Exception as e:
            print('Error', e)

    def parse_relationship(self, response):
        """
        """
        relationshipsItem = RelationshipsItem()
        seedsItem = SeedsItem()
        re_type = response.meta['type']
        current_page = response.meta['current_page']
        data = response.meta['data']
        uid = response.meta['uid']

        json_data = json.loads(response.body.decode('utf-8'))

        if "msg" in json_data:
            if json_data["msg"] == "\u8fd9\u91cc\u8fd8\u6ca1\u6709\u5185\u5bb9" or json_data["msg"] == "这里还没有内容":
                pass
            else:
                logging.warning("抓取uid:{0} {1} 出现特殊情况".format(uid, re_type))
        else:
            uid_list = []
            card_group = None
            if re_type == 'fans':
                card_group = json_data['cards'][0]['card_group']
            elif re_type == 'follows':
                if current_page == 1:
                    for temp in json_data['cards']:
                        if 'title' in temp:
                            if '的全部关注' in temp['title']:
                                card_group = temp['card_group']
                else:
                    card_group = json_data['cards'][0]['card_group']
            if card_group is not None:
                for card in card_group:
                    uid_temp = card['user']['id']
                    uid_list.append(uid_temp)
            logging.warning('抓取完成========uid:{0} {1}的第{2}页用户数{3}'.format(uid, re_type, current_page, len(uid_list)))
            relationshipsItem["Uid"] = uid
            relationshipsItem["R_uids"] = uid_list
            relationshipsItem["Type"] = re_type

            seedsItem["Depth_num"] = self.depth + 1
            seedsItem["Uids"] = uid_list

            yield relationshipsItem
            yield seedsItem

            if re_type == 'follows':
                data['page'] = str(current_page + 1)
            elif re_type == 'fans':
                data['since_id'] = str(current_page + 1)
            meta = response.meta
            meta['current_page'] = current_page + 1
            meta['data'] = data
            yield FormRequest(url="https://m.weibo.cn/api/container/getIndex",
                              formdata=data, callback=self.parse_relationship,
                              meta=meta, dont_filter=True)

    def parse_tweets(self, response):
        """
        """
        current_page = response.meta['current_page']
        uid = response.meta['uid']
        tweetsItem = TweetsItem()
        html = BeautifulSoup(response.body, "lxml")
        tweets_html_list = html.find_all('div', {'class': 'c', 'id': re.compile('M_')})
        for tweet_html in tweets_html_list:
            if tweet_html:
                tweet_id = tweet_html['id']
                content = tweet_html.find('span', {'class': 'ctt'}).text.replace('\u200b', '').strip()
                cooridinates = tweet_html.find('a', {'href': re.compile('center')})
                cooridinates = cooridinates['href'] if cooridinates is not None else None
                cooridinates = re.search(r'center=((\d|\.|,|-)+)', cooridinates) if cooridinates is not None else None
                cooridinates = cooridinates.group(1) if cooridinates is not None else ''
                attitude_num = tweet_html.find('a', {'href': re.compile('attitude')})
                attitude_num = re.search(r'赞\[(\d+)\]', attitude_num.text)
                attitude_num = attitude_num.group(1) if attitude_num is not None else ''
                repost_num = tweet_html.find('a', {'href': re.compile('repost')})
                repost_num = re.search(r'转发\[(\d+)\]', repost_num.text)
                repost_num = repost_num.group(1) if repost_num is not None else ''
                comment_num = tweet_html.find('a', {'href': re.compile('comment')})
                comment_num = re.search(r'评论\[(\d+)\]', comment_num.text)
                comment_num = comment_num.group(1) if comment_num is not None else ''
                other_info = tweet_html.find('span', {'class': 'ct'})
                if other_info is not None:
                    datetime = re.search(r'((\d|-|:|\s|月|日)+)', other_info.text)
                    datetime = datetime.group(1).replace('\xa0', '') if datetime is not None else ""
                    source = re.search(r'来自(.*)', other_info.text)
                    source = source.group(1) if source is not None else ""
                else:
                    datetime = ''
                    source = ''
                tweetsItem["_id"] = '{0}-{1}'.format(uid, tweet_id)
                tweetsItem["Uid"] = uid
                tweetsItem["Content"] = content
                tweetsItem["Cooridinates"] = cooridinates
                tweetsItem["Attitude_num"] = attitude_num
                tweetsItem["Repost_num"] = repost_num
                tweetsItem["Comment_num"] = comment_num
                tweetsItem["PubTime"] = datetime
                tweetsItem["Source"] = source

                yield tweetsItem
        logging.warning('抓取完成========uid:{0} 的原创微博的第{1}页 微博:{2}条'.format(uid, current_page, len(tweets_html_list)))
        if current_page == 1:
            max_pages = html.find('div', {'id': 'pagelist'})
            max_pages = max_pages.find('input', {'name': 'mp'}) if max_pages is not None else None
            max_pages = max_pages["value"] if max_pages is not None else 1
            max_pages = int(max_pages)
            logging.warning('=========uid:{0}的微博总共有{1}页'.format(uid, max_pages))
            if max_pages > 1:
                meta = response.meta
                meta['current_page'] = current_page + 1
                meta['max_pages'] = max_pages
                yield Request(url="https://weibo.cn/%s/profile?filter=1&page=%s" % (uid, str(current_page + 1)),
                              callback=self.parse_tweets, meta=meta, dont_filter=True)
            else:
                logging.warning("=======uid:{0} 没有原创微博".format(uid))
        elif current_page > 1:
            max_pages = response.meta['max_pages']
            if current_page <= max_pages:
                meta = response.meta
                meta['current_page'] = current_page + 1
                yield Request(url="https://weibo.cn/%s/profile?filter=1&page=%s" % (uid, str(current_page + 1)),
                              callback=self.parse_tweets, meta=meta, dont_filter=True)
