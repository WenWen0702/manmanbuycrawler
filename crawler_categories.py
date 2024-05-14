from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re

# 设置Chrome WebDriver路径
service = Service('/Users/jessica/Downloads/chromedriver')

# 初始化WebDriver
driver = webdriver.Chrome(service=service)

# 目标网页URL
url = 'https://www.manmanbuy.com/'  # 更新为你实际的目标URL

# 打开网页
driver.get(url)

# 等待页面完全加载
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.fl.l-side')))

# 获取页面内容
page_content = driver.page_source

# 使用BeautifulSoup解析网页内容
soup = BeautifulSoup(page_content, 'html.parser')

# 初始化一个列表来存储数据
categories_data = []

# 查找所有一级分类的<li>标签
primary_categories = soup.select('div.sub-nav ul li')

for primary_category in primary_categories:
    primary_name_tag = primary_category.find('a')
    # 删除所有的<i>标签
    for i_tag in primary_name_tag.find_all('i'):
        i_tag.decompose()
    # 获取纯文本
    primary_name = primary_name_tag.get_text(strip=True)
    primary_url = primary_name_tag['href']
    
    # 查找二级分类
    secondary_categories = primary_category.select('div.bd dl dd a')
    for secondary_category in secondary_categories:
        # 删除所有的<i>标签
        for i_tag in secondary_category.find_all('i'):
            i_tag.decompose()
        # 获取纯文本
        secondary_name = secondary_category.get_text(strip=True)
        secondary_url = secondary_category['href']
        categories_data.append([primary_name, primary_url, secondary_name, secondary_url])

# 关闭WebDriver
driver.quit()

# 将数据保存到CSV文件
df = pd.DataFrame(categories_data, columns=['一级分类', '一级分类URL', '二级分类', '二级分类URL'])
df.to_csv('categories.csv', index=False, encoding='utf-8')

print("数据已保存到categories.csv")
