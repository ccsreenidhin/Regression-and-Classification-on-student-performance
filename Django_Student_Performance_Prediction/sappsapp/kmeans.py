import numpy as np
import os
from sappsapp.models import *
from django.contrib.auth.models import User



def compute_euclidean_distance(point, centroid):
    return np.sqrt(np.sum((point - centroid)**2))

def assign_label_cluster(distance, data_point, centroids):
    index_of_minimum = min(distance, key=distance.get)
    return [index_of_minimum, data_point, centroids[index_of_minimum]]

def compute_new_centroids(cluster_label, centroids):
    return np.array(cluster_label + centroids)/2

def iterate_k_means(data_points, centroids, total_iteration):
    label = []
    cluster_label = []
    total_points = len(data_points)
    k = len(centroids)
    for iteration in range(0, total_iteration):
        for index_point in range(0, total_points):
            distance = {}
            for index_centroid in range(0, k):
                distance[index_centroid] = compute_euclidean_distance(data_points[index_point], centroids[index_centroid])
            label = assign_label_cluster(distance, data_points[index_point], centroids)
            centroids[label[0]] = compute_new_centroids(label[1], centroids[label[0]])

            if iteration == (total_iteration - 1):
                cluster_label.append(label)

    return [cluster_label, centroids]

def print_label_data(result):
    average=[]
    belowavg=[]
    aboveavg=[]
    centroids=[]
    print("Result of k-Means Clustering: \n")
    for data in result[0]:
        if data[0]==0:
            belowavg.append(data[1])
        elif data[0]==1:
            average.append(data[1])
        elif data[0]==2:
            aboveavg.append(data[1])
        print("data point: {}".format(data[1]))
        print("cluster number: {} \n".format(data[0]))
    print("Last centroids position: \n {}".format(result[1]))
    return average, belowavg, aboveavg, result[1]

def create_centroids():
    centroids = []
    centroids.append([10, 40])
    centroids.append([25, 55])
    centroids.append([38, 85])
    return np.array(centroids)


def startkmeans():
    itotal = 0
    etotal = 0
    i = 1
    j = 1
    points=[]
    semsum = [0,0]
    students = User.objects.filter(groups__name='Students')
    for student in students:
        semsum = [0,0]
        sems = Univresults.objects.filter(user=student)
        for sem in sems:
            itotal = 0
            subjects = Subject.objects.filter(sem=sem)
            for sub in subjects:
                itotal+=((float(sub.internal)/float(sub.internmaxi))*100)
                etotal+=((float(sub.mark)/float(sub.maxi))*100)
            i=len(subjects)
            if i<=0:
                i=1
            semsum[0]+=(itotal/float(i))
            semsum[1]+=(etotal/float(i))
        j=len(sems)
        if j<=0:
            j=1
        semsum[0]/=j
        semsum[1]/=j
        points.append(semsum)


    data_points = points
    print data_points
    centroids = create_centroids()
    total_iteration = 100

    [cluster_label, new_centroids] = iterate_k_means(data_points, centroids, total_iteration)
    average, belowavg, aboveavg, centroids = print_label_data([cluster_label, new_centroids])
    return average, belowavg, aboveavg, centroids





#kmeans ends
