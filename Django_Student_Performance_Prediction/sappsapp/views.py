# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from sappsapp.models import *
from sappsapp.forms import *
from datetime import date
from kmeans import *
from linear import *
from operator import itemgetter
import json
# Create your views here.

today=date.today()


def group_checkt(user):
    return user.groups.filter(name__in=['Teachers',])

def group_checks(user):
    return user.groups.filter(name__in=['Students',])

def group_checkp(user):
    return user.groups.filter(name__in=['Parents',])

def index(request):
	return render(request, 'index.html', context=None)


def login(request):
	return render(request, 'login.html', context=None)



@login_required
def welcome(request):
    if group_checkt(request.user):
        return redirect('dashboard')
    elif group_checks(request.user):
        return redirect('studentprofile')
    elif group_checkp(request.user):
        return redirect('parentprofile')
    else:
        return render(request, 'index.html', context=None)



#@user_passes_test(group_check)
@login_required
def dashboard(request):
    today=date.today()
    studtotal = User.objects.filter(groups__name='Students').count()
    spresent = Attendance.objects.filter(day = today).count()
    spercent = (float(spresent)/float(studtotal))*100
    studtotal = User.objects.filter(groups__name='Students').count()
    spresent = Attendance.objects.filter(day = today).count()
    spercent = (float(spresent)/float(studtotal))*100
    kmeans={}
    average, belowavg, aboveavg, centroids = startkmeans()
    centroids = np.array(centroids)
    avg = len(average)
    bavg = len(belowavg)
    aavg = len(aboveavg)
    cent1 = [int(i) for i in centroids[0]]
    cent2 = [int(i) for i in centroids[1]]
    cent3 = [int(i) for i in centroids[2]]
    kmeans.update({'average':avg, 'belowavg':bavg,'aboveavg':aavg,'cent1':cent1, 'cent2':cent2, 'cent3':cent3})
    if request.user.is_authenticated():
        try:
            profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
            assigns = Assignments.objects.filter(user = request.user).count()
            res = Resources.objects.filter(user = request.user).count()
        except:
            profile = {}
            assigns = {}
            res={}
    return render(request, 'dashboard.html', {'profile':profile, 'spercent':spercent, 'spresent':spresent, 'assigns':assigns,'res':res, 'kmeans':kmeans})


#@user_passes_test(group_check)
@login_required
def profile(request):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
		except:
			profile = None
	return render(request, 'dashboard/profile.html', {'profile':profile})

#@user_passes_test(group_check)
@login_required
def profileedit(request):
	try:
		profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
	except:
		profile = None
	if request.method == "POST":
		form = ProfileteacherForm(request.POST, instance=profile)
		if form.is_valid():
			profile = form.save(commit=False)
			profile.user = request.user
			profile.save()
			return redirect('profile')
	else:
		form = ProfileteacherForm(instance=profile)
	return render(request, 'dashboard/profileedit.html', {'form':form, 'profile':profile })

#@user_passes_test(group_check)
@login_required
def students(request):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
			childprofile = Profilechild.objects.all()
		except:
			profile = None
			childprofile =None
	return render(request, 'dashboard/students.html', {'profile':profile, 'childprofile':childprofile})

#@user_passes_test(group_check)
@login_required
def attendance(request, pk, div='one', dept='cse'):
	p=''
	students={}
	attend  = {}
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
			profiles = Profilechild.objects.filter(division=div).filter(department=dept)
			for prof in profiles:
                            try:
                                attend = Attendance.objects.filter(user=prof.user).filter(day=today)
                            except:
                                pass
		except:
			profile = {}
			attend = {}
		try:
			profiles = Profilechild.objects.filter(division=div).filter(department=dept)
			for prof in profiles:
				students.update({ prof.user:prof.user })

		except:
			students = {}
	if request.method == "POST":
		form = AttendanceForm(request.POST)
		u = User.objects.get(pk=pk)
		if group_checks(u):
			std = u
		else:
			std = 0
		if form.is_valid():
			att = form.save(commit=False)
			att.user = std
			att.save()
		return redirect('attendance', pk=pk, div=div, dept=dept)
	else:
		form = AttendanceForm()
	return render(request, 'dashboard/attendance.html', {'profile':profile, 'form':form, 'attend':attend, 'students':students, 'div':div, 'dept':dept })

