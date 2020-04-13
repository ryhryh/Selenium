from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options

import pandas as pd
import smtplib
from email.mime.text import MIMEText
import time
from bs4 import BeautifulSoup

##########################################################################################

class Crawler591():
    def __init__(self):
        self.set_options()
        self.setup()
        
    def set_options(self):
        executable_path='/media/disk3/feynman52/dummy/crawler591/geckodriver'

        self.options = Options()
        self.options.headless = True

        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("dom.webnotifications.enabled", False)
        
        self.driver = webdriver.Firefox(
            executable_path=executable_path,
            options=self.options,
            firefox_profile=firefox_profile,
            log_path='/media/disk3/feynman52/dummy/crawler591/geckodriver.log'
        )


    def setup(self):
        print('setup...')
        
        # 進入591首頁
        self.driver.get("https://rent.591.com.tw")

        # 新北
        self.click('//*[@id="area-box-body"]/dl[1]/dd[2]')

        # 按鄉鎮選擇 
        self.click('//*[@id="search-location"]/span[2]')
        # 選擇區域
        for x in ['板橋','中和','永和','新店']:
            self.click("//*[contains(text(), '%s')]"%(x))

        # 格局
        self.click('//*[@id="search-pattern"]/span[7]')
        # 兩房
        self.click('//*[@id="search-pattern"]/label[2]')
        # 三房
        self.click('//*[@id="search-pattern"]/label[3]')

        # rentPrice-min
        self.send_keys('//*[@id="rentPrice-min"]',"1")
        # rentPrice-max
        self.send_keys('//*[@id="rentPrice-max"]',"25001")
        # 按確定
        self.click('//*[@id="search-price"]/sapn/input[3]')

        # 刊登時間排序
        self.click('//*[@id="container"]/section[5]/div/div[1]/div[3]/div[3]/div[2]')
        print('finish!!!')
        
    def update(self):
        print('update...')
        
        untrack_urls = self.get_untrack_urls()
        print(len(untrack_urls))
        
        if len(untrack_urls)>=0: 
            self.send_email(untrack_urls)
            self.df_all.to_csv('house.csv', index=False)
        self.driver.quit()
    
        print('finish!!!')
        
    def get_untrack_urls(self):
        path='/media/disk3/feynman52/dummy/crawler591/house.csv'
        df_old_fefore_update=pd.read_csv(path)
        df_old=df_old_fefore_update.copy()

        ######################################################################
        while True:
            old_urls=set(df_old.url)

            urls=self.get_urls()
            current_page_urls=set(urls)

            untrack_urls=current_page_urls-old_urls

            if len(untrack_urls)<=0: break

            # save untrack_urls
            df_untrack=pd.DataFrame()
            df_untrack['url']=list(untrack_urls)
            df_old=df_old.append(df_untrack)

            # load next page
            self.click("//*[contains(text(), '下一頁')]")
        ###################################################################### 
        self.df_all = df_old
        
        old_urls=set(df_old_fefore_update.url)
        all_urls=set(self.df_all.url)
        untrack_urls=all_urls-old_urls       
        return list(untrack_urls)
    
    def get_urls(self):
        page_source = self.driver.page_source  
        soup = BeautifulSoup(page_source, features="lxml")  
        content=soup.find('div', attrs={'id':'content'})
        
        urls=content.find_all('h3')
        urls=['https:'+url.find('a')['href'].replace(' ','') for url in urls]
        
        return urls
    
    def click(self, xpath):
        button = self.driver.find_element_by_xpath(xpath)
        button.click()
        time.sleep(2)

    def send_keys(self, xpath, key):
        button = self.driver.find_element_by_xpath(xpath)
        button.send_keys(key)
        time.sleep(2)
    
    def send_email(self, untrack_urls):
        email_content='\n'.join(untrack_urls)

        gmail_user = 'aaa@gmail.com' # sender
        gmail_password = 'xxxxxx' 
        recipients = ['bbb@gmail.com'] # reciever
        recipients = ", ".join(recipients)

        msg = MIMEText(email_content)
        msg['Subject'] = pd.to_datetime('today').strftime("%Y-%m-%d")
        msg['From'] = gmail_user
        msg['To'] = recipients

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()

        print('Email sent!')

##########################################################################################
if __name__ == '__main__':
    crawler591 = Crawler591()
    crawler591.update()




