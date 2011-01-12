#!/usr/bin/env python

import os, sys

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

from django.test.simple import run_tests
from django.conf import settings

def runtests():
    failures = run_tests(['tests', 'warehouse'], verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
