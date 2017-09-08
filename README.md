

项目用的Python3

通过一批种子用户，抓取用户信息，所有微博，粉丝和关注
关于粉丝抓取，由于微博的限制，也不知道说明原因，无法抓取全部粉丝。
在我编写代码时是这么个情况
1 通过m.weibo.cn   可以抓取用户前250页的粉丝
2 通过weibo.com    这个更少只有5页
3 通过weibo.cn     这个上限是20页，不会再多了


![用户信息](https://github.com/JzwOnly/weibo_spider/blob/master/Weibo_spider/img/Infomation.png)
![微博信息](https://github.com/JzwOnly/weibo_spider/blob/master/Weibo_spider/img/Tweets.png)

使用:
    所需库：
        1 selenium
        2 requests
        3 bs4
        4 scrapy
        5 mongoDB
        6 redis

    需要修改的地方:
    1 在cookies.py 文件里添加新浪微博账号
    2 第一层的种子用户可以在common.py 文件中修改
    3 该爬虫是按层爬取用户的，所以在跑完第一层所有的种子用户之后需要手动去commit.py 文件中修改 "CURRENT_DEPTH_NUM" (当前层数)
