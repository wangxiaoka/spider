# -*- encoding = utf-8 -*-
import urllib.request
from bs4 import BeautifulSoup
import os,sys,re
import requests
import datetime
import json
from test_mongo import database_mongo
import copy


source = 'https://car.autohome.com.cn'

def GetHLDPicLink(url):
    response = requests.get(url)
    # print(response.text)
    # print(type(response))
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    # print(type(soup))
    lst = soup.find_all(attrs={'class': 'interval01-list'})
    # print(len(lst))
    res = []
    l = []
    for ls in lst:
        ls_li = ls.find_all(name='li')
        # print(len(ls_li))
        for ls_li_0 in ls_li:
            temp = ls_li_0.find(name='div').find(name='p')
            # print(temp)
            # print(temp['id'])
            # print(temp.a['href'])
            # print(temp.string)
            l.append(temp['id'].split('p')[1])
            l.append(temp.a['href'])
            l.append(temp.string)
            res.append(l)
            l = []
    return res
    # print(len(res))
    # for a in res:
    #     print(a)

def FindFirstLinkList(style):
    source = 'https://car.autohome.com.cn'
    url_pic = 'https://car.autohome.com.cn/pic/series-s' + style + '/771.html#pvareaid=3454542'
    response = requests.get(url_pic)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    temp = soup.find(attrs={'class': 'cartab-title'})
    uibox = temp.find_all_next(attrs={'class': 'uibox'})
    # print(len(uibox), uibox)
    res = []
    l = []
    for ub in uibox:
        u1 = ub.find(name='div')
        href = u1.a['href']
        flag = href.split('-')[2].split('.')[0]
        text = u1.a.get_text()
        # print(href)
        # print(text)
        # print(flag)

        l.append(flag)
        l.append(text)
        l.append(href)
        li = ub.find(name='li')
        lk = li.a['href']
        l.append(source + lk)
        res.append(l)
        l = []
    # print(res)
    return res

def GetPicLink(url_pic):
    response = requests.get(url_pic)
    html = response.text
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    # print(soup)
    pic = soup.find(attrs={'class': 'pic'})
    # print(pic)
    pic_lk = 'http:' + pic.img['src']
    return pic_lk

def SavePic(url):
    filename = url.split('/')[-1]
    r = requests.get(url)
    # f = open(filename, 'wb')
    with open(filename, 'wb') as f:
        f.write(r.content)
        f.close()



def EnterFold(fold):
    if not os.path.exists(fold):
        os.mkdir(fold)
        os.chdir(fold)
    else:
        os.chdir(fold)

def GetBrandAuto(brand):
    # brand = 33  ##奥迪

    url = 'https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=' + \
          str(brand) + '%20&fctId=0%20&seriesId=0 '

    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    current = soup.find(attrs={'class': 'current'})
    # print(len(current), current)
    # print(len(current), current[1])
    dl = current.find(name='dl')
    # print(len(dl), dl)
    dll = {}
    temp = ''
    for dl_l in dl:
        # print(dl_l.name)
        if dl_l.name == 'dt':
            # temp = dl_l.a['id']
            temp = dl_l.a.text
            dll[temp] = []
            # temp = 'yiqi'
        elif dl_l.name == 'dd':
            dd_xinxi = []
            dd_xinxi.append(dl_l.a.text)
            dd_xinxi.append(dl_l.a['href'])
            dll[temp].append(dd_xinxi)
            # print(dll)
            # input('dd_xinxi')
    # print(dll)
    return dll



def GetAllAuto():
    url = 'https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=0%20&fctId=0%20&seriesId=0'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    # print(soup)
    ul = soup.find_all(name='ul')
    cls = soup.find_all(class_='cartree-letter')
    i = 0
    letter = {}
    for u in ul:   #  23个字母顺序
        li = u.find_all(name='li')
        l = []
        for li_a in li:   #循环5次
            # l.append(len(li))
            l_t = {}
            l_t_t = []
            brandid = li_a.attrs['id'].split('b')[1]
            l_t_t.append(brandid)
            l_t_t.append(li_a.h3.a.attrs['href'])
            string = li_a.h3.a.text
            # print(string)
            p1 = re.compile(r'[(](.*?)[)]', re.S)
            l_t_t.append(int(re.findall(p1, string)[0]))
            # 补充品牌下面的款式，列表形式，（但数组内容是字典，如{东风本田：[], 广州本田:[], 进口本田:[]}）
            # 需要一个方法，可以获取本田下面的生产地和款式
            # 输入：某品牌的品牌号
            # 输出：字典，包含生产地和对应款式
            # l_t_t.append(字典)
            l_t_t.append(GetBrandAuto(brandid))
            l_t[string.split('(')[0]] = l_t_t
            l.append(l_t)
        letter[cls[i].text] = l
        i = i + 1
    return letter

