# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class InformationItem(Item):
    """用户信息"""
    # 用户id
    _id = Field()
    # 昵称
    NickName = Field()
    # 性别
    Gender = Field()
    # 居住地
    Place = Field()
    # 介绍
    Introduction = Field()
    # 生日
    Birthday = Field()
    # 性取向
    Sex_orientation = Field()
    # 感情状况
    Sentiment = Field()
    # 会员等级
    Vip_level = Field()
    # 认证
    Authentication = Field()
    # 个人主页链接
    Link = Field()
    # 标签
    Tag = Field()
    # 微博数
    Tweets_num = Field()
    # 关注数
    Follows_num = Field()
    # 粉丝数
    Fans_num = Field()

class TweetsItem(Item):
    """微博信息"""
    # 用户ID-微博ID
    _id = Field()
    # 用户id
    Uid = Field()
    # 微博内容
    Content = Field()
    # 定位的坐标
    Cooridinates = Field()
    # 点赞数
    Attitude_num = Field()
    # 转发数
    Repost_num = Field()
    # 评论数
    Comment_num = Field()
    # 发表时间
    PubTime = Field()
    # 来源(手机、平台)
    Source = Field()

class RelationshipsItem(Item):
    """
    关系，粉丝和关注
    """
    # 用户id
    Uid = Field()
    # 相关用户
    R_uids = Field()
    # 相关关系
    Type = Field()

class SeedsItem(Item):
    """
    种子
    抓取的深度
    种子用户算第一层，根据与种子用户的关系(粉丝、关注)的用户算下一层，之后的层以此类推
    """
    # 爬取深度
    Depth_num = Field()
    # 当前深度下的所有种子
    Uids = Field()