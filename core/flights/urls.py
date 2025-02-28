from django.urls import path
from flights.views import *
from flights.scraper import *

app_name = "flight"
urlpatterns = [
    path('', base, name='base'),
    path('fly/', index, name='index'),
    path("search/", SearchFlightsView.as_view(), name="search_flights"),
    

]
