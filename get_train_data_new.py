# -*- coding:utf-8 -*-
"""
Author: BigCat
"""
import os
import json
import arrow
import requests
import pandas as pd
from bs4 import BeautifulSoup
from config import *
import datetime
hanzi_arr = ['红', '红', '绿', '黑', '无']
hanzi_dict = {
    "红": 1,
    '1': "红",
    '0': "红",
    "绿": 2,
    '2': "绿",
    "黑": 3,
    '3': "黑",
    "无": 4,
    '4': "无",
    "追红": 1,
    '1': "追红",
    "追绿": 2,
    '2': "追绿",
    "杀红": 3,
    '3': "杀红",
    "杀绿": 4,
    '4': "杀绿",
}

aim_dict = {
    '追红': 1,
    '杀红杀绿': 1,
    '1': '杀红杀绿',
    '杀红追绿': 2,
    '2': '杀红追绿',
    '杀红追绿杀绿': 3,
    '3': '杀红追绿杀绿',
    '杀绿杀红': 4,
    '4': '杀绿杀红',
    '杀绿追红': 5,
    '5': '杀绿追红',
    '杀绿追红杀红': 6,
    '6': '杀绿追红杀红',
    '追红杀绿': 7,
    '7': '追红杀绿',
    '追红追绿': 8,
    '8': '追红追绿',
    '追红追绿杀绿': 9,
    '9': '追红追绿杀绿',
    '追绿杀红': 10,
    '10': '追绿杀红',
    '追绿追红': 11,
    '11': '追绿追红',
    '追绿追红杀红': 12,
    '12': '追绿追红杀红',
    '追绿追红杀绿杀红': 13,
    '13': '追绿追红杀绿杀红',
}


def isLeapYear(years):
    '''
    通过判断闰年，获取年份years下一年的总天数
    :param years: 年份，int
    :return:days_sum，一年的总天数
    '''
    # 断言：年份不为整数时，抛出异常。
    assert isinstance(years, int), "请输入整数年，如 2018"

    if ((years % 4 == 0 and years % 100 != 0) or (years % 400 == 0)):  # 判断是否是闰年
        # print(years, "是闰年")
        days_sum = 366
        return days_sum
    else:
        # print(years, '不是闰年')
        days_sum = 365
        return days_sum


def getAllDayPerYear(years):
    '''
    获取一年的所有日期
    :param years:年份
    :return:全部日期列表
    '''
    start_date = '%s-1-1' % years
    a = 0
    all_date_list = []
    days_sum = isLeapYear(int(years))
    print()
    while a < days_sum:
        b = arrow.get(start_date).shift(days=a).format("YYYY-MM-DD")
        a += 1
        all_date_list.append(b)
    # print(all_date_list)
    return all_date_list


def get_current_number(date):
    """ 获取最新一天的数字
    :return: int
    """
    r = requests.get("{}".format("http://112.124.38.182:7529/lottery-api/api/ml/machineLearningTrain3?date=" + date))
    json_obj = json.loads(r.content)
    single_data = json_obj['data']
    return single_data


def spider(mode, date_list):
    """ 爬取历史数据
    :param start 开始一期
    :param end 最近一期
    :param mode 模式
    :return:
    """
    trs = []
    for dt in date_list:
        s_list = get_current_number(dt)
        trs += s_list
    data = []
    for tr in trs:
        item = dict()
        item[u"期数"] = str(tr['issue']).strip()
        item[u"红球号码_1"] = hanzi_dict[str(tr['arrowColor'])]
        item[u"红球号码_2"] = hanzi_dict[str(tr['grapesColor'])]
        item[u"红球号码_3"] = hanzi_dict[str(tr['trainColor'])]
        item[u"红球号码_4"] = hanzi_dict[str(tr['treeColor'])]
        item[u"红球号码_5"] = str(tr['bettingNum_zh'] + 10).strip()
        item[u"红球号码_6"] = str(tr['rightNum_zh'] + 10).strip()
        item[u"红球号码_7"] = str(tr['wrongNum_zh'] + 10).strip()
        item[u"红球号码_8"] = str(tr['realRightNum_zh'] + 10).strip()
        item[u"红球号码_9"] = str(tr['bettingNum_zl'] + 10).strip()
        item[u"红球号码_10"] = str(tr['rightNum_zl'] + 10).strip()
        item[u"红球号码_11"] = str(tr['wrongNum_zl'] + 10).strip()
        item[u"红球号码_12"] = str(tr['realRightNum_zl'] + 10).strip()
        item[u"红球号码_13"] = aim_dict[tr['aimThis'].replace(",", "")]
        data.append(item)

    if mode == "train":
        df = pd.DataFrame(data)
        df.to_csv("{}{}".format(train_data_path, "data.csv"), encoding="utf-8")
    elif mode == "predict":
        return pd.DataFrame(data)

def spider_predict(mode):
    """ 爬取历史数据
    :param start 开始一期
    :param end 最近一期
    :param mode 模式
    :return:
    """
    dt = str(datetime.date.today())
    trs = get_current_number(dt)
    data = []
    first_issue = 0
    last_issue = 0
    index = 0
    for tr in trs:
        if index == 0:
            first_issue = int(tr['issue'])
        if index == len(trs) - 1 :
            last_issue = int(tr['issue'])
        index += 1
        item = [hanzi_dict[str(tr['arrowColor'])], hanzi_dict[str(tr['grapesColor'])], hanzi_dict[str(tr['trainColor'])],
                                          hanzi_dict[str(tr['treeColor'])], tr['bettingNum_zh'] + 10, tr['rightNum_zh'] + 10,
                                          tr['wrongNum_zh'] + 10, tr['realRightNum_zh'] + 10, tr['bettingNum_zl'] + 10,
                                          tr['rightNum_zl'] + 10, tr['wrongNum_zl'] + 10, tr['realRightNum_zl'] + 10,
                                          aim_dict[tr['aimThis'].replace(",", "")]]
        data.append(item)
        #index += 1
        #if index >= 3:
        #    break

    if mode == "train":
        df = pd.DataFrame(data)
        df.to_csv("{}{}".format(train_data_path, "data.csv"), encoding="utf-8")
    elif mode == "predict":
        return data

def get_latest_issue():
    """ 爬取历史数据
    :param start 开始一期
    :param end 最近一期
    :param mode 模式
    :return:
    """
    dt = str(datetime.date.today())
    trs = get_current_number(dt)
    index = 0
    for tr in trs:
        if index == 0:
            first_issue = int(tr['issue'])
            break
    return first_issue

if __name__ == "__main__":
    print("[INFO] 正在获取数据。。。")
    # date_list_2021 = getAllDayPerYear("2021")
    # date_list_2020 = getAllDayPerYear("2020")
    # all_date_list = date_list_2020 + date_list_2021
    all_date_list = getAllDayPerYear("2022")
    # print(all_date_list)
    #spider('train', all_date_list)
    spider_predict('predict')
    print("[INFO] 数据获取完成，请查看data/data.csv文件。")
