from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProfileteacherForm(forms.ModelForm):
    class Meta:
        model = Profileteacher
        fields = ('phone','email','gender','department','qualification','about','address','picture')


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields =('day','status')


class McqsForm(forms.ModelForm):
    class Meta:
        model = Mcqs
        fields = ('test_id','name')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('mcq','question', 'c1', 'c2', 'c3', 'c4', 'answer')


class UnivresultsForm(forms.Form):
      semname = forms.CharField(label='semname', max_length=10,)


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('sub','mark','internal', 'maxi', 'internmaxi', 'total', 'res')
        widgets = {
            'sub': forms.TextInput(attrs={'size':5}),
            'mark': forms.TextInput(attrs={'size':5}),
            'internal': forms.TextInput(attrs={'size':5}),
            'maxi': forms.TextInput(attrs={'size':5}),
            'internmaxi': forms.TextInput(attrs={'size':5}),
            'total': forms.TextInput(attrs={'size':5}),
            'res': forms.TextInput(attrs={'size':5}),
        }


class AssignmentsForm(forms.ModelForm):
    class Meta:
        model = Assignments
        fields = ('topic','disc','fil',)


class ResourcesForm(forms.ModelForm):
    class Meta:
        model = Resources
        fields = ('topic','disc','video',)



class SearchForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = ('item',)


class AttendexamForm(forms.ModelForm):
    class Meta:
        model = Attendexam
        fields = ('answer',)

class MyPerformanceForm(forms.ModelForm):
    class Meta:
        model = MyPerformance
        fields = '__all__'

class MyPresultsForm(forms.ModelForm):
    class Meta:
        model = MyPerformance
        fields = '__all__'