#@user_passes_test(group_check)
@login_required
def mcqs(request):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
			mcqs = Mcqs.objects.filter(user=request.user)
		except:
			profile = {}
			mcqs = {}
	if request.method == "POST":
		form = McqsForm(request.POST)
		if form.is_valid():
			att = form.save(commit=False)
			att.user = request.user
			att.marks = 0
			att.save()
		return redirect('mcqs')
	else:
		form = McqsForm()
	return render(request, 'dashboard/setmcq.html', {'profile':profile, 'mcqs':mcqs, 'form':form })

#@user_passes_test(group_check)
@login_required
def assignments(request):
	user = request.user
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
			assigns = Assignments.objects.filter(user=user)
		except:
			profile = {}
			assigns = {}
	if request.method == "POST":
		form = AssignmentsForm(request.POST, request.FILES)
		if form.is_valid():
			forms = form.save(commit=False)
			forms.user = user
			forms.save()
			return redirect('assignments')
	else:
		form = AssignmentsForm()
	return render(request, 'dashboard/assignments.html', { 'profile':profile, 'assigns':assigns, 'form':form, })

#@user_passes_test(group_check)
@login_required
def resources(request):
	user = request.user
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
			res = Resources.objects.filter(user=user)
		except:
			profile = {}
			res ={}
	if request.method == "POST":
		form = ResourcesForm(request.POST, request.FILES)
		if form.is_valid():
			formres = form.save(commit=False)
			formres.user = user
			formres.save()
			return redirect('resources')
	else:
		form = ResourcesForm()
	return render(request, 'dashboard/resources.html', { 'profile':profile, 'res':res, 'form':form, })

#@user_passes_test(group_check)
@login_required
def ques(request, pk):
	pk = pk
	mcq = Mcqs.objects.get(pk=pk)
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
		except:
			profile = {}
	if request.method == "POST":
		form = QuestionForm(request.POST)
		if form.is_valid():
			formq = form.save(commit=False)
			formq.save()
			return redirect('ques', pk=pk)
	else:
		form = QuestionForm()
	return render(request, 'dashboard/mcq.html', { 'profile':profile, 'form':form, 'mcq':mcq })

#university results page

#University result main page add
#@user_passes_test(group_check)
@login_required
def subject(request):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
			users = User.objects.filter(groups__name='Students')
		except:
			profile = {}
			users = {}
	return render(request, 'dashboard/subject.html', {'profile':profile, 'users':users, })

@login_required
def myper(request):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
			users = User.objects.filter(groups__name='Students')
		except:
			profile = {}
			users = {}
	return render(request, 'dashboard/myper.html', {'profile':profile, 'users':users, })

#add semester mark
#@user_passes_test(group_check)
@login_required
def markadd(request, pk):
    pk=pk
    try:
        ures = Univresults.objects.get(pk=pk)
        subjects = Subject.objects.filter(sem=ures)
    except:
        ures= {}
        subjects = {}
    try:
        profile = Profileteacher.objects.get(user=user, user__is_active = True)
    except:
        profile = {}
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            sobj = form.save(commit=False)
            sobj.sem=ures
            sobj.save()
            if str(sobj.res).upper() == 'PASS' or str(sobj.res).upper() == 'FAIL':
                ures.completed = True
                ures.save()
        return redirect('markadd', pk=pk)
    else:
        form = SubjectForm()
	return render(request, 'dashboard/markadd.html', { 'profile':profile, 'form':form, 'ures':ures, 'subjects':subjects })

#Mcq DELETE
#questions list mcq
#@user_passes_test(group_check)
@login_required
def questionlist(request,pk):
	try:
		mcq = Mcqs.objects.get(pk=pk)
		lis = Question.objects.filter(mcq=mcq)
	except:
		pass
	return render(request, 'dashboard/questionlist.html', {'lis':lis})

