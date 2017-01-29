from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinLengthValidator,  MaxLengthValidator

class University(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Student(models.Model):
    YEAR_IN_SCHOOL_CHOICES = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
    )
    year_in_school = models.CharField(max_length=2, choices=YEAR_IN_SCHOOL_CHOICES)
    age = models.SmallIntegerField(validators=[MinLengthValidator(1),, MaxLengthValidator(100)])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # relationships models
    university = models.ForeignKey(University, null=True, blank=True)
    courses = models.ManyToManyField(Course, null=True, blank=True)



