# Facebook group poster's information crawler

**環境: Win7/ Python 2.7.14**

#==================================== 

使用 selenium 爬取 facebook 特定關鍵字搜尋結果的公開社團，<br>
並設定篩選條件，爬取

* po文臉書名稱
* po文臉書網址
* po文內容網址

#====================================


執行程式前須 install selenium 與下載 chrome webdriver

1. 下載 selenium <br>
`pip install selenium`

2. 下載 chrome webdriver <br>
[下載](http://chromedriver.chromium.org/downloads) 
解壓縮執行後將檔案移到特定資料夾（使用者自行決定），<br>
之後在啟動 webdriver（`webdriver.Chrome(路徑)`）時會需要這個路徑。
