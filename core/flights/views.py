from django.shortcuts import render
from django.http import JsonResponse
from flights.scraper import *
from selenium.webdriver.common.by import By
from django.views import View
import time

# Initialize the Chrome WebDriver using the WebDriverManager library
webdriver_manager = WebDriverManager(headless=True) 


def base(request):
    return render(request, "base.html")
def index(request):
    error_message = request.session.pop("error_message", None)
    return render(request, "index.html", {"error_message": error_message})

class SearchFlightsView(View):
    template_name = "index.html"

    def post(self, request):
        data = request.POST
        inp_start = data.get("start")
        inp_end = data.get("end")
        day = data.get("day")
        month = data.get("month")

        if not inp_start or not inp_end:
            return JsonResponse({"error": "مبدا و مقصد باید مشخص شوند."}, status=400)

        driver = webdriver_manager.start_driver()
        if not driver:
            return JsonResponse({"error": "مشکل در راه‌اندازی مرورگر، لطفاً بررسی کنید."}, status=500)

        bot = FlightScraper(driver)
        try:
            bot.open_website("https://www.alibaba.ir/")
            bot.select_location("مبدا (شهر)", inp_start)
            bot.select_location("مقصد (شهر)", inp_end)
            bot.select_date(day, month)
            bot.click_button(By.CLASS_NAME, "btn.is-nl.is-solid-secondary.px-6")
            time.sleep(2)
            bot.click_button(By.XPATH, "//button[contains(text(),'جستجو')]")
            flight_data = bot.get_flight_results()
        finally:
            webdriver_manager.quit_driver()

        context = {
            "flights": flight_data,
            "day": day,
            "month": month,
            "inp_start": inp_start,
            "inp_end": inp_end,
        }
        bot.save_to_database(flight_data)
        return render(request, 'result/flights.html', context)

