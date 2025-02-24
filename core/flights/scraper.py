from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flights.models import Flight
import os
import time

def setup_driver():
    """Initialize and configure the Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # اجرای در پس‌زمینه
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

    first_option =WebDriverWait(driver, 2).until(
        EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'font-medium')]"))
    )
    first_option[0].click()

def select_date(driver,day,month):
    """تابع کمکی برای انتخاب تاریخ در مرورگر با استفاده از Selenium."""
    try:
       
        calendar_divs = driver.find_elements(By.XPATH, "//div[@class='calendar is-jalali']")

        target_calendar = None

        
        for calendar in calendar_divs:
            month_text = calendar.find_element(By.TAG_NAME, "h5").text.strip()
            if month_text == month:
                target_calendar = calendar
                break
        
        if target_calendar is None:
            print("❌ ماه موردنظر پیدا نشد!")
            
            return 

        day_xpath = f".//span[@class='calendar-cell']/span[contains(text(), '{int(day)}')]"
        date_element = WebDriverWait(target_calendar, 5).until(
            EC.element_to_be_clickable((By.XPATH, day_xpath))
        )

        driver.execute_script("arguments[0].classList.add('is-selected');", date_element)
        date_element.click()

        print("✅ تاریخ با موفقیت انتخاب شد!")
        if month == "فروردین":
            try:
                is_pass_element = date_element.find_element(By.XPATH, "./span[@class='is-pass']")
                driver.execute_script("arguments[0].remove();", is_pass_element)
            except:
                print("✅ هیچ تگ is-pass برای حذف وجود نداشت.")

        # کلیک روی تاریخ موردنظر
        date_element.click()
        
        
    except Exception as e:
        print(f"Error selecting date: {e}")

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

def save_to_html(data):
    """Saves flight results to an HTML file and opens it in a browser."""
    os.makedirs("templates", exist_ok=True)
    html_template = """
    <!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flight Results</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');

        body {
            font-family: 'Vazirmatn', Arial, sans-serif;
            direction: rtl;
            text-align: right;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            padding: 20px;
            color: #fff;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            max-width: 800px;
            margin: auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: fadeIn 1s ease-in-out;
        }

        h2 {
            color: #fff;
            text-align: center;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .flight {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 12px;
            border-right: 6px solid #007bff;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        }

        .flight:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
        }

        .flight strong {
            color: #007bff;
        }

        .flight::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
            transform: skewX(-20deg);
            transition: left 0.5s ease-in-out;
        }

        .flight:hover::before {
            left: 100%;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* استایل دکمه بروزرسانی */
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            display: none; /* مخفی کردن دکمه */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease-in-out;
        }

        .refresh-btn:hover {
            background: #0056b3;
            transform: scale(1.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>نتایج پرواز</h2>
        {flights}
    </div>

    <!-- دکمه بروزرسانی -->
    <a href="{% url 'flight:base' %}" class="refresh-btn" id="refreshButton">برو به صفحه اصلی</a>

    <script>
        // نمایش دکمه بعد از 3 ثانیه
        setTimeout(function() {
            document.getElementById("refreshButton").style.display = "block";
        }, 3000);
    </script>
</body>
</html>


    """

    flights_html = "".join(f'<div class="flight">{flight}</div>' for flight in data)
    final_html = html_template.replace("{flights}", flights_html)

    with open("./core/templates/flights.html", "w", encoding="utf-8") as f:
        f.write(final_html)


def save_to_database(data):
    """ذخیره اطلاعات پرواز در دیتابیس Django"""
    flight_list = []
    for flight in data:
        flight_list2 = Flight.objects.create(details=flight)
        flight_list.append(flight_list2)
    
