from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

# 设置Chrome WebDriver路径
service = Service('/Users/jessica/Downloads/chromedriver')

# 初始化WebDriver
driver = webdriver.Chrome(service=service)

# 读取二级分类数据
df_categories = pd.read_csv('categories.csv')

# 初始化一个列表来存储所有商品数据
all_data = []

# 爬取每一个二级分类的URL
for index, row in df_categories.iterrows():
    primary_name = row['一级分类']
    secondary_name = row['二级分类']
    secondary_url = row['二级分类URL']

    # 打开二级分类的URL
    driver.get(secondary_url)

    try:
        # 等待页面完全加载
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.item')))

        # 尝试获取总页数
        try:
            total_pages_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#ctl00_Content_lblPage'))
            )
            total_pages_text = total_pages_element.text

            # 使用正则表达式提取总页数
            match = re.search(r'/\s*(\d+)\s*页', total_pages_text)
            if match:
                total_pages = int(match.group(1))
            else:
                raise ValueError("无法提取总页数")
        except Exception as e:
            # 如果没有找到分页元素，则认为只有一页
            print(f"未找到分页元素，可能只有一页数据: {e}")
            total_pages = 1

        # 循环遍历每一页
        for page in range(total_pages):
            # 获取当前页面的内容
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')

            # 查找所有商品的<li>标签
            product_items = soup.find_all('li', class_='item')

            for product in product_items:
                # 获取商品链接
                link_tag = product.find('a', href=True)
                product_url = link_tag['href'] if link_tag else None

                # 获取商品名称
                h3_tag = product.find('h3')
                name_tag = h3_tag.find('a') if h3_tag else None
                product_name = name_tag.text.strip() if name_tag else None

                # 获取商店名称
                mall_tag = product.find('span', class_='mall')
                mall_name = mall_tag.text.strip() if mall_tag else None

                # 将数据添加到列表
                all_data.append([primary_name, secondary_name, product_url, product_name, mall_name])

            # 尝试找到并点击“下一页”按钮
            if total_pages > 1:
                try:
                    next_button = driver.find_element(By.ID, 'nextPage')
                    next_button.click()
                    # 等待页面加载
                    time.sleep(3)
                except Exception as e:
                    print(f"到达最后一页或找不到'下一页'按钮: {e}")
                    break  # 没有更多的页面或找不到'下一页'按钮

    except Exception as e:
        print(f"在处理URL时出错: {secondary_url}, 错误信息: {e}")
        continue  # 继续处理下一个URL

# 关闭WebDriver
driver.quit()

# 将所有数据保存到一个CSV文件
df = pd.DataFrame(all_data, columns=['一级分类', '二级分类', '商品URL', '商品名称', '商店名称'])
df.to_csv('all_products.csv', index=False, encoding='utf-8')
print("所有数据已保存到 all_products.csv")
