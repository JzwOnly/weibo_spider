

项目用的Python3

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
