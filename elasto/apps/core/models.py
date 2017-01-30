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
                    'preserve_separators': True,
                    'preserve_position_increments': True,
                    'max_input_length': 50,
                },
                "course_names": {
                    "type": "string", "store": "yes", "index": "not_analyzed",
                },
            }
        }

        def es_repr(self):
        data = {}
        mapping = self._meta.es_mapping
        data['_id'] = self.pk

        for field_name in mapping['properties'].keys():
            data[field_name] = self.field_es_repr(field_name)
        return data

    def field_es_repr(self, field_name):
        config = self._meta.es_mapping['properties'][field_name]
        if hasattr(self, 'get_es_%s' % field_name):
            field_es_value = getattr(self, 'get_es_%s' % field_name)()
        else:
            if config['type'] == 'object':
                related_object = getattr(self, field_name)
                field_es_value = {}
                field_es_value['_id'] = related_object.pk
                for prop in config['properties'].keys():
                    field_es_value[prop] = getattr(related_object, prop)
            else:
                field_es_value = getattr(self, field_name)
        return field_es_value

    def get_es_name_complete(self):
        return {
            "input": [self.first_name, self.last_name],
            "output": "%s %s" % (self.first_name, self.last_name),
            "payload": {"pk": self.pk},
        }

    def get_es_course_names(self):
        if not self.courses.exists():
            return []
        return [c.name for c in self.courses.all()]

    def save(self, *args, **kwargs):
        is_new = self.pk
        super(Student, self).save(*args, **kwargs)
        payload = self.es_repr()
        if is_new is not None:
            del payload['_id']
            es_client.update(
                index=self._meta.es_index_name,
                doc_type=self._meta.es_type_name,
                id=self.pk,
                refresh=True,
                body={
                    'doc': payload
                }
            )
        else:
            es_client.create(
                index=self._meta.es_index_name,
                doc_type=self._meta.es_type_name,
                id=self.pk,
                refresh=True,
                body={
                    'doc': payload
                }
            )

    def delete(self, *args, **kwargs):
        prev_pk = self.pk
        super(Student, self).delete(*args, **kwargs)
        es_client.delete(
            index=self._meta.es_index_name,
            doc_type=self._meta.es_type_name,
            id=prev_pk,
            refresh=True,
        )


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



