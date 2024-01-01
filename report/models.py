from django.db import models
from django.utils import timezone

class ReportEntry(models.Model):
    machine_number = models.CharField(max_length=100)
    part_number = models.CharField(max_length=100)
    part_description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.machine_number},{self.part_number},{self.quantity}'
    

    @classmethod
    def entries_by_day(cls, day):
        start_time = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
        end_time = start_time + timezone.timedelta(days=1)
        return cls.objects.filter(date_added__range=(start_time, end_time))