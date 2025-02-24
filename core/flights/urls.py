from django.urls import path
from flights.views import *
from flights.scraper import *

app_name = "flight"
urlpatterns = [
    path('', index, name='index'),
    path("search/", search_flights, name="search_flights"),
    

]
