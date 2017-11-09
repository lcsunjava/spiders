# -*- coding: utf-8 -*-
""" 
@author: 李超 
@file: spider_wukong.py
@time: 2017/11/08 
"""
import json
import requests
import time
import xlsxwriter
from collections import OrderedDict
import easygui

Colums = ['问题','提问时间','提问者名称','解答者','答案']
BASE_URL = 'https://www.wukong.com/wenda/web/search/loadmore/?search_text=%s&offset=%s&count=%s'

#获取入口url
def api_get_data(api):
    req = requests.get(api)
    res = req.text
    res_dict = json.loads(res)
    return res_dict

#解析数据并格式化
def parse_data(data):
    has_more = False
    data_list = list()

    if not isinstance(data,dict):
        print(u'数据格式化非法：%s'%(data))
        return has_more,data_list
    if data.get('err_no',None)!=0:
        print(u'数据格式化错误：%s' %(data.get('err_tips')))
        return has_more, data_list

    _data = data.get('data',None)
    if _data:
        has_more = _data.get('has_more','false')
        feed_questions = _data.get('feed_question',[])
        for q in feed_questions:
            q_info = OrderedDict()
            ans_list = q.get('ans_list',[])
            question = q.get('question',None)
            if not question:
                break
            q_info['title'] = question['title']
            q_info['create_time'] = transfer_data(int(question['create_time']))
            q_info['uname'] = question['user']['uname']

            if ans_list:
                ans1 = ans_list[0]
                q_info['ans_user'] = ans1['user']['uname']
                q_info['abstract_text'] = ans1['abstract_text']


            data_list.append(q_info)
    return has_more,data_list

#按照给定格式转化日期
def transfer_data(time_stamp):
    struct_time = time.localtime(time_stamp)
    str_time = time.strftime('%Y-%m-%d %H:%M:%S',struct_time)

    return str_time

#以execl格式存储数据
def data_to_execl(work_book,data_list,key_word,row_no):
    work_sheet = work_book.get_worksheet_by_name(key_word)
    if not work_sheet:
        work_sheet = work_book.add_worksheet(key_word)
        row_no = 0
        work_sheet.write_row(row_no,0,Colums)
        row_no += 1

    for i in data_list:
        work_sheet.write_row(row_no,0,i.values())
        row_no += 1

    return row_no

#保存数据
def save_data(work_book,search_url,key_word,r_no):
    ret = api_get_data(search_url)
    has_more,data_list = parse_data(ret)
    r_no = data_to_execl(work_book,data_list,key_word,r_no)

    return has_more,r_no

#入口程序
def main(key_word,count):
    FileName = u'悟空回答_%s.xlsx'%(key_word)
    work_book = xlsxwriter.Workbook(FileName)
    offset = 0
    row_num = 0
    has_more = True

    while has_more:
        search_url = BASE_URL %(key_word,offset,count)
        has_more,row_num = save_data(work_book,search_url,key_word,row_num)
        print (u'已经爬取%s条数据......'%(row_num-1))
        offset += count
        if offset >= 2000:
            break
        work_book.close()


if __name__=="__main__":
    #key_word = raw_input(u"请输入搜索关键字:")
    key_word = easygui.enterbox(u"请输入搜索关键字:")
    count = 100
    main(key_word,count)