#Question DELETE
def questiondelete(request, pk):
    post = get_object_or_404(Mcqs, pk=pk)
    post.delete()
    return redirect('mcqs')

#Assignment DELETE
def removeassigns(request, pk):
    post = get_object_or_404(Assignments, pk=pk)
    post.delete()
    return redirect('assignments')

#Attendance DELETE
def removeattend(request, pk):
    post = get_object_or_404(Attendance, pk=pk)
    post.delete()
    return redirect('attendance', pk=0, div='cse')

#Resources DELETE
def removeres(request, pk):
    post = get_object_or_404(Resources, pk=pk)
    post.delete()
    return redirect('resources')

@login_required
def editres(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
    if request.method == "POST" and request.META['HTTP_REFERER'] != 'http://127.0.0.1:8000/dashboard/markadd/47/':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            post = form.save(commit=False)
            upk = subject.sem.pk
            ures = Univresults.objects.get(pk=upk)
            post.sem = ures
            post.save()
            if str(post.res).upper() == 'PASS' or str(post.res).upper() == 'FAIL':
                ures.completed = True
                ures.save()
            return redirect('editres', pk=pk)
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'dashboard/markedit.html', {'form': form, 'subject':subject})



#Search Parent
#@user_passes_test(group_check)
@login_required
def searchparent(request):
    parentprofile={}
    if request.user.is_authenticated():
        try:
            profile = Profileteacher.objects.get(user=user, user__is_active = True)
        except:
            profile = {}
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            sitem = form.save(commit= False)
            sitem.save()
            try:
                user = User.objects.get(username = sitem.item)
                parentprofile = Profileparent.objects.filter(user = user)
            except:
                try:
                    parentprofile = Profileparent.objects.all()
                except:
                    pass
    return render(request, 'dashboard/parents.html', {'profile':profile, 'parentprofile':parentprofile})


#Search Attendance
#@user_passes_test(group_check)
@login_required
def searchattend(request):
	attend={}
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
		except:
			profile = {}
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			aitem = form.save(commit= False)
			aitem.save()
			try:
				user = User.objects.get(username = aitem.item)
				attend = Attendance.objects.filter(user = user)
			except:
				try:
					attend = Attendance.objects.filter(day = aitem.item)
				except:
					pass
	return render(request, 'dashboard/attendance.html', {'profile':profile, 'attend':attend })

#Search Students
#@user_passes_test(group_check)
@login_required
def searchstud(request):
	childprofile={}
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
		except:
			profile = {}
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			sitem = form.save(commit= False)
			sitem.save()
			try:
				childprofile = Profilechild.objects.filter(division = str(sitem.item))
			except:
				try:
					user = User.objects.get(username = sitem.item)
					childprofile = Profilechild.objects.filter(user = user)
				except:
					childprofile = Profilechild.objects.all()

	return render(request, 'dashboard/students.html', {'profile':profile, 'childprofile':childprofile})


#student profile
#@user_passes_test(group_check)
@login_required
def studentpro(request, pk):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
		except:
			profile = {}
		prof = Profilechild.objects.get(pk=pk)
	return render(request, 'dashboard/student/stdntproforteacher.html', {'profile':profile, 'prof':prof })


#Add semester
#@user_passes_test(group_check)
@login_required
def semname(request, pk):
    pk = pk
    user = User.objects.get(pk=pk)
    sems = Univresults.objects.filter(user=user)
    profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
    if request.method == "POST":
        form = UnivresultsForm(request.POST)
        if form.is_valid():
            formq = Univresults()
            formq.semname = form.cleaned_data['semname']
            formq.user=user
            print formq.semname
            if formq.semname:
                formq.save()
        return redirect('semname', pk=pk)
    else:
        form = UnivresultsForm()
	return render(request, 'dashboard/student/semname.html', { 'profile':profile, 'sems':sems,'form':form, 'user':user })




