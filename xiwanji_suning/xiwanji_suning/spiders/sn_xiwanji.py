import scrapy
from xiwanji_suning.items import Xiwnaji_suning
from scrapy import Selector
import requests
import re
import json
import time
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
class Suning_spider(scrapy.Spider):
    name = "sn_XWJ"#苏宁洗碗机
    allowed_domain = ['suning.com']
    start_urls =['https://search.suning.com/%E6%B4%97%E7%A2%97%E6%9C%BA/']
    def parse(self, response):
        '''
        信息条数为440+
        '''
        numbers=Selector(response).re('pageNumbers = "(.*?)"')[0]
        print(numbers)
        for i in range(0,int(numbers)):
            page_url='https://search.suning.com/%E6%B4%97%E7%A2%97%E6%9C%BA/&iy=0&cp='+str(i)
            request_page=scrapy.Request(url=page_url,callback=self.parse_pro,dont_filter=True)
            yield request_page
    def parse_pro(self,response):
        for url in response.xpath(".//div[@class='wrap']"):
            product_url_m=url.xpath(".//p[@class='sell-point']/a/@href").extract()[0]
            #商品的url提取
            product_url="https:"+product_url_m[:]
            #商品名称与之前不同，以列表得到，转化为字符串
            may_name_list=url.xpath(".//p[@class='sell-point']/a/text()").extract()
            may_name=''
            for each in may_name_list:
                may_name=may_name[:]+each
                if each != may_name_list[-1]:
                    may_name=may_name[:]+' '
            may_name=re.sub(r'\n','',may_name)
            print(may_name)
            # 店铺名称
            try:
                shop_name=url.xpath(".//p['seller no-cut']/@salesname").extract()[0]
            except:
                shop_name=url.xpath(".//p['seller no-more']/@salesname").extract()[0]
            print(shop_name)
            #产品ID
            ProductID=product_url_m.split('/')[-1].split('.')[0]
            #对应商品详情页的请求ID
            urlID=product_url_m.split('/')[-2]
            #实例化item
            # url='https://product.suning.com/0000000000/945018940.html'
            item=Xiwnaji_suning(ProductID=ProductID,urlID=urlID,may_name=may_name,shop_name=shop_name,product_url=product_url)
            request=scrapy.Request(url=product_url,callback=self.product_parse,meta={'item':item},dont_filter=True)
            yield request
        '''
        已经找到最大页码，待修改代码
        '''

    def product_parse(self,response):
        # print(response.url)
        item=response.meta['item']
        ProductID=item['ProductID']
        urlID=item['urlID']
        may_name=item['may_name']
        shop_name=item['shop_name']
        product_text=requests.get(response.url).text
        #品牌
        try:
            brand = Selector(response).re('"brandName":"(.*?)"')[0]
        except:
            try:
                brand=Selector(response).re('<li><b>品牌</b>：(.*?)</li>')[0]
            except:
                try:
                    brand=re.findall('"brandName":"(.*?)"',product_text)[0]
                except:
                    brand = None
        #去掉品牌括号内容
        if brand:
            if re.findall(r'（.*?）', brand):
                re_com = re.compile('（.*?）')
                brand = brand[:0] + re.sub(re_com, '', brand)
        if brand:
            if re.findall(r'\(.*?\)', brand):
                re_cn = re.compile('\(.*?\)')
                brand = brand[:0] + re.sub(re_cn, '', brand)
        #安装方式
        try:
            install=Selector(response).re('安装方式：(.*?)</li>')[0]
        except:
            try:
                install=Selector(response).re('安装方式</span> </div> </td> <td class="val">(.*?)</td>')[0]
            except:
                try:
                    install=re.findall('安装方式：(.*?)</li>',product_text)[0]
                except:
                    install=None
        #颜色
        try:
            color=Selector(response).re('颜色：(.*?)</li>')[0]
        except:
            try:
                color=Selector(response).re('颜色</span> </div> </td> <td class="val">(.*?)</td>')[0]
            except:
                try:
                    color=re.findall('颜色：(.*?)</li>',product_text)[0]
                except:
                    color=None
        #类型，商品型号
        try:
            p_Name = Selector(response).re('型号</span> </div> </td> <td class="val">(.*?)</td>')[0]
        except:
            try:
                p_Name=re.findall('型号</span> </div> </td> <td class="val">(.*?)</td>',product_text)[0]
                if p_Name==None:
                    p_Name=re.findall('型号</span> </div> </td> <td class="val">(.*?)</td>',product_text)[0]
            except:
                p_Name=None
        if p_Name:
            if brand:
                if brand in p_Name:
                    pass
                else:
                    p_Name=brand+p_Name[:]
        if p_Name:
            if re.findall(r'（.*?）', p_Name):
                re_com = re.compile('（.*?）')
                p_Name = p_Name[:0] + re.sub(re_com, '', p_Name)
        if p_Name:
            if re.findall(r'\(.*?\)', p_Name):
                re_cn = re.compile('\(.*?\)')
                p_Name = p_Name[:0] + re.sub(re_cn, '', p_Name)
        print(p_Name)

        #控制方式
        try:
            control=Selector(response).re('控制方式：(.*?)</li>')[0]
        except:
            try:
                control=Selector(response).re('控制方式</span> </div> </td> <td class="val">(.*?)</td>')[0]
            except:
                try:
                    control=re.findall('控制方式：(.*?)</li>',product_text)[0]
                except:
                    control=None
        #耗水量
        try:
            consump=Selector(response).re('标准程序耗水量</span> </div> </td> <td class="val">(.*?)</td>')[0]
        except:
            try:
                consump=re.findall('标准程序耗水量</span> </div> </td> <td class="val">(.*?)</td>',product_text)[0]
            except:
                consump=None
        #洗涤方式
        try:
            laundry=Selector(response).re('洗碗方式：(.*?)</li>')[0]
        except:
            try:
                laundry=Selector(response).re('洗碗方式</span> </div> </td> <td class="val">(.*?)</td>')[0]
            except:
                try:
                    laundry=re.findall('洗碗方式</span> </div> </td> <td class="val">(.*?)</td>',product_text)[0]
                except:
                    laundry=None
        #餐具容量
        try:
            capacity=Selector(response).re('餐具容量：(.*?)</li>')[0]
        except:
            try:
                capacity=Selector(response).re('餐具容量</span> </div> </td> <td class="val">(.*?)</td>')[0]
            except:
                try:
                    capacity=re.findall('餐具容量：(.*?)</li>',product_text)[0]
                except:
                    try:
                        capacity=re.findall('餐具容量</span> </div> </td> <td class="val">(.*?)</td>',product_text)[0]
                    except:
                        capacity=None
        #核心参数
        type='"'
        response_r=requests.get(response.url).text
        time.sleep(3)
        soup=BeautifulSoup(response_r,'lxml')
        try:
            ul = soup.find('ul', attrs={'class': 'cnt clearfix'})
            li = ul.find_all('li')
            for i in range(len(li)):
                type=type[:]+li[i].text
                if i < len(li)-1:
                    type=type[:]+' '
                if i == len(li)-1:
                    type=type[:]+'"'
        except:
            try:#部分核心参数格式更改
                div = soup.find('div', class_='prod-detail-container')
                ul = div.find('ul', attrs={'class': 'clearfix'})
                li = ul.find_all('li')
                for each in li:
                    li_li = each.find_all('li')
                    for i in range(len(li_li)):
                        type = type[:] + li_li[i].text
                        if i < len(li_li) - 1:
                            type = type[:] + ' '
                        if i == len(li_li) - 1:
                            type = type[:] + '"'
            except:
                type =None
        if type == None:
            try:
                parameter_id=Selector(response).re('"mainPartNumber":"(.*?)"')[0]
            except:
                try:
                    parameter_id=re.findall('"mainPartNumber":"(.*?)"',product_text)[0]
                except:
                    parameter_id=None
                    type=None
            if parameter_id:        
                try:
                    parameter_url = 'https://product.suning.com/pds-web/ajax/itemParameter_%s_R0105002_10051.html' % parameter_id
                    para_response=requests.get(parameter_url).text
                    time.sleep(1)
                    eles = re.findall('"snparameterdesc":"(.*?)"', para_response)
                    souls = re.findall('"snparameterVal":"(.*?)"', para_response)
                    try:
                        type = '"'
                        for i in range(len(eles)):
                            type = type[:] + eles[i] + ':' + souls[i]
                            if i < len(eles) - 1:
                                type = type[:] + ' '
                            if i == len(eles) - 1:
                                type = type[:] + '"'
                    except:
                        type = None
                    try:
                        if len(brand) < 1:
                            brand = re.findall('"snparameterdesc":"品牌","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        brand = None
                    try:
                        color = re.findall('"snparameterdesc":"颜色","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        color = None
                    try:
                        consump = re.findall('"snparameterdesc":"标准程序耗水量","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        consump = None
                    try:
                        install = re.findall('"snparameterdesc":"安装方式","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        install = None
                    try:
                        laundry = re.findall('"snparameterdesc":"洗碗方式","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        laundry = None
                    try:
                        control = re.findall('"snparameterdesc":"控制方式","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        control = None
                    try:
                        capacity = re.findall('"snparameterdesc":"餐具容量","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        capacity = None
                    try:
                        p_Name = re.findall('"snparameterdesc":"型号","snparameterVal":"(.*?)"', para_response)[0]
                    except:
                        p_Name = None
                    if p_Name:
                        if brand:
                            if brand in p_Name:
                                pass
                            else:
                                p_Name = brand + p_Name[:]
                    if p_Name:
                        if re.findall(r'（.*?）', p_Name):
                            re_com = re.compile('（.*?）')
                            p_Name = p_Name[:0] + re.sub(re_com, '', p_Name)
                    if p_Name:
                        if re.findall(r'\(.*?\)', p_Name):
                            re_cn = re.compile('\(.*?\)')
                            p_Name = p_Name[:0] + re.sub(re_cn, '', p_Name)
                    print(p_Name)
                except:
                    type=None

        # 获取相关请求url
        comment_url = 'https://review.suning.com/ajax/review_satisfy/general-000000000' + ProductID + '-' + urlID + '-----satisfy.htm'
        price_url = 'https://pas.suning.com/nspcsale_0_000000000' + ProductID + '_000000000' + ProductID + '_' + urlID + '_10_010_0100101_20268_1000000_9017_10106_Z001.html'
        # 获取评价信息
        try:
            comment_response = requests.get(comment_url).text
            comment_text = json.loads(re.findall(r'\((.*?)\)', comment_response)[0])
            comment_list = comment_text.get('reviewCounts')[0]
            # 差评
            PoorCount = comment_list.get('oneStarCount')
            twoStarCount = comment_list.get('twoStarCount')
            threeStarCount = comment_list.get('threeStarCount')
            fourStarCount = comment_list.get('fourStarCount')
            fiveStarCount = comment_list.get('fiveStarCount')
            # 评论数量
            CommentCount = comment_list.get('totalCount')
            # 好评
            GoodCount = fourStarCount + fiveStarCount
            # 中评
            GeneralCount = twoStarCount + threeStarCount
            # 好评度
            # 得到百分比取整函数
            goodpercent = round(GoodCount / CommentCount * 100)
            generalpercent = round(GeneralCount / CommentCount * 100)
            poorpercent = round(PoorCount / CommentCount * 100)
            commentlist = [GoodCount, GeneralCount, PoorCount]
            percent_list = [goodpercent, generalpercent, poorpercent]
            # 对不满百分之一的判定
            for i in range(len(percent_list)):
                if percent_list[i] == 0 and commentlist[i] != 0 and CommentCount != 0:
                    percent_list[i] = 1
            nomaxpercent = 0  # 定义为累计不是最大百分比数值
            # 好评度计算url='http://res.suning.cn/project/review/js/reviewAll.js?v=20170823001'
            if CommentCount != 0:
                maxpercent = max(goodpercent, generalpercent, poorpercent)
                for each in percent_list:
                    if maxpercent != each:
                        nomaxpercent += each
                GoodRateShow = 100 - nomaxpercent
            else:
                GoodRateShow = 100
        except:
            try:
                comment_package='https://review.suning.com/ajax/review_satisfy/package-000000000' + ProductID + '-' + urlID + '-----satisfy.htm'
                comment_response = requests.get(comment_package).text
                comment_text = json.loads(re.findall(r'\((.*?)\)', comment_response)[0])
                comment_list = comment_text.get('reviewCounts')[0]
                # 差评
                PoorCount = comment_list.get('oneStarCount')
                twoStarCount = comment_list.get('twoStarCount')
                threeStarCount = comment_list.get('threeStarCount')
                fourStarCount = comment_list.get('fourStarCount')
                fiveStarCount = comment_list.get('fiveStarCount')
                # 评论数量
                CommentCount = comment_list.get('totalCount')
                # 好评
                GoodCount = fourStarCount + fiveStarCount
                # 中评
                GeneralCount = twoStarCount + threeStarCount
                # 好评度
                # 得到百分比取整函数
                goodpercent = round(GoodCount / CommentCount * 100)
                generalpercent = round(GeneralCount / CommentCount * 100)
                poorpercent = round(PoorCount / CommentCount * 100)
                commentlist = [GoodCount, GeneralCount, PoorCount]
                percent_list = [goodpercent, generalpercent, poorpercent]
                # 对不满百分之一的判定
                for i in range(len(percent_list)):
                    if percent_list[i] == 0 and commentlist[i] != 0 and CommentCount != 0:
                        percent_list[i] = 1
                nomaxpercent = 0  # 定义为累计不是最大百分比数值
                # 好评度计算url='http://res.suning.cn/project/review/js/reviewAll.js?v=20170823001'
                if CommentCount != 0:
                    maxpercent = max(goodpercent, generalpercent, poorpercent)
                    for each in percent_list:
                        if maxpercent != each:
                            nomaxpercent += each
                    GoodRateShow = 100 - nomaxpercent
                else:
                    GoodRateShow = 100
            except:
                PoorCount=0
                CommentCount=0
                GoodCount=0
                GeneralCount=0
                GoodRateShow=0
        # 有关价格
        try:
            price_response = requests.get(price_url).text
        except requests.RequestException as e:
            print(e)
            time.sleep(2)
            s=requests.session()
            s.keep_alive = False
            s.mount('https://',HTTPAdapter(max_retries=5))
            price_response=s.get(price_url).text
        if len(price_response)>900:
            price_text = json.loads(re.findall(r'\((.*?)\)', price_response)[0])
            price_list = price_text.get('data').get('price').get('saleInfo')[0]
            # 折扣价
            PreferentialPrice = price_list.get('promotionPrice')
            # 原价
            try:
                price = price_list.get('netPrice')
            except:
                price = PreferentialPrice
                if (not price) and PreferentialPrice:
                    price = PreferentialPrice
        else:
            time.sleep(3)
            price_response = requests.get(price_url).text
            if len(price_response)>900:
                price_text = json.loads(re.findall(r'\((.*?)\)', price_response)[0])
                price_list = price_text.get('data').get('price').get('saleInfo')[0]
                # 折扣价
                PreferentialPrice = price_list.get('promotionPrice')
                # 原价
                try:
                    price = price_list.get('netPrice')
                except:
                    price = PreferentialPrice
                    if (not price) and PreferentialPrice:
                        price=PreferentialPrice
            else:
                #作出失败判断并将url归入重试
                price_response=self.retry_price(price_url)
                if len(price_response)>500:
                    price_text = json.loads(re.findall(r'\((.*?)\)', price_response)[0])
                    price_list = price_text.get('data').get('price').get('saleInfo')[0]
                    # 折扣价
                    PreferentialPrice = price_list.get('promotionPrice')
                    # 原价
                    try:
                        price = price_list.get('netPrice')
                    except:
                        price = PreferentialPrice
                        if (not price) and PreferentialPrice:
                            price = PreferentialPrice
                else:
                    PreferentialPrice=None
                    price=None
        if len(price)<1:
            try:
                price_package='https://pas.suning.com/nspcpackage_000000000'+ProductID+'_'+urlID+'_010_0100101_000000000104167973%7C1%7CR2101004%7C52.000_2_1__0.html'
                price_res=requests.get(price_package).text
                PreferentialPrice=re.findall('"promotionPrice":"(.*?)"',price_res)[0]
                price=re.findall('"netPrice":"(.*?)"',price_res)[0]
                if len(price)<1:
                    price=PreferentialPrice
            except:
                price=None
                PreferentialPrice=None
        #防止出现多个字段出现为空
        keyword=None
        if type==None and brand==None and p_Name==None:
            yield None
        else:
            source='苏宁'
            item['p_Name'] = may_name
            item['X_name'] = p_Name
            item['type'] = type
            item['price'] = price
            item['PreferentialPrice'] = PreferentialPrice
            item['brand'] = brand
            item['keyword'] = keyword
            item['PoorCount'] = PoorCount
            item['CommentCount'] = CommentCount
            item['GoodCount'] = GoodCount
            item['GeneralCount'] = GeneralCount
            item['GoodRateShow'] = GoodRateShow
            item['ProductID'] = ProductID
            item['shop_name'] = shop_name
            item['color']=color
            item['source']=source
            item['install']=install
            item['control']=control
            item['consump']=consump
            item['laundry']=laundry
            item['capacity']=capacity
            yield item
    def retry_price(self,price_url):
        price_response_may = requests.get(price_url)
        time.sleep(5)
        price_response=price_response_may.text
        return price_response