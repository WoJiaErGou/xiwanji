import scrapy
from scrapy import Selector
import requests
import re
from bs4 import BeautifulSoup
import time
from comment_suning.items import CommentSuningItem
class Comment_spider(scrapy.Spider):
    name='comment_XWJ'
    start_urls=['https://search.suning.com/%E6%B4%97%E7%A2%97%E6%9C%BA/']
    def parse(self, response):
        '''
        信息条数为440+
        '''
        numbers = Selector(response).re('pageNumbers = "(.*?)"')[0]
        print(numbers)
        for i in range(0, int(numbers)):
            page_url = 'https://search.suning.com/%E6%B4%97%E7%A2%97%E6%9C%BA/&iy=0&cp=' + str(i)
            request_page = scrapy.Request(url=page_url, callback=self.parse_pro, dont_filter=True)
            yield request_page

    def parse_pro(self, response):
        for url in response.xpath(".//div[@class='wrap']"):
            product_url_m = url.xpath(".//p[@class='sell-point']/a/@href").extract()[0]
            # 商品的url提取
            product_url = "https:" + product_url_m[:]
            # 商品名称与之前不同，以列表得到，转化为字符串
            may_name_list = url.xpath(".//p[@class='sell-point']/a/text()").extract()
            may_name = ''
            for each in may_name_list:
                may_name = may_name[:] + each
                if each != may_name_list[-1]:
                    may_name = may_name[:] + ' '
            may_name = re.sub(r'\n', '', may_name)
            print(may_name)
            # 产品ID
            ProductID = product_url_m.split('/')[-1].split('.')[0]
            # 对应商品详情页的请求ID
            urlID = product_url_m.split('/')[-2]
            # 实例化item
            # url='https://product.suning.com/0000000000/945018940.html'
            item = CommentSuningItem(ProductID=ProductID, urlID=urlID, may_name=may_name)
            request = scrapy.Request(url=product_url, callback=self.product_parse, meta={'item': item},dont_filter=True)
            yield request



    def product_parse(self,response):
        item=response.meta['item']
        ProductID=item['ProductID']
        urlID=item['urlID']
        product_text=requests.get(response.url).text
        # 品牌
        try:
            brand = Selector(response).re('"brandName":"(.*?)"')[0]
        except:
            try:
                brand = Selector(response).re('<li><b>品牌</b>：(.*?)</li>')[0]
            except:
                try:
                    brand = re.findall('"brandName":"(.*?)"', product_text)[0]
                except:
                    brand = None
        # 去掉品牌括号内容
        if brand:
            if re.findall(r'（.*?）', brand):
                re_com = re.compile('（.*?）')
                brand = brand[:0] + re.sub(re_com, '', brand)
        if brand:
            if re.findall(r'\(.*?\)', brand):
                re_cn = re.compile('\(.*?\)')
                brand = brand[:0] + re.sub(re_cn, '', brand)
        if brand==None:
            try:
                parameter_id=Selector(response).re('"mainPartNumber":"(.*?)"')[0]
            except:
                try:
                    parameter_id=re.findall('"mainPartNumber":"(.*?)"',product_text)[0]
                except:
                    parameter_id=None
            if parameter_id:
                try:
                    parameter_url = 'https://product.suning.com/pds-web/ajax/itemParameter_%s_R0105002_10051.html' % parameter_id
                    para_response = requests.get(parameter_url).text
                    brand=re.findall('"snparameterdesc":"品牌","snparameterVal":"(.*?)"',para_response)[0]
                except:
                    brand=None
            else:
                brand=None
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        headers = {'User-Agent': user_agent}
        for i in range(1,21):
            comment_url='https://review.suning.com/ajax/review_lists/general-000000000'+ProductID+'-'+urlID+'-total-%d-default-10-----reviewList.htm?callback=reviewList' % i
            r = requests.get(comment_url, headers=headers).text
            time.sleep(1)
            content=re.findall('"content":"(.*?)"',r)
            for each in content:
                item['comment']=each
                item['brand']=brand
                yield item