#student detail
#@user_passes_test(group_check)
@login_required
def attendanceres(request,pk):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
		except:
			profile = {}
		prof = Profilechild.objects.get(pk=pk)
		user = prof.user
		attend = Attendance.objects.filter(user=user)
	return render(request, 'dashboard/student/attendanceres.html', {'attend':attend, 'profile':profile, 'prof':prof })


#assignment detail
#@user_passes_test(group_check)
@login_required
def assignmentdet(request,pk):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
		except:
			profile = {}
		user = User.objects.get(pk=pk)
		attend = Assignments.objects.filter(user=user)
	return render(request, 'dashboard/student/assignmentdet.html', {'attend':attend, 'profile':profile})

#university mark add for TEACHER
#@user_passes_test(group_check)
@login_required
def universityres(request, pk):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=user, user__is_active = True)
		except:
			profile = {}
		prof = Profilechild.objects.get(pk=pk)
		user = prof.user
		results = Univresults.objects.filter(user=user)
		sems = {}
		for result in results:
			sems.update({ Subject.objects.filter(sem=result): Subject.objects.filter(sem=result)})
	return render(request, 'dashboard/student/universityres.html', {'results': results, 'profile':profile, 'prof':prof, 'sems':sems })

#@user_passes_test(group_check)
@login_required
def parentpro(request,pk):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
		except:
			profile = None
		pprof = Profileparent.objects.get(pk=pk)
	return render(request, 'dashboard/parent/parentprofile.html', {'profile':profile, 'pprof':pprof })

#@user_passes_test(group_check)
@login_required
def parents(request):
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
			parentprofile = Profileparent.objects.all()
		except:
			profile = None
			parentprofile =None
	return render(request, 'dashboard/parents.html', {'profile':profile, 'parentprofile':parentprofile})


#@user_passes_test(group_check)
@login_required
def mcqmarks(request, pk):
	pk = pk
	marks = {}
	m=0
	ma=0
	if request.user.is_authenticated():
		try:
			profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
		except:
			profile = {}
		prof = Profilechild.objects.get(pk=pk)
		user = prof.user
		for mc in Mcqs.objects.all():
			ma = McqMarks.objects.filter(user=user).filter(mcq=mc.name).count()
			qs = Question.objects.filter(mcq=mc).count()
			try:
                            m = ((float(ma)/float(qs))*100)
                        except:
                            m=0
			marks.update({str(mc.name):m})
		print marks
	return render(request, 'dashboard/mcqmark.html', {'marks':marks, 'profile':profile, 'prof':prof })


#@user_passes_test(group_check)
@login_required
def prediction(request):
    global prediclist
    resintern, resmcq, resatt, prediclist = startprediction()
    resintern.sort(key=itemgetter(0))
    resmcq.sort(key=itemgetter(0))
    resatt.sort(key=itemgetter(0))
    if request.user.is_authenticated():
        try:
            profile = Profileteacher.objects.get(user=request.user, user__is_active = True)
        except:
            profile = {}
    results = {'resintern':resintern, 'resmcq':resmcq, 'prediclist':prediclist, 'resatt':resatt }
    return render(request, 'dashboard/predictions.html', {'profile':profile, 'results':results })






##########################################################################
##########################################################################
###############Student views##############################################


@login_required
def studentprofile(request):
    resintern, resmcq, resatt, prediclist = startprediction()
    if request.user.is_authenticated():
        try:
            profile = Profilechild.objects.get(user=request.user)
        except:
            profile = {}
        context = { 'profile':profile }
	val =[i for i in prediclist if i[0]==(request.user.username)]
	context.update({'prediction':val[0]})
	return render(request, 'student/profile.html', context)


#student assignment
@login_required
def stuassignmentdet(request):
	if request.user.is_authenticated():
		try:
			profile = Profilechild.objects.get(user=request.user)
		except:
			profile = {}

		assign = Assignments.objects.all()
	return render(request, 'student/stuassignmentdet.html', {'assign':assign, 'profile':profile})

