# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XiwanjiGomeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 商品长名称
    p_Name = scrapy.Field()
    # 店铺名称
    shop_name = scrapy.Field()
    # 商品ID
    ProductID = scrapy.Field()
    # 价格区间稍后设置
    PriceRange = scrapy.Field()
    # 正价
    price = scrapy.Field()
    # 折扣价
    PreferentialPrice = scrapy.Field()
    # 评论总数
    CommentCount = scrapy.Field()
    # 好评度
    GoodRateShow = scrapy.Field()
    # 好评
    GoodCount = scrapy.Field()
    # 中评
    GeneralCount = scrapy.Field()
    # 差评
    PoorCount = scrapy.Field()
    # 评论关键字
    keyword = scrapy.Field()
    # 类别：核心参数等
    type = scrapy.Field()
    # 品牌
    brand = scrapy.Field()
    # 商品型号
    X_name = scrapy.Field()
    # 安装方式
    install = scrapy.Field()
    # 控制方式
    control = scrapy.Field()
    # 耗水量
    consump = scrapy.Field()
    # 颜色
    color = scrapy.Field()
    # 洗涤方式
    laundry = scrapy.Field()
    # 商品链接
    # 餐具容量
    capacity = scrapy.Field()
    product_url = scrapy.Field()
    # 不需要展示的数据
    # url前面部分id
    # urlID = scrapy.Field()
    # 来源
    source = scrapy.Field()

