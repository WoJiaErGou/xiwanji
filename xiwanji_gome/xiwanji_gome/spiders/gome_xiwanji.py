import scrapy
from scrapy import Selector
import requests
import re
from bs4 import BeautifulSoup
from xiwanji_gome.items import XiwanjiGomeItem
class GomeSpider(scrapy.Spider):
    name='gm_XWJ'
    start_urls=['http://list.gome.com.cn/cat10000201-00-0-48-1-0-0-0-1-18yY-0-0-10-0-0-0-0-0.html?intcmp=sy-1000053149-7']
    def parse(self, response):
        maxtext=response.xpath(".//div[@class='min-pager-box']/span[@id='min-pager-number']/text()").extract()[0]
        max_num=maxtext.split('/')[1]
        try:
            numbers=Selector(response).re('<em id="searchTotalNumber">(.*?)</em> 个商品</span>')[0]
            print(numbers)
        except:
            print('找不到总数')
        print(max_num)
        for i in range(1,int(max_num)+1):
        # for i in range(1, 11):
            next_url='http://list.gome.com.cn/cat10000201-00-0-48-1-0-0-0-1-18yY-0-0-10-0-0-0-0-0.html?&page=%d' % i
            request=scrapy.Request(url=next_url,callback=self.detail_parse,dont_filter=True)
            yield request


    def detail_parse(self,response):
        print(len(response.text))
        if len(response.text)< 50000:
            yield scrapy.Request(url=response.url,callback=self.detail_parse,dont_filter=True)
            return None
        # print(response.text)
        for each in response.xpath(".//div[@class='item-tab-warp']"):
            # print(each)
            try:
                print('1')
                p_Name=each.xpath(".//p[@class='item-name']/a/text()").extract()[0]
                may_product_url=each.xpath(".//p[@class='item-name']/a/@href").extract()[0]
                # print(may_product_url)
                product_url='http:'+may_product_url
                print(product_url)
                try:
                    shop_name=each.xpath(".//p[contains(@class,'item-shop')]/span/text()").extract()[0]
                except:
                    shop_name=each.xpath(".//p[contains(@class,'item-shop')]/a/text()").extract()[0]
                item=XiwanjiGomeItem(p_Name=p_Name,shop_name=shop_name,product_url=product_url)
                # url='http://tuan.gome.com.cn/deal/Q8800679974.html?intcmp=list-9000000700-1_6_1'
                #检测product_url是否符合标准，是否多http：///
                http_list = re.findall(r'http:/+', product_url)
                if len(http_list) > 1:
                    url_n = 'http:' + product_url.split('http:')[-1]
                    # print(url_n)
                    request = scrapy.Request(url=product_url, callback=self.product_detail, meta={'item': item},dont_filter=True)
                    yield request
                else:
                    request=scrapy.Request(url=product_url,callback=self.product_detail,meta={'item':item},dont_filter=True)
                    yield request

            except:
                print('失败')


    def product_detail(self,response):
        print('???')
        item=response.meta['item']
        p_Name=item['p_Name']
        product_text = requests.get(response.url).text
        product_soup=BeautifulSoup(product_text,'lxml')
        # print('测试')
        # print(response.body)
        try:
        #国美价，真划算价格
            Price=re.findall('price:"(.*?)"',product_text)
            # print(Price)
            gomeprice=re.findall('gomePrice:"(.*?)"',product_text)
            # print(gomeprice)
            groupprice=re.findall('groupPrice:"(.*?)"',product_text)
            # print(groupprice)
            if Price:
                if Price[0]=='0':
                    price=gomeprice[0]
                    PreferentialPrice=gomeprice[0]
                else:
                    if float(Price[0])<float(gomeprice[0]):
                        price=gomeprice[0]
                        PreferentialPrice=Price[0]
                    else:
                        price=Price[0]
                        PreferentialPrice=gomeprice[0]
            else:
                PreferentialPrice=groupprice[0]
                price=product_soup.select('div.old-price p span')[0].text
            # print(price+' '+PreferentialPrice)
        except:
            price=None
            PreferentialPrice=None
        #商品ID
        try:
            ProductID = Selector(response).re('prdId:"(.*?)"')[0]
        except:
            try:
                ProductID=re.findall('prdId:"(.*?)"',product_text)[0]
            except:
                try:
                    ProductID=re.findall('prdId:"(.*?)"',product_text)[0]
                except:
                    ProductID=response.url.split('/')[-1].split('-')[0]
        #品牌，商品名称，匹数，定变频
        #品牌
        try:
            brand=re.findall('品牌</span><span>(.*?)</span>',product_text)[0]
        except:
            try:
                brand=re.findall('"品牌：(.*?)"',product_text)[0]
            except:
                try:
                    brand=Selector(response).re('"品牌：(.*?)"')[0]
                except:
                    brand=None
        if brand:
            if re.findall(r'（.*?）',brand):
                re_com = re.compile('（.*?）')
                brand = brand[:0] + re.sub(re_com, '', brand)
        if brand:
            if re.findall(r'(.*?)', brand):
                re_cn = re.compile('\(.*?\)')
                brand = brand[:0] + re.sub(re_cn, '', brand)
        # print(brand)
        #餐具容量
        try:
            capacity=re.findall('餐具容量（套）</span><span>(.*?)</span>',product_text)[0]
        except:
            try:
                capacity=Selector(response).re('餐具容量（套）</span><span>(.*?)</span>')[0]
            except:
                capacity=None
        # print(capacity)
        #商品名称
        try:
            X_name=Selector(response).re('型号：(.*?)</div>')[0]
        except:
            try:
                X_name=re.findall('型号</span><span>(.*?)</span>',product_text)[0]
            except:
                try:
                    X_name=Selector(response).re('型号：(.*?)</div>')[0]
                except:
                    try:
                        X_name=re.findall('型号</span><span>(.*?)</span>',product_text)[0]
                    except:
                        try:
                            X_name=re.findall('商品型号：(.*?)</div>',product_text)[0]
                        except:
                            try:
                                X_name=re.findall('商品型号</span><span>(.*?)</span>',product_text)[0]
                            except:
                                X_name=None
        if X_name:
            if brand:
                if brand in X_name:
                    pass
                else:
                    X_name = brand + X_name[:]
        #安装方式
        try:
            install=Selector(response).re('安装方式：(.*?)</div>')[0]
        except:
            try:
                install=Selector(response).re('安装方式</span><span>(.*?)</span>')[0]
            except:
                try:
                    install=re.findall('安装方式：(.*?)</div>',product_text)[0]
                except:
                    try:
                        install=re.findall('安装方式</span><span>(.*?)</span>',product_text)[0]
                    except:
                        install=None
        #控制方式
        try:
            control=Selector(response).re('控制方式：(.*?)</div>')[0]
        except:
            try:
                control=Selector(response).re('控制方式</span><span>(.*?)</span>')[0]
            except:
                try:
                    control=re.findall('控制方式：(.*?)</div>',product_text)[0]
                except:
                    try:
                        control=re.findall('控制方式</span><span>(.*?)</span>',product_text)[0]
                    except:
                        control=None
        #耗水量
        try:
            consump=Selector(response).re('耗水量（L）</span><span>(.*?)</span>')[0]
        except:
            try:
                consump=re.findall('耗水量（L）</span><span>(.*?)</span>',product_text)[0]
            except:
                consump=None
        #颜色
        try:
            color=Selector(response).re('颜色：(.*?)</div>')[0]
        except:
            try:
                color=Selector(response).re('颜色</span><span>(.*?)</span>')[0]
            except:
                try:
                    color=re.findall('颜色：(.*?)</div>',product_text)[0]
                except:
                    try:
                        color=re.findall('颜色</span><span>(.*?)</span>',product_text)[0]
                    except:
                        color=None
        #洗涤方式
        laundry=None
        #处理核心参数，存在三种情况
        text = requests.get(response.url).text
        soup = BeautifulSoup(text, 'lxml')
        try:
            parameter=[]
            div_item = soup.find_all('div', class_='param-item')
            # print(div_item)
            for each in div_item:
                li_list=each.find_all('li')
                for each in li_list:
                    # print(each.text)
                    li_text=re.sub(r'\n','',each.text)
                    # print(li_text)
                    parameter.append(li_text)
            if len(parameter)<1:
                print(1/0)
        except:
            try:
                parameter=[]
                div_item = soup.find('div', class_='guigecanshu_wrap')
                div_canshu = div_item.find_all('div', class_='guigecanshu')
                for each in div_canshu:
                    parameter.append(each.text)
                if len(parameter)<1:
                    print(1/0)
            except:#针对真划算页面的type参数分析
                try:
                    parameter=[]
                    table = soup.find('table', attrs={'class': 'grd-specbox'})
                    tr_list = table.find_all('tr')
                    for each in tr_list:
                        if each.find('td'):
                            td = each.find_all('td')
                            if td:
                                td1 = re.sub(r'\n', '', td[0].text)
                                td2 = re.sub(r'\n', '', td[1].text)
                                parameter.append(td1+':'+td2)
                                # print(td1 + ':' + td2)
                    print(parameter)
                    if len(parameter)< 1:
                        print(1/0)
                except:
                    parameter=None
        #将核心参数转化为字符串形式
        try:
            if parameter==None:
                type=None
            else:
                type='"'
                for i in range(len(parameter)):
                    type=type[:]+parameter[i]
                    if i<len(parameter)-1:
                        type=type[:]+' '
                    if i==len(parameter)-1:
                        type=type[:]+'"'
        except:
            type=None
        # print(type)
        #好评，差评等信息采集
        comment_url='http://ss.gome.com.cn/item/v1/prdevajsonp/appraiseNew/%s/1/all/0/10/flag/appraise' % ProductID
        mark_url='http://ss.gome.com.cn/item/v1/prdevajsonp/productEvaComm/%s/flag/appraise/totleMarks?callback=totleMarks' % ProductID
        #访问comment_url
        comment_text=requests.get(comment_url).text
        try:
            #好评
            GoodCount=re.findall('"good":(.*?),',comment_text)[0]
        except:
            GoodCount = None
            #中评
        try:
            GeneralCount=re.findall('"mid":(.*?),',comment_text)[0]
        except:
            GeneralCount = None
            #差评
        try:
            PoorCount=re.findall('"bad":(.*?),',comment_text)[0]
        except:
            PoorCount = None
            #总评
        try:
            CommentCount=re.findall('"totalCount":(.*?),',comment_text)[0]
        except:
            CommentCount = None
        #访问评论关键字
        mark_text=requests.get(mark_url).text
        #好评度
        try:
            GoodRateShow=re.findall(r'"goodCommentPercent":(\d+)',mark_text)[0]
        except:
            try:
                GoodRateShow=re.findall(r'"good":(\d+),',mark_text)[0]
            except:
                GoodRateShow=None
        try:
            keyword='"'
            word_list=re.findall('"recocontent":"(.*?)"',mark_text)
            for each in word_list:
                if '?'in each:
                    word_list.remove(each)
            if word_list:
                for every in word_list:
                    keyword=keyword[:]+every
                    if every != word_list[-1]:
                        keyword=keyword[:]+' '
                    if every== word_list[-1]:
                        keyword=keyword[:]+'"'
            if len(keyword)<= 1:
                print(1/0)
        except:
            keyword=None

        source='国美'
        item['ProductID']=ProductID
        item['source']=source
        item['price']=price
        item['PreferentialPrice']=PreferentialPrice
        item['brand'] = brand
        item['capacity'] = capacity
        item['X_name'] = X_name
        item['install'] = install
        item['type'] = type
        item['GoodCount'] = GoodCount
        item['GeneralCount'] = GeneralCount
        item['PoorCount'] = PoorCount
        item['CommentCount'] = CommentCount
        item['GoodRateShow'] = GoodRateShow
        item['keyword'] = keyword
        item['control'] = control
        item['consump'] = consump
        item['color'] = color
        item['laundry'] = laundry

        yield item
