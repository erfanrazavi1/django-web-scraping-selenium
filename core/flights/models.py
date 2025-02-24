from django.db import models



class Flight(models.Model):
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.details[:50]  # نمایش ۵۰ کاراکتر اول برای خلاصه
