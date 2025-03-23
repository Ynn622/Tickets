from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import undetected_chromedriver as uc
import time
import certifi
import os
os.environ["SSL_CERT_FILE"] = certifi.where()    # uc.Chrome() 需要

""" 輸入資訊階段 """
# input: 搶票連結/選擇天數/選擇座位/購買張數
url = input("輸入「搶票連結」：")                # https://tixcraft.com/activity/detail/25_xalive
choose_times = int(input("輸入「第x天」："))    # 1
choose_seat = input("輸入「座位」：")           # 綠214
ticket_num = input("輸入「張數」：")            # 1

# Chrome設定
driver_op = uc.ChromeOptions()
driver_op.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver_op.add_argument("--disable-blink-features=AutomationControlled")  # 隱藏 Selenium 特徵
driver_op.add_argument("--start-maximized")   # 全螢幕

# Chrome瀏覽器
driver = uc.Chrome(options=driver_op)   # 開啟 Chrome
driver.get(url)                     # 進入網頁
waiter = WebDriverWait(driver, 15)  # 元素等待器：最多等 15 秒

""" 等待登入 """
login = input("請登入完成後，要搶票時在此按下 Enter：")

""" 進入搶票頁面 """
print("Execute: 進入搶票頁面")
driver.get(url)     # 再次進入網頁
driver.execute_script(f"window.scrollTo(0,400)")  # 向下滑動到購票
time.sleep(0.3)

''' 開始搶票 '''
# 關閉下方cookie提示框
try:
    driver.find_element(By.ID,"onetrust-accept-btn-handler").click()
except:
    print("-無cookie提示框")
    pass

# 按下「立即購票」
table = waiter.until(EC.presence_of_element_located((By.CLASS_NAME,"buy")))  # 等待元素出現在 HTML 裡
buy = driver.find_element(By.CLASS_NAME,"buy")
buy.click()
print("Execute: 按下「立即購票」")

# 關閉下方cookie提示框
try:
    time.sleep(0.2)
    driver.find_element(By.ID,"onetrust-accept-btn-handler").click()
except:
    print("-無cookie提示框")
    pass

print("Execute: 選取演出場次")
# 找出時間表格 id=gameList (會等待元素出現在 HTML 裡)
table = waiter.until(EC.presence_of_element_located((By.ID,"gameList")))
tr = driver.find_elements(By.TAG_NAME,"tr")   # 所有<tr>：表演時間
for i in tr:
    # print(i.text)  # 表演時間
    pass
print()

# 找出「訂票」button (會等待元素出現在 HTML 裡)
element = waiter.until(EC.presence_of_element_located((By.TAG_NAME, "td")))
time.sleep(0.5)
order = tr[choose_times].find_elements(By.TAG_NAME,"td")[3].find_element(By.TAG_NAME,"button")  # 找出場次的按鈕
order.click()  # 按下「立即訂購」

''' 進入 選位頁面 '''
print("Execute: Page-選位")
# 找出可買欄位
all_area = driver.find_elements(By.CLASS_NAME,"area-list")[1:]   # 所有座位
while True:
    try:
        find = False  # 是否找到
        for i in all_area:
            row = i.find_elements(By.TAG_NAME,"li")    # 所有行
            for j in row: 
                # print(j.text)  # 顯示目前的行
                if choose_seat in j.text:
                    driver.execute_script(f"window.scrollTo(0,{j.location['y']-400})")  # 滑動到該座位
                    time.sleep(0.5)
                    j.find_element(By.TAG_NAME,"a").click()   # 點擊該座位
                    find = True
                    break
            if find:
                break
        else:
            raise Exception("No Seat!")
        break
    except:
        choose_seat = input("找不到該座位，請重新輸入：")
        pass

print("Execute: Page-選票數")
''' 進入 選數量頁面 '''

# 找出「下拉式選單」
selected = Select(driver.find_element(By.TAG_NAME,"select"))
selected.select_by_value(ticket_num)
print(f"Execute: 輸入-{ticket_num}張票")

# 找出「同意鈕」
agree = driver.find_element(By.ID, "TicketForm_agree")
agree.click()
print("Execute: 按下「同意鈕」")

# 自行輸入驗證碼！
TicketForm_verifyCode = driver.find_element(By.ID, "TicketForm_verifyCode")
TicketForm_verifyCode.click()
print("Successed: 自動化步驟結束 請自行輸入「驗證碼」！")

time.sleep(300)
