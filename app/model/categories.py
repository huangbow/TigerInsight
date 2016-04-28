#__author__ = 'aria joon!'

import sys
import csv
import time
import heapq
import math
import copy
#from sklearn.metrics import silhouette_samples, silhouette_score
import numpy as np
#import matplotlib as cm
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from sklearn.cluster import KMeans
from parse import CleanData

#assumption: the input file is sorted on date for each person
####################
#functions used in the code:
####################
def dist(a_list,b_list): #return euclidean distance of two n-D vectors
    sum = 0
    for i in range(0,dimentionality):
        sum += (a_list[i]-b_list[i])*(a_list[i]-b_list[i])
    return math.sqrt(sum)

def avg(input_array):
    sum=0
    for i in range(0,len(input_array)):
        sum += input_array[i]
    return sum/len(input_array)

# return centroid of given points
def centroid(points,input): #points is a 1D array:keeping indices(for input list) of points for which we find centroid
    result = [0]*dimentionality
    for i in range(0,dimentionality):
        for j in points:
            #input dim reduced to one
            result[i] += input[j]
        result[i] = result[i]/len(points)
    return result

def index(input_list,value):#assumption:input_list does not hold repetitive values
    for i in range(0,len(input_list)):
        if input_list(i)==value:
            return i
    return -1 #signals 'the value not found'


def heap_init(input): #initializes heap
    #define heap node structure : [distance_between_clusters,[cluster_A],[cluster_B],lazy_removal_tag]
    #lazy_removal_tag: 0-->clusters can be considered to merge;
    #                  1-->at least one of the clusters was prevoiusly merged
    #                      and the current root node is ignored
    heap = []
    for i in range(0,len(input)-1):
        for j in range(i+1,len(input)):
            heap.append([dist(centroid([i],input),centroid([j],input)),[i],[j],0])
    heapq.heapify(heap)
    return heap

def heap_init_after_kmeans(init_clusters,input): #init_clusters is 2D
    heap=[]
    for i in range(0,len(init_clusters)-1):
        for j in range(i+1,len(init_clusters)):
            heap.append([dist(centroid(init_clusters[i],input),centroid(init_clusters[j],input)),init_clusters[i],init_clusters[j],0])
    heapq.heapify(heap)
    return heap


#function for extracting the heap root node and all related stuff...
def heap_root_extract(heap,current_clusters,input):
    temp = heapq.heappop(heap)

    if temp[3] == 0: #if the root node is valid for merging the two clusters

        for i in range(0,len(heap)): #checking heap nodes for lazy removal tagging
            if heap[i][1]==temp[1] or heap[i][1]==temp[2] or heap[i][2]==temp[1] or heap[i][2]==temp[2]:
                heap[i][3] = 1 #tagging for lazy removal
        clusters_temp = copy.deepcopy(current_clusters)

        for i in range(0,len(clusters_temp)): #remove first merged cluster
            if temp[1]==clusters_temp[i]:
                clusters_temp.remove(clusters_temp[i])
                break

        for i in range(0,len(clusters_temp)): #remove second merged cluster
            if temp[2]==clusters_temp[i]:
                clusters_temp.remove(clusters_temp[i])
                break
        clusters_temp.append(temp[1]+temp[2]) #add new cluster

        for i in range(0,len(clusters_temp)-1): #now, add new nodes to heap:
            heapq.heappush(heap,[dist(centroid(clusters_temp[len(clusters_temp)-1],input),centroid(clusters_temp[i],input)),clusters_temp[len(clusters_temp)-1],clusters_temp[i],0])
        return clusters_temp
    else:
        return []


#returns numpy compatible sparse matrix for scikit learn functions' input arguments
def np_matrix(input_list):
    output_list=[0]*len(input_list)
    for i in range(0,len(input_list)):
        output_list[i] = [input_list[i]]
    return np.asarray(output_list)

#to perform k-mean clustering before hierarchical clustering
def kmeans_result(inter_arrival_means,num_of_clusters):#num_of_clusters=8
    init_seeds = [0]*num_of_clusters
    for i in range(0,num_of_clusters):
        init_seeds[i]= (i+0.5)*(max(inter_arrival_means)-min(inter_arrival_means))/num_of_clusters
    km = KMeans(n_clusters=num_of_clusters,init=np_matrix(init_seeds), n_init=1).fit(np_matrix(inter_arrival_means))
    initial_clustering = []
    for i in range(0,num_of_clusters):
        initial_clustering.append([])
    for i in range(0,len(inter_arrival_means)):
        cluster_id = km.predict(np.matrix(inter_arrival_means[i]))
        initial_clustering[cluster_id[0]].append(i)
    return initial_clustering

##############################
# These functions implement silhouette method for determning k_value, number of clusters
##############################
# returns avg distance of a  point to all other points in the same cluster
def intra_clust_dist(point_index,cluster,inter_arrival_means): #for one dimensional data (our case)
    sum = 0
    for i in range(0,len(cluster)):
        sum += abs(inter_arrival_means[cluster[i]]-inter_arrival_means[point_index])
    if (len(cluster)>1):return 1.0*sum/(len(cluster)-1)
    else:return 0 # just to signal that we have single item cluster

