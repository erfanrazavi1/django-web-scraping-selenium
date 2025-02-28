from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from django.shortcuts import render
from flights.models import Flight
import os
import time


class WebDriverManager:
    """ The manager for webdriver """
    
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless")  
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # جلوگیری از شناسایی هدلس
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )  # real user agent
        self.driver = None

    def start_driver(self):
        
        if not self.driver:
            self.driver = webdriver.Chrome(options=self.options)
        return self.driver

    def quit_driver(self):
        
        if self.driver:
            self.driver.quit()
            self.driver = None  


class FlightScraper:
    """Handles flight search operations using Selenium."""
    
    def __init__(self, driver):
        self.driver = driver  # Store the WebDriver instance

    def open_website(self, url):
        """Opens the specified website."""
        self.driver.get(url)
    
    def select_location(self, label_text, city_name):
        """Select a city in the search box based on the given label text."""
        label = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{label_text}')]"))
        )
        input_id = label.get_attribute("for")  # Get the ID of the input field
        search_box = self.driver.find_element(By.ID, input_id)
        
        search_box.clear()
        search_box.send_keys(city_name)
        time.sleep(1)

        first_option = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'font-medium')]"))
        )
        first_option[0].click()

    def select_date(self, day, month):
        """Select a date from the calendar based on the provided day and month."""
        try:
            # Find all available calendars
            calendar_divs = self.driver.find_elements(By.XPATH, "//div[@class='calendar is-jalali']")
            
            target_calendar = None
            
            # Find the correct calendar matching the given month
            for calendar in calendar_divs:
                month_text = calendar.find_element(By.TAG_NAME, "h5").text.strip()
                if month_text == month:
                    target_calendar = calendar
                    break

            if target_calendar is None:
                print("❌ Month not found!")
                return 

            # Different XPath patterns for selecting the date
            day_xpaths = [
                f".//span[@class='calendar-cell']/span[normalize-space(text()) = '{int(day)}']",
                f".//span[@class='calendar-cell is-holiday']/span[normalize-space(text()) = '{int(day)}']",
                f".//span[@class='calendar-cell is-first is-holiday']/span[normalize-space(text()) = '{int(day)}']"
            ]
            
            date_element = None

            # Iterate through XPath patterns to find the correct element
            for xpath in day_xpaths:
                try:
                    date_element = WebDriverWait(target_calendar, 2).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    break  # Exit loop if found
                except:
                    continue  # Try next XPath pattern
            
            if date_element is None:
                print(f"❌ Date {day} not found in calendar!")
                return
            
            print(f"✅ Date {day} found!")

            # Select the date
            self.driver.execute_script("arguments[0].classList.add('is-selected');", date_element)
            date_element.click()
            
            print("✅ Date successfully selected!")

        except Exception as e:
            print(f"❌ Error selecting date: {e}")

    def click_button(self, by, value):
        """Click a button identified by the given locator."""
        button = WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((by, value))
        )
        button.click()

    def get_flight_results(self):
        """Retrieve flight search results."""
        try:
            results = WebDriverWait(self.driver, 2).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "available-card__content"))
            )
        except TimeoutException:
            return ["هیچ پروازی در این تاریخ یافت نشد"]

        return [result.text.strip() for result in results] if results else ["هیچ پروزاری در این تاریخ یافت نشد"]

    def save_to_database(self, data):
        """Save flight details to the Django database."""
        flight_list = []
        for flight in data:
            flight_entry = Flight.objects.create(details=flight)
            flight_list.append(flight_entry)
