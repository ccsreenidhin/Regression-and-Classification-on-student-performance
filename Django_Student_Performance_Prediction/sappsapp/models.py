# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

from django.core.validators import RegexValidator

from datetime import date

# Create your models here.

def get_upload_path(instance, filename):
    return 'users/{0}/{1}'.format(instance.user.username, filename)

class Profileteacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    idno = models.IntegerField(default=0, null=True, blank = True)
    qualification = models.CharField(max_length=30, blank=True, null=True)
    about = models.TextField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=50, blank=True)
    address = models.TextField(max_length=150, blank=True)

    def __unicode__(self):
        return self.user.username


class Profilechild(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    univno = models.IntegerField(default=0)
    about = models.TextField(max_length=150, default='')
    phone = models.CharField(max_length=50, default='')
    email = models.CharField(max_length=50, default='')
    gender = models.CharField(max_length=50, default='')
    department = models.CharField(max_length=50, default='')
    division = models.CharField(max_length=50, default='')
    father = models.CharField(max_length=50, default='')
    mother = models.CharField(max_length=50, default='')
    address = models.TextField(max_length=150, default='')

    def __unicode__(self):
        return self.user.username

class Profileparent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    about = models.TextField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(max_length=150, blank=True, null=True)
    child = models.OneToOneField(Profilechild, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.user.username

ATT_CHOICE = (('present','present'),('absent','absent'))

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.DateField(default=date.today, null = True, blank = True)
    status = models.CharField(max_length=50, choices=ATT_CHOICE, default='present')

class Assignments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200, blank=True, null=True)
    disc = models.CharField(max_length=200, blank=True, null=True)
    fil = models.FileField(upload_to='documents/asignments')

class Resources(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200, blank=True, null=True)
    disc = models.CharField(max_length=200, blank=True, null=True)
    video = models.FileField(upload_to='documents/video')


class Univresults(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    semname = models.CharField(max_length=200, blank=True, null=True)
    completed = models.BooleanField(default = False)

    def __unicode__(self):
        return self.user.username

class Subject(models.Model):
    sem = models.ForeignKey(Univresults, on_delete=models.CASCADE)
    sub = models.CharField(max_length=200,  blank=True, null=True)
    mark = models.CharField(max_length=200,  blank=True, null=True)
    internal = models.CharField(max_length=200,  blank=True, null=True)
    internmaxi = models.CharField(max_length=200,  blank=True, null=True)
    maxi = models.CharField(max_length=200,  blank=True, null=True)
    total = models.CharField(max_length=200,  blank=True, null=True)
    res = models.CharField(max_length=200, blank=True, null=True)


class Mcqs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_id = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=80, null=True, blank = True)
    marks = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)


class Question(models.Model):
    mcq = models.ForeignKey(Mcqs, on_delete=models.CASCADE, null=True, blank=True)
    question = models.CharField(max_length=200, null=True, blank=True)
    c1 = models.CharField(max_length=200, null=True, blank=True)
    c2 = models.CharField(max_length=200, null=True, blank=True)
    c3 = models.CharField(max_length=200, null=True, blank=True)
    c4 = models.CharField(max_length=200, null=True, blank=True)
    answer = models.CharField(max_length=200, null=True, blank=True)
    marks = models.IntegerField(default=0)

    def __str__(self):
        return str(self.question)

class McqMarks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    marks = models.IntegerField(default=0)
    mcq = models.CharField(max_length=80, null=True, blank = True)

    def __str__(self):
        return str(self.mcq)

class MyPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    testname = models.CharField(max_length=200, blank=True, null=True)

class MyPresults(models.Model):
    sem = models.ForeignKey(MyPerformance, on_delete=models.CASCADE)
    sub = models.CharField(max_length=200,  blank=True, null=True)
    mark = models.CharField(max_length=200,  blank=True, null=True)
    maxi = models.CharField(max_length=200,  blank=True, null=True)

class Search(models.Model):
    item = models.CharField(max_length=80, null=True, blank = True)

class Attendexam(models.Model):
    question = models.IntegerField(default=0)
    answer = models.CharField(max_length=80, null=True, blank = True)
