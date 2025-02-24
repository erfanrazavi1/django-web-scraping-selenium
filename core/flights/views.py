from django.shortcuts import render
from django.http import JsonResponse
from flights.scraper import *
from selenium.webdriver.common.by import By
import time


def index(request):
    error_message = request.session.pop("error_message", None)
    return render(request, "index.html", {"error_message": error_message})

def search_flights(request):
    if request.method == "POST":
        data = request.POST
        inp_start = data.get("start")
        inp_end = data.get("end")
        day = data.get("day")
        month = data.get("month")

        if not inp_start or not inp_end:
            return JsonResponse({"error": "مبدا و مقصد باید مشخص شوند."}, status=400)

        driver = setup_driver()
        try:
            driver.get("https://www.alibaba.ir/")
            select_location(driver, "مبدا (شهر)", inp_start)
            select_location(driver, "مقصد (شهر)", inp_end)
            select_date(driver,day,month)  # انتخاب تاریخ به‌صورت دستی
            click_button(driver, By.CLASS_NAME, "btn.is-nl.is-solid-secondary.px-6")
            time.sleep(2)
            click_button(driver, By.XPATH, "//button[contains(text(),'جستجو')]")
            flight_data = get_flight_results(driver)
        finally:
            driver.quit()
            file_path = save_to_html(flight_data)
            # flight_data_list = {'detail': flight_data}
            
            save_to_database(flight_data)
            return render(request, 'flights.html', {
                "message": "جستجو با موفقیت انجام شد",
                "data": flight_data,
                "html_file": file_path
            })


        # save_to_html(flight_data)
        

    return JsonResponse({"error": "درخواست نامعتبر است."}, status=400)