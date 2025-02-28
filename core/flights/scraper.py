from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from django.shortcuts import render
from flights.models import Flight
import os
import time

def setup_driver():
    """Initialize and configure the Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # اجرای در پس‌زمینه
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--window-size=1920,1080")  # تنظیم رزولوشن
    options.add_argument("--disable-blink-features=AutomationControlled")  # جلوگیری از شناسایی هدلس
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # User-Agent واقعی
    
    
    
    return webdriver.Chrome(options=options)


def select_location(driver, label_text, city_name):
    """انتخاب شهر در کادر جستجو بر اساس متن label."""
    label =WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{label_text}')]"))
    )
    input_id = label.get_attribute("for")  # گرفتن id فیلد ورودی
    search_box = driver.find_element(By.ID, input_id)
    
    search_box.clear()
    search_box.send_keys(city_name)
    time.sleep(1)

    first_option =WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'font-medium')]"))
    )
    first_option[0].click()

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def select_date(driver, day, month):
    """تابع کمکی برای انتخاب تاریخ در مرورگر با استفاده از Selenium."""
    try:
        # یافتن همه‌ی تقویم‌های موجود
        calendar_divs = driver.find_elements(By.XPATH, "//div[@class='calendar is-jalali']")
        
        target_calendar = None
        
        # پیدا کردن تقویم مربوط به ماه موردنظر
        for calendar in calendar_divs:
            month_text = calendar.find_element(By.TAG_NAME, "h5").text.strip()
            if month_text == month:
                target_calendar = calendar
                break

        if target_calendar is None:
            print("❌ ماه موردنظر پیدا نشد!")
            return 

        # XPathهای مختلف برای روزها
        day_xpaths = [
            f".//span[@class='calendar-cell']/span[normalize-space(text()) = '{int(day)}']",
            f".//span[@class='calendar-cell is-holiday']/span[normalize-space(text()) = '{int(day)}']",
            f".//span[@class='calendar-cell is-first is-holiday']/span[normalize-space(text()) = '{int(day)}']"
        ]
        
        date_element = None

        # بررسی هر XPath برای یافتن عنصر موردنظر
        for xpath in day_xpaths:
            try:
                date_element = WebDriverWait(target_calendar, 2).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                break  # اگر پیدا شد، از حلقه خارج شود
            except:
                continue  # اگر پیدا نشد، بقیه‌ی XPathها بررسی شوند
        
        if date_element is None:
            print(f"❌ عنصر روز {day} در تقویم پیدا نشد!")
            return
        
        print(f"✅ عنصر روز {day} پیدا شد!")
        
        # انتخاب تاریخ
        driver.execute_script("arguments[0].classList.add('is-selected');", date_element)
        date_element.click()
        
        print("✅ تاریخ با موفقیت انتخاب شد!")

    except Exception as e:
        print(f"❌ خطا در انتخاب تاریخ: {e}")


def click_button(driver, by, value):
    """Clicks a button identified by the given locator."""
    button =WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((by, value))
    )
    button.click()

def get_flight_results(driver):
    """Retrieves flight search results."""
    try:
        results =WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "available-card__content"))
        )
    except TimeoutException:
        return ["پروازی در این تاریخ وجود ندارد."]

    return [result.text.strip() for result in results] if results else ["پروازی در این تاریخ وجود ندارد."]

# def save_to_html(flight_data, day, month, inp_start, inp_end):
#     """Saves flight results to an HTML file and opens it in a browser."""

#     return  {
#         "flights": flight_data,
#         "day": day,
#         "month": month,
#         "inp_start": inp_start,
#         "inp_end": inp_end,
#     }
     


def save_to_database(data):
    """ذخیره اطلاعات پرواز در دیتابیس Django"""
    flight_list = []
    for flight in data:
        flight_list2 = Flight.objects.create(details=flight)
        flight_list.append(flight_list2)
