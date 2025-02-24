from django.contrib import admin
from flights.models import Flight

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'details', 'created_at')  
    search_fields = ('details',)  
    list_filter = ('created_at',) 