# returns avg distance of a point to all other points in another cluster
def inter_clust_dist(point_index,cluster,inter_arrival_means):
    sum = 0
    for i in range(0,len(cluster)):
        sum += abs(inter_arrival_means[cluster[i]]-inter_arrival_means[point_index])
    return 1.0*sum/(len(cluster))

#silhouette coef for one point
def silhouette_coef(point_index,clusters,cluster_index,inter_arrival_means):#clusters:all clusters
    a = intra_clust_dist(point_index,clusters[cluster_index],inter_arrival_means)
    if (clusters[0]!=clusters[cluster_index]): b = inter_clust_dist(point_index,clusters[0],inter_arrival_means)
    else: b = inter_clust_dist(point_index,clusters[1],inter_arrival_means) #init b
    for i in range(0,len(clusters)):
        if (inter_clust_dist(point_index,clusters[i],inter_arrival_means) < b and clusters[i]!=clusters[cluster_index]):
            b = inter_clust_dist(point_index,clusters[i],inter_arrival_means)
            #print "for clister[i]=",clusters[i],"point=",point_index,"b is: ",b,"max a,b is ",max(a,b)
    #if (max(a,b)==0) : print "max is 0!"
    if (a==0): return -1 # why -1? any other value?
    else: return (b-a)/max(a,b)

#k_clust_eval:returns [k,avg_silhouette_coef_on_all_datapoints,[cluste_id,size,avg_silhouette_coef]s]
def k_cluster_eval(clusters, inter_arrival_means):#clustering evaluation for a known k
    result = [0]*(len(clusters)+2)
    result[0] = len(clusters) # k: num of clusters
    for i in range(0,len(clusters)):
        cluster_id = i
        cluster_size = len(clusters[i])
        sum=0
        for j in range(0,len(clusters[i])):
            sum=silhouette_coef(clusters[i][j],clusters, i,inter_arrival_means)
        cluster_silhouette= 1.0*sum/cluster_size
        result[i+2] = [cluster_id,cluster_size,cluster_silhouette]
    sum = 0
    data_cnt = 0
    for i in range(0,len(clusters)): # returns avg silhouette of all datapoits (weighted avg of cluster silhouettes)
        sum += result[i+2][2]*result[i+2][1]
        data_cnt += result[i+2][1]
    result[1] = 1.0*sum/data_cnt
    return result

#returns k_value: The optimal number of clusters that we choose for clustering algorithm.
# cluster_proc: a list of "all clusters" in "all iterations" of hierarchical clustering
def determine_k_value(cluster_proc, inter_arrival_means):
    k_value = k_cluster_eval(cluster_proc[1],inter_arrival_means)[0]
    temp_silhouette = k_cluster_eval(cluster_proc[1],inter_arrival_means)[1]
    for i in range (2,len(cluster_proc)-1):
        if (k_cluster_eval(cluster_proc[i],inter_arrival_means)[1] > temp_silhouette):
            k_value = k_cluster_eval(cluster_proc[i],inter_arrival_means)[0]
            temp_silhouette = k_cluster_eval(cluster_proc[i],inter_arrival_means)[1]
            #print "for k = ", len(cluster_proc)-i,"eval is:",k_cluster_eval(cluster_proc[i],inter_arrival_means)
    return k_value

