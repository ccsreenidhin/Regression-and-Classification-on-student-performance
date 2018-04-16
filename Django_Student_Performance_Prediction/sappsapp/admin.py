# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Profileteacher)

admin.site.register(Profilechild)

admin.site.register(Profileparent)

admin.site.register(Attendance)

admin.site.register(Mcqs)

admin.site.register(Resources)

admin.site.register(Question)

admin.site.register(Assignments)

admin.site.register(Univresults)

admin.site.register(Attendexam)

admin.site.register(McqMarks)

admin.site.register(Subject)