def GetBrandPic(folder, url):
    EnterFold(folder)
    piclinklist = GetHLDPicLink(url)
    # print(piclinklist)

    for link in piclinklist:
        # link  :   ['33655', '//www.autohome.com.cn/spec/33655/#pvareaid=2042128', '2018款 2.0T 两驱精英版 5座']

        EnterFold(link[2] + '-' + link[0])
        lk = FindFirstLinkList(link[0])
        # lk:
        # ['1', '车身外观', '/pic/series-s30501/771-1.html#pvareaid=2042222','https://car.autohome.com.cn/photo/30501/1/4117609.html#pvareaid=2042264'],
        # ['10', '中控方向盘', '/pic/series-s30501/771-10.html#pvareaid=2042222','https://car.autohome.com.cn/photo/30501/10/4117562.html#pvareaid=2042264'],
        # ['3', '车厢座椅', '/pic/series-s30501/771-3.html#pvareaid=2042222', 'https://car.autohome.com.cn/photo/30501/3/4117602.html#pvareaid=2042264'],
        # ['12', '其它细节', '/pic/series-s30501/771-12.html#pvareaid=2042222','https://car.autohome.com.cn/photo/30501/12/4117522.html#pvareaid=2042264']
        for xijie in lk:
            EnterFold(xijie[1])
            pic_lk = GetPicLink(xijie[3])
            SavePic(pic_lk)
            os.chdir(os.path.dirname(os.getcwd()))
            # input("mark")
        # input("输入Enter：")
        os.chdir(os.path.dirname(os.getcwd()))

    print("%s图片采集完成！！！" % (folder.split('\\')[-1]))

def save_data_json(dic_data):
    data = json.dumps(dic_data)
    with open('auto.json','w') as f:
        f.write(data)
        f.close()
    print("保存数据完毕！")

def save_data_mongo(dic_data):
    mongo = database_mongo('192.168.0.108', 27017, 'AutoCar', 'kinds')
    mongo.save_data(dic_data)


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    url = 'https://car.autohome.com.cn/price/series-771.html'
    folder = u'E:\python3\汉兰达771'

    url1 = 'https://car.autohome.com.cn/price/series-4645.html'
    folder1 = u'E:\python3\CHR-4645'
    # GetBrandPic(folder1, url1)
    ALL_CAR = GetAllAuto()
    # 分类说明：
    # 第一层：每个字母以字典为单位记录(第二层)；
    # 第二层：每个字母下面的品牌以字典为单位进行记录(第三层)；
    # 第三层：各品牌特征以数组记录：[品牌代码，品牌网址，品牌数量(款式总数)，[各个系列（第四层）]]
    # 第四层：品牌下面的各个系列，以生产地分类，以字典记录(第五层)：
    # 第五层：各个产地的款式名称(以数组记录)；
    #{'ALPINA': ['276', '/price/brand-276.html', 1, {'ALPINA': [['ALPINA B4 (1)', '/price/series-4212.html']]}]},
    # print(ALL_CAR)
    mongodb = copy.deepcopy(ALL_CAR)
    save_data_mongo(mongodb)
    save_data_json(ALL_CAR)
    print("所有汽车型号采集完毕！")
    print('采集时间：', (datetime.datetime.now() - starttime))
    # print(ALL_CAR['A'])

    num_brand = 0
    num_xilie = 0
    num_kuanshi = 0
    num_kuanshi1 = 0
    for letter in ALL_CAR:
        print(letter)
        BRAND = ALL_CAR[letter]
        num_brand = num_brand + len(BRAND)
        for brand in BRAND:
            print('type(brand)', type(brand))  # dic
            print(len(brand), brand)
            for brand_s in brand:
                bb = brand[brand_s]    ## 品牌详情,shuzu
                print('type(bb)', type(bb))
                print(len(bb), bb)
                num_kuanshi = num_kuanshi + bb[2]
                xilie = bb[3]   ### 字典
                print('type(bb[3])', type(bb[3]))
                print(len(bb[3]), bb[3])
                num_xilie = num_xilie + len(bb[3])
                for xl in xilie:
                    num_kuanshi1 = num_kuanshi1 + len(xilie[xl])

        #         input('mark1')
        #     input('mark2')
        # input('mark3')
        print('num_brand',  num_brand)
        print('num_xilie',  num_xilie)   #######生产地
        print('num_kuanshi',  num_kuanshi)
        print('num_kuanshi1',  num_kuanshi1)

        print('统计时间：', (datetime.datetime.now() - starttime))








