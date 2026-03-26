from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import certifi
import os

os.environ["SSL_CERT_FILE"] = certifi.where()  # uc.Chrome() 需要


def get_user_input():
    """獲取使用者輸入的搶票資訊"""
    print("\n======= 拓元搶票輔助神器 =======")
    url = input("[Input] 輸入「搶票連結」：")
    choose_times = int(input("[Input] 輸入「第x天」："))
    choose_seat = input("[Input] 輸入「座位」：")
    ticket_num = input("[Input] 輸入「張數」：")
    return url, choose_times, choose_seat, ticket_num


def setup_driver():
    """設定並啟動 Chrome 瀏覽器"""
    driver_op = uc.ChromeOptions()
    driver_op.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver_op.add_argument("--disable-blink-features=AutomationControlled")
    driver_op.add_argument("--start-maximized")
    
    print("\n[Execute] 開啟模擬瀏覽器Chrome")
    driver = uc.Chrome(options=driver_op)
    return driver


def close_cookie_banner(driver):
    """關閉 cookie 提示框（如果存在）"""
    try:
        wait = WebDriverWait(driver, 3)
        cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        cookie_btn.click()
        print("[Execute] 關閉 cookie 提示框")
    except TimeoutException:
        print("[Warning] 無cookie提示框")
    except Exception as e:
        print(f"[Warning] 關閉 cookie 提示框時發生錯誤: \n{type(e).__name__}")


def wait_for_login(driver, url):
    """等待使用者登入"""
    driver.get(url)
    input("\n[Input] 請登入完成後，要搶票時在此按下 Enter：")


def scroll_to_element(driver, element):
    """滾動到指定元素位置"""
    y_position = element.location['y'] - 400
    driver.execute_script(f"window.scrollTo(0, {y_position})")


def click_buy_button(driver):
    """點擊「立即購票」按鈕"""
    print("\n[Execute] 進入搶票頁面")
    
    # 等待購買按鈕出現並可點擊
    wait = WebDriverWait(driver, 15)
    try:
        buy_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "buy")))
        
        # 滾動到按鈕位置
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buy_button)
        
        # 等待按鈕完全可見
        wait.until(EC.visibility_of(buy_button))
        
        buy_button.click()
        print("[Execute] 按下「立即購票」")
    except TimeoutException:
        print("[Error] 無法找到「立即購票」按鈕，請確認連結是否正確！")
        raise
    
    # 再次嘗試關閉 cookie（可能在新頁面再次出現）
    close_cookie_banner(driver)


def select_show_time(driver, choose_times):
    """選擇演出場次"""
    print("\n[Execute] 選取演出場次")
    wait = WebDriverWait(driver, 15)
    
    try:
        # 等待時間表格出現
        wait.until(EC.presence_of_element_located((By.ID, "gameList")))
        
        # 等待 td 元素出現（確保表格已完全載入）
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "td")))
        
        # 找出所有場次
        tr_elements = driver.find_elements(By.TAG_NAME, "tr")
        
        if choose_times >= len(tr_elements):
            raise IndexError(f"場次索引 {choose_times} 超出範圍，總共只有 {len(tr_elements)} 個場次")
        
        # 找出指定場次的「立即訂購」按鈕
        target_row = tr_elements[choose_times]
        td_elements = target_row.find_elements(By.TAG_NAME, "td")
        
        if len(td_elements) <= 3:
            raise NoSuchElementException(f"場次 {choose_times} 的 td 元素數量不足")
        
        # 等待按鈕可點擊
        order_button = wait.until(EC.element_to_be_clickable(td_elements[3].find_element(By.TAG_NAME, "button")))
        order_button.click()
        print(f"[Execute] 已選擇第 {choose_times} 天的場次")
        
    except TimeoutException:
        print("[Error] 等待時間表格超時，請確認連結是否正確！")
        input("[Input] 請手動點擊「立即訂購」後，在此處按下 Enter：")
    except (IndexError, NoSuchElementException) as e:
        print(f"[Error] {str(e)}")
        input("[Input] 請手動點擊「立即訂購」後，在此處按下 Enter：")
    except Exception as e:
        print(f"[Error] 選擇場次時發生未預期錯誤: \n{type(e).__name__} - {str(e)}")
        input("[Input] 請手動點擊「立即訂購」後，在此處按下 Enter：")


