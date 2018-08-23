# -*- coding: utf-8 -*-
# 使用 selenium 抓取 facebook 公開社團，團購主
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import urllib
import math
import csv
import getpass
import os
import sys
import subprocess
import random






def open_browser():
    '''打開瀏覽器
    '''

    # disable chrome alter
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)

    # 執行 chromedriver.exe
    cmd = os.getcwd() + "\\Tool\\chromedriver.exe"
    # print cmd
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    driver = webdriver.Chrome(cmd, chrome_options=chrome_options)
    # 打開瀏覽器
    driver.get("https://www.facebook.com/")

    return driver



def login(driver, usr, pwd):
    '''登入臉書帳號
    '''

    # login facebook
    elem = driver.find_element_by_id("email")
    elem.send_keys(usr)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(pwd)

    # click longin button
    try:
        elem = driver.find_element_by_id("u_0_2")
        elem.click()
    except:
        elem = driver.find_element_by_id("u_0_w")
        elem.click()

    return driver


def get_post_class(driver):
    '''獲取每個登入帳號看到的po文人的資料 class
    '''
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    links = soup.select("head")[0].select("link")
    for link in links:
    	try:
    		if link["data-bootloader-hash"] == "TvoAA":
    			script = link
    			break
    	except:
    		continue
    # print script

    # 獲取class    
    start = str(script).find("utf-8,.")
    end = str(script).find("{margin-bottom")
    class_length = end - start - 7
    start = 102+class_length-11
    post_class = str(script)[start:(start+class_length)]
    # print post_class

    return post_class





def get_fb_group(driver, place, data, post_class):

    # 地區 兩個關鍵字搜尋社團
    # search_url = 'https://www.facebook.com/search/groups/?q='+ urllib.quote("團購 " + place) +'&filters_groups_show_only={"name":"public_groups","args":""}'
    search_url = 'https://www.facebook.com/search/groups/?q='+ urllib.quote(place) +'&filters_groups_show_only={"name":"public_groups","args":""}'
    driver.get(search_url)

    # 滑到網頁最底
    while True:
        try:
            driver.find_element_by_id("browse_end_of_results_footer")
            break
        except:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")    
            time.sleep(1)

    # 獲取所有社團網址
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.select("._401d")[:-1]

    # 儲存團購主臉書名稱
    poster_name_set = set()

    # 分別抓取社團po文裡包含 團購 與 面交 兩個關鍵字的團購主臉書名稱與臉書網址
    for i in links:

    	# 確認一天貼文是否有超過(包含)五篇
        group_info = (i.select("._pac")[0].text.encode("utf-8")).split("·")
        if len(group_info) == 1:
            continue
        group_info = group_info[1]
        if "天" not in group_info:
            continue
        if ("5" not in group_info) and ("6" not in group_info) and ("7" not in group_info) and ("8" not in group_info) and ("9" not in group_info) and ("10" not in group_info):
            continue

        # 依po文時間排序
        group_page = "https://www.facebook.com" + i.select("a")[0]["href"].replace("?ref=br_rs", "") + "search?query=" + urllib.quote("團購 面交") + '&filters_rp_chrono_sort={"name":"chronosort","args":""}'
        print group_page
        time.sleep(random.randint(2, 3))
        driver.get(group_page)
        time.sleep(random.randint(1, 2))

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 關鍵字搜尋無結果
        if len(soup.select("#empty_result_error")) != 0:
        	print "NO DATA"
        	continue
    
        # 搜尋結果第一篇po的年份，若小於2017則直接跳過該社團
        first_post = soup.select("." + post_class)

        try:
            if len(first_post.select("._5pcq")) != 0:
                year = int(first_post.select("._5pcq")[0].text.encode("big5")[-4:])
            else:
                year = int(first_post.select("._5pcp")[0].text.encode("big5")[-4:])
        except:
            year = 2018

        if year < 2017:
            print "NO DATA"
            continue

        # 第一篇po文大於2017
        # 滑到網頁最底
        while True:
            try:
        	    driver.find_element_by_id("ariaPoliteAlert")
        	    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            except:
        	    break

        # 所有有團購和面交兩個關鍵詞的貼文
        soup = BeautifulSoup(driver.page_source, "html.parser")
    	posts = soup.select("." + post_class)
    
        # 抓取每篇po文
        for post in posts:        
            # 確認po文的年份是否小大於2017
            try:
                if len(post.select("._5pcq")) != 0:
                    year = int(post.select("._5pcq")[0].text.encode("big5")[-4:])
                else:
                    year = int(post.select("._5pcp")[0].text.encode("big5")[-4:])
            except:
                year = 2018
            print year

            if year < 2017:
                print "此社團結束".decode("utf-8").encode("big5")
                break
        
            # 該團購貼文網址
            post_link = "https://www.facebook.com" + post.select("._5pcp")[0].select("a")[1]["href"]
            
            # 團購主臉書名稱與網址
            poster = post.select("a")[1]
            # print poster
            # 團購主臉書名稱
            poster_name = poster.text.encode("big5", "ignore")
            if poster_name in poster_name_set:
                continue
            # print poster_name
            poster_name_set.add(poster_name)
        
            # 團購主臉書網址
            poster_fb = poster["href"]
            # print poster_fb
        
            data.append([place.decode("utf-8").encode("big5"), poster_name, poster_fb, post_link])

    return driver, data



