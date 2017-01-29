from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinLengthValidator,  MaxLengthValidator
import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + (
    'es_index_name', 'es_type_name', 'es_mapping'
)
class University(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Student(models.Model):
    class Meta:
        es_index_name = 'django'
        es_type_name = 'student'
        es_mapping = {
            'properties': {
                'university': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'index': 'not_analyzed'},
                    }
                },
                'first_name': {'type': 'string', 'index': 'not_analyzed'},
                'last_name': {'type': 'string', 'index': 'not_analyzed'},
                'age': {'type': 'short'},
                'year_in_school': {'type': 'string'},
                'name_complete': {
                    'type': 'completion',
                    'analyzer': 'simple',
                    'payloads': True,
                    'preserve_separators': True,
                    'preserve_position_increments': True,
                    'max_input_length': 50,
                },
                "course_names": {
                    "type": "string", "store": "yes", "index": "not_analyzed",
                },
            }
        }
    YEAR_IN_SCHOOL_CHOICES = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
    )
    year_in_school = models.CharField(max_length=2, choices=YEAR_IN_SCHOOL_CHOICES)
    age = models.SmallIntegerField(validators=[MinLengthValidator(1), MaxLengthValidator(100)])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # relationships models
    university = models.ForeignKey(University, null=True, blank=True)
    courses = models.ManyToManyField(Course, null=True, blank=True)