def select_seat(driver, choose_seat):
    """選擇座位"""
    print("\n[Page]「選位」頁面")
    wait = WebDriverWait(driver, 10)
    
    while True:
        try:
            # 等待座位列表載入
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "area-list")))
            
            all_area = driver.find_elements(By.CLASS_NAME, "area-list")[1:]
            
            if not all_area:
                raise NoSuchElementException("找不到座位區域列表")
            
            seat_found = False
            
            for area in all_area:
                rows = area.find_elements(By.TAG_NAME, "li")
                
                for seat_element in rows:
                    if choose_seat in seat_element.text:
                        # 檢查座位是否可選
                        if seat_element.get_attribute("class") == "":
                            print(f"[Error] 該座位已售完：{seat_element.text}")
                            raise ValueError(f"座位 {choose_seat} 已售完")
                        
                        # 滾動到座位位置
                        scroll_to_element(driver, seat_element)
                        
                        # 等待座位連結可點擊
                        seat_link = wait.until(EC.element_to_be_clickable(seat_element.find_element(By.TAG_NAME, "a")))
                        seat_link.click()
                        
                        print(f"[Execute] 已選擇座位 - {choose_seat}")
                        seat_found = True
                        break
                
                if seat_found:
                    break
            
            if not seat_found:
                raise NoSuchElementException(f"未找到座位：{choose_seat}")
            
            break  # 成功選擇座位，跳出迴圈
            
        except (ValueError, NoSuchElementException) as e:
            print(f"[Error] {str(e)}")
            choose_seat = input("[Input] 請重新輸入座位：")
        except TimeoutException:
            print("[Error] 等待座位元素超時")
            choose_seat = input("[Input] 請重新輸入座位：")
        except Exception as e:
            print(f"[Error] 選擇座位時發生未預期錯誤: {type(e).__name__} - {str(e)}")
            choose_seat = input("[Input] 請重新輸入座位：")


def select_ticket_count(driver, ticket_num):
    """選擇票數並同意條款"""
    print("\n[Page]「選取票數」頁面")
    wait = WebDriverWait(driver, 10)
    
    try:
        # 等待下拉選單出現
        select_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
        selected = Select(select_element)
        selected.select_by_value(ticket_num)
        print(f"[Execute] 輸入 {ticket_num} 張票")
        
        # 等待同意按鈕可點擊
        agree_checkbox = wait.until(EC.element_to_be_clickable((By.ID, "TicketForm_agree")))
        agree_checkbox.click()
        print(f"[Execute] 按下「同意鈕」")
        
    except TimeoutException:
        print("[Error] 等待票數選單或同意按鈕超時")
        raise
    except Exception as e:
        print(f"[Error] 選擇票數時發生錯誤: \n{type(e).__name__} - {str(e)}")
        raise


def wait_for_verification(driver):
    """等待使用者輸入驗證碼"""
    wait = WebDriverWait(driver, 10)
    
    try:
        # 等待驗證碼輸入框可點擊
        verify_code_input = wait.until(EC.element_to_be_clickable((By.ID, "TicketForm_verifyCode")))
        verify_code_input.click()
        
        print("\n" + "="*60)
        print("[Success] 自動化步驟結束 請自行輸入「驗證碼」！")
        print("="*60)
        print("[Tips]:")
        print("1. 請完成驗證碼輸入和訂票流程")
        print("2. 訂票完成後，請「關閉瀏覽器視窗」即可結束程式")
        print("3. 或直接按 Ctrl+C 中斷程式")
        print("4. 感謝您的使用！")
        print("="*60)
        
        print("\n等待中... (關閉瀏覽器視窗即可結束程式)")
        
        while True:
            try:
                driver.current_url
                wait.until(lambda d: False)
            except TimeoutException:
                continue
            except Exception:
                print("\n偵測到瀏覽器已關閉")
                break
            
    except TimeoutException:
        print("[Error] 找不到驗證碼輸入框")
        raise
    except Exception as e:
        print(f"[Error] 處理驗證碼時發生錯誤: \n{type(e).__name__} - {str(e)}")
        raise


def main():
    """主程式流程"""
    driver = None
    
    try:
        # 1. 獲取使用者輸入
        url, choose_times, choose_seat, ticket_num = get_user_input()
        
        # 2. 設定瀏覽器
        driver = setup_driver()
        
        # 3. 等待登入
        wait_for_login(driver, url)
        
        # 4. 進入搶票頁面
        driver.get(url)
        close_cookie_banner(driver)
        
        # 5. 點擊「立即購票」
        click_buy_button(driver)
        
        # 6. 選擇場次
        select_show_time(driver, choose_times)
        
        # 7. 選擇座位
        select_seat(driver, choose_seat)
        
        # 8. 選擇票數
        select_ticket_count(driver, ticket_num)
        
        # 9. 等待驗證碼輸入
        wait_for_verification(driver)
        
    except KeyboardInterrupt:
        print("\n\n[Stop] 使用者中斷程式")
    except Exception as e:
        print(f"\n\n[Error] 程式執行時發生嚴重錯誤: \n{type(e).__name__} - {str(e)}")
    finally:
        if driver:
            driver.quit()
            print("\n[Success] 瀏覽器已關閉")


if __name__ == "__main__":
    main()