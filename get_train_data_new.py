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

hanzi_dict = {
    "红": 1,
    "绿": 2,
    "黑": 3,
    "无": 4,
    "追红": 1,
    "追绿": 2,
    "杀红": 3,
    "杀绿": 4
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
    r = requests.get("{}".format("http://112.124.38.182:7529/lottery-api/api/ml/machineLearningTrain3?date="+date))
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
        item[u"红球号码_5"] = str(tr['bettingNum_zh']+10).strip()
        item[u"红球号码_6"] = str(tr['rightNum_zh']+10).strip()
        item[u"红球号码_7"] = str(tr['wrongNum_zh']+10).strip()
        item[u"红球号码_8"] = str(tr['realRightNum_zh']+10).strip()
        item[u"红球号码_9"] = str(tr['bettingNum_zl']+10).strip()
        item[u"红球号码_10"] = str(tr['rightNum_zl']+10).strip()
        item[u"红球号码_11"] = str(tr['wrongNum_zl']+10).strip()
        item[u"红球号码_12"] = str(tr['realRightNum_zl']+10).strip()
        item[u"红球号码_13"] = tr['aimThis'].replace(",","").replace("追红","1").replace("追绿","2").replace("杀红","3").replace("杀绿","4")
        data.append(item)

    if mode == "train":
        df = pd.DataFrame(data)
        df.to_csv("{}{}".format(train_data_path, "data.csv"), encoding="utf-8")
    elif mode == "predict":
        return pd.DataFrame(data)


if __name__ == "__main__":
    print("[INFO] 正在获取数据。。。")
    #date_list_2021 = getAllDayPerYear("2021")
    #date_list_2020 = getAllDayPerYear("2020")
    #all_date_list = date_list_2020 + date_list_2021
    all_date_list = ['2022-05-08']
    print(all_date_list)
    spider('train', all_date_list)
    print("[INFO] 数据获取完成，请查看data/data.csv文件。")