#student attendance
@login_required
def stuattendanceres(request):
    if request.user.is_authenticated():
        try:
            profile = Profilechild.objects.get(user=request.user)
        except:
            profile = {}
        attend = Attendance.objects.filter(user=request.user)
    return render(request, 'student/stuattendanceres.html', {'attend':attend, 'profile':profile })

#student resources
@login_required
def studentresources(request):
    if request.user.is_authenticated():
        try:
            profile = Profilechild.objects.get(user=request.user)
        except:
            profile = {}
        res = Resources.objects.all()
    return render(request, 'student/studentresource.html', { 'res':res,'profile':profile, })

#MCQ for student
@login_required
def questions(request):
    que={}
    context={}
    profile = Profilechild.objects.get(user=request.user)
    if request.user.is_authenticated():
	    try:
		    que = Mcqs.objects.all()
	    except:
		    que = {}
    context={'profile':profile, 'que':que}
    return render(request, 'student/studentmcq.html', context)

#attend exam
@login_required
def attendexam(request, pk, id):
    profile = Profilechild.objects.get(user=request.user)
    if request.method == "POST":
        try:
            mcq = Mcqs.objects.get(pk=id)
            q = Question.objects.get(pk=pk)
            form = AttendexamForm(request.POST)
            if form.is_valid():
                formq = form.save(commit=False)
                items = Attendexam()
                items.answer = formq.answer
                items.question = pk
                items.save()
                if q.answer.upper() == formq.answer.upper():
                    markclass = McqMarks()
                    markclass.user = request.user
                    markclass.mark=1
                    markclass.mcq=mcq.name
                    markclass.save()
        except:
            pass
        return redirect('attendexam', pk=pk, id=id)
    else:
        mcq = Mcqs.objects.get(pk=id)
        quest= Question.objects.filter(mcq=mcq)
        form = AttendexamForm()
    return render(request, 'student/attendexam.html', {'quest':quest, 'form':form,'mpk':pk, 'profile':profile})

#MCQ for student
@login_required
def studentUnires(request):
    if request.user.is_authenticated():
        try:
            profile = Profilechild.objects.get(user=request.user)
        except:
            profile = {}
    	user = profile.user
    	results = Univresults.objects.filter(user=user)
    	sems = {}
    	for result in results:
    		sems.update({ Subject.objects.filter(sem=result): Subject.objects.filter(sem=result)})
    return render(request, 'student/studentUnires.html', {'results': results, 'profile':profile, 'sems':sems })

#view result
@login_required
def viewres(request,pk):
    if request.user.is_authenticated():
		try:
			que = Subject.objects.get(pk=pk)
		except:
			que = {}
    print type(que)
    print Subject
    return render(request, 'student/viewres.html', {'quest':que})


@login_required
def stdmcqmarks(request, pk):
	pk = pk
	marks = {}
	m=0
	ma=0
	qs=0
	if request.user.is_authenticated():
		try:
			profile = Profilechild.objects.get(user=request.user, user__is_active = True)
		except:
			profile = {}
		prof = Profilechild.objects.get(pk=pk)
		user = prof.user
		for mc in Mcqs.objects.all():
			ma = McqMarks.objects.filter(user=user).filter(mcq=mc.name).count()
			print ma
			qs = Question.objects.filter(mcq=mc).count()
			try:
                            m = ((float(ma)/float(qs))*100)
                        except:
                            m=0
			marks.update({str(mc.name):{'mark':m,'pk':mc.pk}})
		print marks
	return render(request, 'student/mcqmark.html', {'marks':marks, 'profile':profile, 'prof':prof })

#student resources
@login_required
def stdcontteacher(request):
    if request.user.is_authenticated():
        try:
            profile = Profilechild.objects.get(user=request.user)
        except:
            profile = {}
	prof={}
	prof = Profileteacher.objects.all().values('user','phone','email')
    return render(request, 'student/contactt.html', { 'profile':profile, 'prof':prof, })

##########################################################################
##########################################################################
##################Parent views############################################


