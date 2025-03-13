from django.db import models


class AssignTable(models.Model):
    group = models.CharField(max_length=50)
    category = models.CharField(max_length=20)
    lecturer = models.CharField(max_length=255)
    assigned_room = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20)
    group_capacity = models.PositiveIntegerField()
    room_capacity = models.PositiveIntegerField()
    assigned_day = models.CharField(max_length=10)
    assigned_time_slot = models.CharField(max_length=20)

    LECTURE_CHOICES = [('Y', 'Yes'), ('N', 'No')]
    lecture = models.CharField(max_length=1, choices=LECTURE_CHOICES, default='N')
    tutorial = models.CharField(max_length=1, choices=LECTURE_CHOICES, default='N')
    lab = models.CharField(max_length=1, choices=LECTURE_CHOICES, default='N')

    duration = models.PositiveIntegerField()  # 분 단위 강의 시간

    def __str__(self):
        return f"{self.group} - {self.lecturer} ({self.assigned_day} {self.assigned_time_slot})"
