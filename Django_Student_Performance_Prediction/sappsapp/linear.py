import numpy as np
from sklearn import linear_model, metrics
from sappsapp.models import *
from django.contrib.auth.models import User

X_train = [[78, 40, 70],[60, 75, 80],[25, 40, 60]]
y_train = [80,90,59]

Att_total = 200
def testdataprep():
	prediction = []
	itotal = 0
	etotal = 0
	i = 1
	j = 1
	atts=0
	points = []
	semsum = [0,0,0,0]
	mcqmark = 0
	students = User.objects.filter(groups__name='Students')
	for student in students:
		sems = Univresults.objects.filter(user=student)
		atts = Attendance.objects.filter(user=student).count()
		mcqs = McqMarks.objects.filter(user=student)
		semsum = [0,0,0,0]
		for mcq in mcqs:
			mcqmark+=1
		for sem in sems:
			itotal =0
			subjects = Subject.objects.filter(sem=sem)
			for sub in subjects:
				itotal+=((float(sub.internal)/float(sub.internmaxi))*100)
				etotal+=((float(sub.mark)/float(sub.maxi))*100)
				print "itotal"
				print itotal
			i=len(subjects)
			if i<=0:
				i=1
			semsum[0]+=(itotal/float(i))
			semsum[1]+=(etotal/float(i))
			print "s0"
			print semsum[0]
		j=len(sems)
		if j<=0:
			j=1
		semsum[0]/=j
		semsum[1]/=j
		print "s1"
		print semsum[0]
		try:
			semsum[2]+= ((mcqmark/len(mcqs))*10)
		except:
			pass
		try:
			semsum[3]+= ((float(atts)/float(Att_total))*100)
		except:
			pass
		points.append(semsum)
		prediction.append([student.username.encode("ascii"), semsum[0], semsum[2], semsum[3]])
	a = [i[0] for i in points]
	b = [i[2] for i in points]
	c = [i[3] for i in points]
	test = [list(i) for i in zip(a, b, c)]
	X_test = test
	return X_test, prediction


# Predict the results
def startprediction():
	global prediction
	# create linear regression object
	reg = linear_model.LinearRegression()

	# train the model using the training sets
	reg.fit(X_train, y_train)

	testdataset, prediction = testdataprep()

	y_internres =[]
	y_mcqres = []
	y_attres = []
	i = 0
	for X_test in testdataset:
		y_res = reg.predict([X_test])
		y_res = y_res.tolist()
		y_internres.append([X_test[0], y_res[0]])
		y_mcqres.append([X_test[1], y_res[0]])
		y_attres.append([X_test[2], y_res[0]])
		prediction[i].append(y_res[0])
		i+=1
	return y_internres, y_mcqres, y_attres, prediction