@login_required
def parentprofile(request):
    if request.user.is_authenticated():
        try:
            profile = Profileparent.objects.get(user=request.user)
        except:
            profile = {}
	return render(request, 'parent/profile.html', { 'profile':profile })


#student attendance
@login_required
def parattendanceres(request):
    if request.user.is_authenticated():
        profile = Profileparent.objects.get(user=request.user)
        attend = Attendance.objects.filter(user=profile.child.user)
	return render(request, 'parent/parattendanceres.html', {'attend':attend,'profile':profile})


#MCQ for student
@login_required
def parentUnires(request):
    profile = Profileparent.objects.get(user=request.user)
    child = profile.child.user
    if request.user.is_authenticated():
        results = Univresults.objects.filter(user=child)
        sems = {}
        for result in results:
            sems.update({ Subject.objects.filter(sem=result): Subject.objects.filter(sem=result)})
	return render(request, 'parent/parentUnires.html', { 'sems':sems, 'profile':profile })


#view result
@login_required
def parentviewres(request,pk):
    return render(request, 'parent/viewres.html', {'sems':sems})

@login_required
def prochild(request, pk):
    if request.user.is_authenticated():
        try:
            profile = Profileparent.objects.get(user=request.user)
        except:
            profile = {}
    context={}
    resintern, resmcq, resatt, prediclist = startprediction()
    try:
	prof = Profilechild.objects.get(pk=pk)
    except:
	prof = {}
    context = { 'profile':profile, 'prof':prof }
    val =[i for i in prediclist if i[0]==str(prof.user.username)]
    context.update({'prediction':val[0]})
    return render(request, 'parent/prochild.html', context)

@login_required
def pmcqmarks(request):
	marks = {}
	m=0
	ma=0
	if request.user.is_authenticated():
		try:
			profile = Profileparent.objects.get(user=request.user, user__is_active = True)
		except:
			profile = {}
		u = profile.child.user
		prof = Profilechild.objects.get(user=u)
		user = prof.user
		for mc in Mcqs.objects.all():
			ma = McqMarks.objects.filter(user=user).filter(mcq=mc.name).count()
			qs = Question.objects.filter(mcq=mc).count()
			try:
                            m = ((float(ma)/float(qs))*100)
                        except:
                            m=0
			marks.update({str(mc.name):m})
		print marks
	return render(request, 'parent/mcqmark.html', {'marks':marks, 'profile':profile, 'prof':prof })

#student resources
@login_required
def pcontteacher(request):
    if request.user.is_authenticated():
        try:
            profile = Profilechild.objects.get(user=request.user)
        except:
            profile = {}
	prof={}
	prof = Profileteacher.objects.all().values('user','phone','email')
    return render(request, 'parent/contactt.html', { 'profile':profile, 'prof':prof, })

##########################################################################
##########################################################################
##################Android views############################################

@csrf_exempt
def androidlogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        em = {}
        if user is not None:
            if group_checks(user):
                resintern, resmcq, resatt, prediclist = startprediction()
                val =[i for i in prediclist if i[0]==(user.username)]
                emails = Profileteacher.objects.all().values_list('email', flat=True)
                profile = Profilechild.objects.get(user=user)
                dict = {'user':str(profile.user.username),
                'picurl':str(profile.picture.url),
                'univno':str(profile.univno),
                'about':str(profile.about),
                'phone':str(profile.phone),
                'email':str(profile.email),
                'gender':str(profile.gender),
                'department':str(profile.department),
                'division':str(profile.division),
                'father':str(profile.father),
                'mother':str(profile.mother),
                'address':str(profile.address),
		'prediction':str(val[0][4]),
                'studentpk':str(profile.user.pk)
                }
                dict.update({'usertype':'student', 'message':'loginsuccess'})
            elif group_checkp(user):
                resintern, resmcq, resatt, prediclist = startprediction()
                emails = Profileteacher.objects.all().values_list('email', flat=True)
                profile = Profileparent.objects.get(user=user)
                val =[i for i in prediclist if i[0]==(profile.child.user.username)]
                dict = {'user':str(profile.user.username),
                'picurl':str(profile.picture.url),
                'about':str(profile.about),
                'phone':str(profile.phone),
                'email':str(profile.email),
                'gender':str(profile.gender),
                'child':str(profile.child.user.username),
                'address':str(profile.address),
		        'prediction':str(val[0][4]),
                'studentpk':str(profile.child.user.pk)
                }
                dict.update({'usertype':'parent', 'message':'loginsuccess'})
        else:
            dict={'message':'loginerror'}
    return HttpResponse(json.dumps(dict))

