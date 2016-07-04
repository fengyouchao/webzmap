from django.test import TestCase

# Create your tests here.
import uuid


def gen_job_id():
    return str(uuid.uuid4()).replace('-', '')


print len(gen_job_id())