def save_file(data, place):
    # 存檔
    with open(os.getcwd() + "\\data\\" + place + ".csv", "wb") as f:
        w = csv.writer(f)
        w.writerows(data)



def main():

    # user login information 
    print "登入臉書以開始爬取團購社團資訊......".decode("utf-8").encode("big5")
    usr = raw_input("請輸入帳號:".decode("utf-8").encode("big5"))
    pwd = getpass.getpass("password:")
    # 地區關鍵字
    places = raw_input("請輸入要搜尋的團購地區(若輸入多筆請以','分隔):".decode("utf-8").encode("big5")).split(",")

    # 打開瀏覽器
    driver = open_browser()
    # Login
    driver = login(driver, usr, pwd)
    time.sleep(3)

    # 獲得登入帳號po文人的資料class
    post_class = get_post_class(driver)
    print post_class
    
    # 抓取地區關鍵字社團連結
    for place in places:
        # 資料欄位名
        data = []
        data.append(["地區".decode("utf-8").encode("big5"), "團購主".decode("utf-8").encode("big5"), "FB".decode("utf-8").encode("big5"), "網址".decode("utf-8").encode("big5")])
   
        print place
        driver, data = get_fb_group(driver, place.decode("big5").encode("utf-8"), data, post_class)
        save_file(data, place)
        
        # 每爬完一個地區休息兩分鐘
        if len(places) != 1 and place != places[len(places)-1]:
            print "休息一下......".decode("utf-8").encode("big5")
            time.sleep(120)

    # 關閉瀏覽器
    driver.close()

    print "抓取完成!".decode("utf-8").encode("big5")
    

def combine_files():
    '''合併各地區的資料，並刪除重複，最後產出 facebook.csv
    '''
    
    # 將資料儲存成 dictionary
    file_data = {}
    # 最後要存進facebook.csv的資料
    data = []
    data.append(["地區".decode("utf-8").encode("big5"), "團購主".decode("utf-8").encode("big5"), "FB".decode("utf-8").encode("big5"), "網址".decode("utf-8").encode("big5")])
    
    # 讀取所有csv檔
    files = os.listdir(os.getcwd() + "\\data\\")
    for file in files:
        with open(os.getcwd() + "\\data\\" + file, "r") as f:
            reader = csv.reader(f, delimiter = ',')
            # skip 第一列
            for i in range(1):
                next(reader, None)

            for row in reader:
                file_data[row[1]] = [row[0], row[1], row[2], row[3]]
    
    # 依地區抓出資料，並塞進data
    for area in files:
        area = area.replace(".csv", "")
        for i in file_data.keys():
            if file_data[i][0] == area:
                data.append(file_data[i])
    
    # 存檔
    with open("facebook.csv", "wb") as f:
        w = csv.writer(f)
        w.writerows(data)




if __name__ == "__main__":
    
    while True:
        
        while True:
            print "請選擇要使用的功能:(1) 合併資料 (2) 爬取社團資料 (3) 關閉程式".decode("utf-8").encode("big5")
            ans = input("請選擇:".decode("utf-8").encode("big5"))
            print
        
            if ans == 1 or ans == 2 or ans == 3:
                break
        
            print "只能選擇(1)或(2)或(3)......請重新輸入".decode("utf-8").encode("big5")

        if ans == 1:
            combine_files()
            print "合併完成!".decode("utf-8").encode("big5")
            # input()
       
        if ans == 2:
            main()

        if ans == 3:
            break 