## Use a class to wrap this file
class Category():

    def __init__(self):
        self.inp_dataset = []
        self.inter_arrivals = [[]]
        self.acc_id=[]
        self.user_id = []
        self.inter_arrival_means = []
        self.inter_arrival_cnt = []
        self.index_to_remove = []
        self.categories = []

    def categorize(self, file_name, file_to_save_path):    
        ############################
        ##### main code here:#####
        ############################

        inp_dataset = []

        # Clean data at first, and obtain the path of the cleaned input data
        file_to_save_path = CleanData(file_name, file_to_save_path)

        #with open('social_wifi_preprocessed_sample.csv','rU') as csvfile:
        with open(file_to_save_path,'rU') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=",")
            for line in csvreader:
                #inp_dataset.append([line[0],time.strptime(line[1],"%m/%d/%y %H:%M"),int(line[2])]) #
                if (line[0].isspace()== False and line[0]!=''):
                    inp_dataset.append([int(line[0]),time.strptime(line[1],"%m/%d/%y"),int(line[2])]) #changed(arg 0)

        #print "pre-processed social Wi-Fi input dataset:", inp_dataset #for test


        inter_arrivals=[[]]
        acc_id=[inp_dataset[0][0]]
        user_id=[inp_dataset[0][2]]
        for i in range (1,len(inp_dataset)):
            if inp_dataset[i][0]!=inp_dataset[i-1][0]:
                inter_arrivals.append([])
                acc_id.append(inp_dataset[i][0])
                user_id.append(inp_dataset[i][2])
            else:
                inter_arrivals[len(inter_arrivals)-1].append((time.mktime(inp_dataset[i-1][1])-time.mktime(inp_dataset[i][1]))/86400)

        print "inter_arrivals: ", inter_arrivals
        print "acc_id: ",acc_id
        print "user_id: ",user_id
        #print "row_cnt ",row_cnt
        #print "len row cnt",len(row_cnt)
        #print "row_cnt_tester ",row_cnt_tester
        #print "len row tester cnt",len(row_cnt_tester)

        #input array for clustering algo
        #inter_arrival_means=[]
        #for i in range(0,len(inter_arrivals)):
        #    inter_arrival_means.append(avg(inter_arrivals[i]))
        #print "inter_arrivals mean values: ", inter_arrival_means

        #input array for clustering algo, applying filters
        inter_arrival_means=[]
        inter_arrival_cnt=[]
        index_to_remove = []
        for i in range(0,len(inter_arrivals)):
            inter_arrival_cnt.append(len(inter_arrivals[i]))
            if (avg(inter_arrivals[i])<180 and len(inter_arrivals[i])<21): #apply two filters
                inter_arrival_means.append(avg(inter_arrivals[i]))
            else:
                index_to_remove.append(i)

        removed_index_cnt = 0
        for i in index_to_remove:
            inter_arrivals.pop(i-removed_index_cnt)
            acc_id.pop(i-removed_index_cnt)
            user_id.pop(i-removed_index_cnt)
            removed_index_cnt +=1
        #print "inter_arrival_cnt",inter_arrival_cnt
        #print("len(interarrival cnt)",len(inter_arrival_cnt))

        ## Bowen Huang 04-27-2016
        global dimentionality
        dimentionality = 1
        #cluster_proc is a list of lists. Inner lists store clusters of each iteration of hierarchical clustering
        cluster_proc = [[]]
        #initializing the heap in the beginning
        init_clusters = kmeans_result(inter_arrival_means,8) #num_of_clusters=8
        heap=heap_init_after_kmeans(init_clusters,inter_arrival_means)
        print("-----------------------------")
        #print "heap_init_after_kmeans:",heap
        print "len(heap):",len(heap)
        cluster_proc[0]=init_clusters
        #for i in range(0,len(inter_arrival_means)):
            #cluster_proc[0].append([i])


        #main loop implementing clustering process
        #while (len(cluster_proc)<len(inter_arrival_means)):
        while (len(cluster_proc[len(cluster_proc)-1])>1):
            next_cluster_proc=heap_root_extract(heap,cluster_proc[len(cluster_proc)-1],inter_arrival_means)
            if next_cluster_proc!=[]:
                cluster_proc.append(next_cluster_proc)
                #print "now len(cluster_proc) is: ",len(cluster_proc)
        print "cluster_proc:", cluster_proc

        #each category format : [[id of people in the category based on sorted input .csv file],
        #                         avg inter_arrival times for the category in terms of days ]

        #k_value for number of clusters:
        # this value should be determined by a separate function
        k_value = 7
        #k_value = determine_k_value(cluster_proc,inter_arrival_means)

        categories=[]
        for i in range(0,k_value):
            temp_clust = sorted(list(set(cluster_proc[len(cluster_proc)-k_value][i])))
            temp_class=0
            temp_total_inter_arrivals=0
            for j in temp_clust:
                temp_class += inter_arrival_means[j]*len(inter_arrivals[j]) #weighted avg
                temp_total_inter_arrivals += len(inter_arrivals[j]) #weighted avg
            categories.append([temp_clust,temp_class/temp_total_inter_arrivals])

            #categories.append([temp,avg])
        print
        print "categories: ", categories
        print "len(categories)",len(categories)


        #plot categories:
        cat_size=[0]*len(categories)
        labels=[' ']*len(categories)
        fig = plt.figure()
        #colors=cm.Set1(np.arange(len(categories))/(1.0*len(categories)))
        for i in range(0,len(categories)):
             cat_size[i]=len(categories[i][0])
             labels[i]="category "+str(i)+" : Account IDs with average inter-arrival times of "+str(int(categories[i][1]))+" days"
        patches,texts = plt.pie(cat_size, shadow=True, startangle=140)
        fontP = FontProperties()
        fontP.set_size('small')
        plt.legend(patches,labels, prop=fontP)
        plt.axis('equal')
        save_as='./app/static/img/cat_result/cat_share.png'
        plt.savefig(save_as)
        plt.show(block=False)
        plt.close(fig)

        self.inp_dataset = inp_dataset
        self.inter_arrivals = inter_arrivals
        self.acc_id = acc_id
        self.user_id = user_id
        self.inter_arrival_means = inter_arrival_means
        self.inter_arrival_cnt = inter_arrival_cnt
        self.index_to_remove = index_to_remove
        self.categories = categories

    #### categorize END