@csrf_exempt
def androidatt(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if group_checks(user):
                dict = {'category':{}}
                attendance = Attendance.objects.filter(user=user)
                for att in attendance:
                    dict['category'].update({ str(att.day):str(att.status)})
            elif group_checkp(user):
                dict = {}
                parent = Parentprofile.objects.get(user = user)
                chld = parent.child.user
                attendance = Attendance.objects.filter(user=child)
                for att in attendance:
                    dict.update({'day':str(att.day), 'status':str(att.status),})
        else:
            dict={'message':'loginerror'}
    return HttpResponse(json.dumps(dict))

@csrf_exempt
def androidassi(request):
     if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if group_checks(user):
                dict = {}
                assigns = Assignments.objects.all()
                for assi in assigns:
                    dict.update({ str(assi.topic):{'description':str(assi.disc), 'url':str(assi.fil.url)}})

            elif group_checkp(user):
                dict = {}

        else:
            dict={'message':'loginerror'}
     return HttpResponse(json.dumps(dict))


@csrf_exempt
def androidres(request, pk):
    child = User.objects.get(pk=pk)
    results = Univresults.objects.filter(user=child)
    sems = {}
    for result in results:
        sems.update({ Subject.objects.filter(sem=result): Subject.objects.filter(sem=result)})
    return render(request, 'androiduniv.html', {'sems':sems})



@csrf_exempt
def androidmcq(request):
     if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if group_checks(user):
                dict = {}
		m=0
		ma=0
		prof = Profilechild.objects.get(user=user)
		user = prof.user
		for mc in Mcqs.objects.all():
			ma = McqMarks.objects.filter(user=user).filter(mcq=mc.name).count()
			qs = Question.objects.filter(mcq=mc).count()
        		try:
                            m = ((float(ma)/float(qs))*100)
                        except:
                            m=0
			dict.update({str(mc.name):m})

            elif group_checkp(user):
                dict = {}
		m=0
		ma=0
		profile = Profileparent.objects.get(user=user)
		prof = Profilechild.objects.get(user=profile.child.user)
		user = prof.user
		for mc in Mcqs.objects.all():
			ma = McqMarks.objects.filter(user=user).filter(mcq=mc.name).count()
			qs = Question.objects.filter(mcq=mc).count()
			try:
                            m = ((float(ma)/float(qs))*100)
                        except:
                            m=0
			dict.update({str(mc.name):m})

        else:
            dict={'message':'loginerror'}
     return HttpResponse(json.dumps(dict))

@csrf_exempt
def androidcont(request):
     if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if group_checks(user):
                dict={}
		p = Profileteacher.objects.all()
		for prof in p:
                	dict.update({str(prof.user.username):{'phone':prof.phone, 'email':prof.email}})

            elif group_checkp(user):
                dict={}
		p = Profileteacher.objects.all()
		for prof in p:
                	dict.update({str(prof.user.username):{'phone':prof.phone, 'email':prof.email}})


        else:
            dict={'message':'loginerror'}
     return HttpResponse(json.dumps(dict))



@csrf_exempt
def androidresource(request):
     if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if group_checks(user):
                dict = {}
                assigns = Resources.objects.all()
                for assi in assigns:
                    dict.update({ str(assi.topic):{'description':str(assi.disc), 'url':str(assi.video.url)}})

            elif group_checkp(user):
                dict = {}

        else:
            dict={'message':'loginerror'}
     return HttpResponse(json.dumps(dict))
