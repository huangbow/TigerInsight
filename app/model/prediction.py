from categories import Category
import time
import math
#from scipy.stats import norm
from scipy.stats import expon
#from scipy import stats
from sklearn.neighbors import KernelDensity
import matplotlib.pyplot as plt
import numpy as np


#The function for estimation of variance of a gaussian distribution
def gauss_cat_var(inter_arrivals,categories):
    var = [0]*len(categories) #variance vector
    for i in range(0,len(categories)):
        temp_var = 0
        num_of_samples = 0
        for j in range(0,len(categories[i][0])):
            current_index = categories[i][0][j]
            for k in range(0,len(inter_arrivals[current_index])):
                temp_var += pow((inter_arrivals[current_index][k] -categories[i][1]),2)
                num_of_samples += 1
        var[i] = temp_var/num_of_samples #indexing is same as categories array
        #print ("num of sample:",num_of_samples)
    return var

def cat_mean(inter_arrivals,categories):
    mean = [0]*len(categories)
    for i in range(0,len(categories)):
        temp_mean = 0
        num_of_samples = 0
        for j in range(0,len(categories[i][0])):
            current_index = categories[i][0][j]
            for k in range(0,len(inter_arrivals[current_index])):
                temp_mean += inter_arrivals[current_index][k]
                num_of_samples += 1
        mean[i] = temp_mean/num_of_samples #indexing is same as categories array
    return mean

def exp_rate_param_estimate(sample_means):
    rate_param = [0]*len(sample_means)
    for i in range(0,len(sample_means)):
        rate_param[i] = 1/sample_means[i]
    return rate_param

# returns all interarrival samples for one category as a list of lists for kde input
def extract_cat_samples(inter_arrivals,categories,cat_index):
    cat_samples=[]
    for i in range(0,len(categories[cat_index][0])):
        current_index = categories[cat_index][0][i]
        for k in range(0,len(inter_arrivals[current_index])):
              cat_samples.append([inter_arrivals[current_index][k]])#list of lists for sklearn
    return cat_samples


def extract_last_visit(inp_dataset,inter_arrivals,inter_arrival_cnt,user_index):#user_index based on labels in categories vector
    current_row = 0 #current element in inp_dataset list
    for i in range(0,user_index):
        current_row += inter_arrival_cnt[i]+1
    return inp_dataset[current_row][1]

def last_visit_elapsed(inp_dataset,inter_arrivals,inter_arrival_cnt,user_id,time_now):#user_id: list of all user_ids
    last_visit_elapsed=[0]*len(inter_arrivals) #array for all user_id's indicating time elapsed from the last visit
    for i in range(0,len(inter_arrivals)):
        last_visit_elapsed[i]= (time_now - time.mktime(extract_last_visit(inp_dataset,inter_arrivals,inter_arrival_cnt,user_id[i])))/86400
    return last_visit_elapsed

def combine_inner_lists(two_dim_list): #combine inner lists inside a list
    result=[]
    for i in range(0,len(two_dim_list)):
        for j in range(0,len(two_dim_list[i])):
            result.append(two_dim_list[i][j])
    return result

#returns numpy compatible sparse matrix for scikit learn functions' input arguments
def np_matrix(input_list):
    output_list=[0]*len(input_list)
    for i in range(0,len(input_list)):
        output_list[i] = [input_list[i]]
    return np.asarray(output_list)

def kde_integrate(kde,t_elapsed,step_size):
    num_of_points = int(1.0*t_elapsed/step_size) #(for integration = total points in the interval - 1)
    Sum = 0
    t= 0
    for i in range(0,num_of_points):
        t = i*step_size
        Sum += step_size*np.exp(kde.score(np.asarray(t)))
    return Sum

#returns maximum value in each cluster (on avg of inter-arrivals for each person), for defining range of kde function
#def max_interarrival_mean(categories,input,cat_index):
#    max = input[categories[cat_index][0][0]]
#    for i in range(1,len(categories[cat_index][0])):
#        if input[categories[cat_index][0][i]]>max:
#            max = input[categories[cat_index][0][i]]
#    return max

#returns maximum value in each cluster (on all inter-arrival), for defining range of kde function
def max_interarrival_mean(categories,inter_arrivals,cat_index):
    max = 0
    for p_index in categories[cat_index][0]:
        for i in range(0,len(inter_arrivals[p_index])):
            if inter_arrivals[p_index][i]>max:
                max = inter_arrivals[p_index][i]
    return max

#visualization of PDFs; returning KDEs
def KDE_plt(categories,inter_arrivals):
    KDEs = []
    for i in range(0,len(categories)):

        X = np.asarray(extract_cat_samples(inter_arrivals,categories,i))#for single inter-arrivals in a category
        #X = np_matrix(categories[i][0])#for avg(inter-arrival)/person in a category
        kde = KernelDensity(kernel='gaussian', bandwidth=4).fit(X)
        KDEs.append(kde) #to use for prob_return()
        max_sample = max_interarrival_mean(categories,inter_arrivals,i)
        X_plot = np.linspace(0,1.5*max_sample,2000)[:, np.newaxis]
        log_dens = kde.score_samples(X_plot)

        plt.figure(i)
        plt.plot(X_plot[:, 0], np.exp(log_dens), '-',label="kernel = '{0}'".format('gaussian'))
            #plt.draw()
            #plt.pause(0.001)
        #plt.title("Non-Parametric Density Estimation for category=%s Visitors"%(i))
        plt.hist(combine_inner_lists(extract_cat_samples(inter_arrivals,categories,i)),bins=40,normed=1,color="cyan",alpha=.3,label="histogram") #alpha, from 0 (transparent) to 1 (opaque)
       # plt.hist(np.asarray(categories[i][0]),bins=40,normed=1,color="cyan",alpha=.3,label="histogram") #alpha, from 0 (transparent) to 1 (opaque)
        plt.xlabel("inter-arrival time (days)")
        plt.ylabel("PDF")
        plt.legend()
        save_as='./app/static/img/cat_result/kde/kdeplt_cat'+str(i)+'.png' # dump result into kde folder
        plt.savefig(save_as)
        plt.show(block=False)
        plt.close(plt.figure(i))
    return KDEs

# for parametric model of inter-arrival times, exponential distribution is the correct choice.(explanation in report)
# Exponential distribution have a rate param, lambda, which its MLE estimation is : lambda = 1/mean(x)
def MLE_plt(categories,inter_arrivals,inter_arrival_means):
    cat_means = cat_mean(inter_arrivals,categories)
    for i in range(0,len(categories)):

        #X = np.asarray(extract_cat_samples(categories.inter_arrivals,categories.categories,i))#for single inter-arrivals in a category
        #X = np_matrix(categories.categories[i][0])#for avg(inter-arrival)/person in a category
        data = [0]*len(categories[i][0])
        for j in range(0,len(categories[i][0])):
            data.append(inter_arrival_means[categories[i][0][j]])
        X = np.asarray(data)
        param = expon.fit(X) # distribution fitting
        sample_mean = cat_means[i]
        #rate_param = 1.0/sample_mean
        #fitted_pdf = expon.pdf(X,scale = 1/rate_param)
        # rate_param_estimate = exp_rate_param_estimate(sample_means)
        max_sample = max_interarrival_mean(categories,inter_arrivals,i)
        X_plot = np.linspace(0,2*sample_mean,2000)[:, np.newaxis]
        fitted_pdf = expon.pdf(X_plot,loc=param[0],scale=param[1])
        # Generate the pdf (fitted distribution)

        #kde = KernelDensity(kernel='gaussian', bandwidth=4).fit(X)
        #KDEs.append(kde) #to use for prob_return()
        #max_sample = max_interarrival_mean(categories.categories,categories.inter_arrivals,i)
        #X_plot = np.linspace(0,1.5*max_sample,2000)[:, np.newaxis]
        #log_dens = kde.score_samples(X_plot)

        fig = plt.figure()
        #plt.plot(X_plot[:, 0], np.exp(log_dens), '-',label="kernel = '{0}'".format('gaussian'))
        plt.plot(X_plot[:, 0],fitted_pdf,"red",label="Estimated Exponential Dist",linestyle="dashed", linewidth=1.5)
            #plt.draw()
            #plt.pause(0.001)
        plt.title("Parametric MLE (exponential distribution) for category=%s Visitors"%(i))
        plt.hist(X,bins=40,normed=1,color="cyan",alpha=.3,label="histogram") #alpha, from 0 (transparent) to 1 (opaque)
        #plt.hist(combine_inner_lists(extract_cat_samples(categories.inter_arrivals,categories.categories,i)),bins=40,normed=1,color="cyan",alpha=.3,label="histogram") #alpha, from 0 (transparent) to 1 (opaque)
        #plt.hist(np.asarray(categories[i][0]),bins=40,normed=1,color="cyan",alpha=.3,label="histogram") #alpha, from 0 (transparent) to 1 (opaque)
        plt.xlabel("inter-arrival time (days)")
        plt.ylabel("PDF")
        plt.legend()
        save_as='./app/static/img/cat_result/mle/mleplt_cat'+str(i)+'.png' # dump results into mle folder
        plt.savefig(save_as)
        plt.show(block=False)
        plt.close(fig)



class Prediction():
    """docstring for Prediction"""
    def __init__(self):
        self.category_num = 0
        


    # The Main prediction fuction, all in one
    ##     *file*                   the input data
    ##     *file_to_save_path       the path for cleaned data
    def prediction(self, file, file_to_save_path):
        ## main here: ##
        #time_now = time.mktime((2016, 4, 26, 14, 45,45,4,120,-1)) # time_now = 01_May_2015
        time_now = time.mktime(time.localtime())


        # By Bowen Huang 04-27-2016
        # Instant of class Category
        categories = Category()
        # Run categorize to obtain categories and internal results
        categories.categorize(file, file_to_save_path)

        # Assume last_visit_elapsed_variable is a global variable
        global last_visit_elapsed_variable
        last_visit_elapsed_variable = last_visit_elapsed(categories.inp_dataset,categories.inter_arrivals,categories.inter_arrival_cnt,categories.user_id,time_now)
        print
        #print "last visit elapsed:", last_visit_elapsed

        KDEs = KDE_plt(categories.categories,categories.inter_arrivals)
        MLE_plt(categories.categories,categories.inter_arrivals,categories.inter_arrival_means)

        ###recommendations####
        recoms = []
        for i in range(0,len(categories.categories)):
            num_of_recom = int(math.floor(0.01*len(categories.categories[i][0])))+1 #top 1% customers for recommendation
            temp_recom = [-1]*num_of_recom
            temp_cat = categories.categories[i][0]
            for n in range(0,num_of_recom):
                current_index=0
                #print "temp_cat_prob",temp_cat_prob
                for j in range(0,len(temp_cat)):
                    if last_visit_elapsed_variable[temp_cat[j]]>last_visit_elapsed_variable[temp_cat[current_index]]:
                        # print "here for j= ",j
                        current_index=j
                temp_recom[n]=temp_cat[current_index]
                temp_cat.pop(current_index)
            recoms.append(temp_recom)

        print "The top 1 percent customers to recommend for target marketing:"
        print
        fh = open("./uploads/target_selection.txt", "w")
        for i in range(0,len(recoms)):
            for j in range(0,len(recoms[i])):#format in each line: (acc_id,category,priority)
                fh.writelines(str(categories.acc_id[recoms[i][j]])+","+str(i)+","+str(j+1))
                fh.write("\n")
                print "Account ID",categories.acc_id[recoms[i][j]],"has priority", j+1," in customer category", i
            print


        # store the number of categories
        self.category_num = len(categories.categories)


# For Test
# def main():
#     prediction()


# if __name__ == '__main__':
#     main()
# Test END


# prob_not_return = [[]]*len(categories.categories)#form:[for all categories store: [customer_index,prob.]s]
# for i in range(0,len(categories.categories)):
#     temp_p=[]
#     #temp_i=[]
#     for j in range(0,len(categories.categories[i][0])):
#         customer_index = categories.categories[i][0][j]
#         #prob_return[i].append([customer_index, 1 - kde_integrate(kde,last_visit_elapsed[customer_index],0.01)])
#         temp_p.append([customer_index,kde_integrate(KDEs[i],last_visit_elapsed[customer_index],0.05)])
#         #temp_i.append(customer_index)
#     prob_not_return[i]=temp_p
#     #index = temp_i

# print "prob_not_return():",prob_not_return
# print
# print
# print "Assuming that the application was run on 05/01/2015 for the same input data:"
# print
# for i in range(0,len(prob_not_return)):
#     print "For customers from category ",i+1,", we have: "
#     for j in range(0,len(prob_not_return[i])):
#         #customer_index = prob_not_return[i][j][0]
#         print "for customer ",prob_not_return[i][j][0],", P(NOT return in the future|time elapsed from last visit)=",prob_not_return[i][j][1]
#     print "---------------------------------------------------------"


# recoms = []
# for i in range(0,len(prob_not_return)):
#     num_of_recom = int(math.floor(0.01*len(prob_not_return[i])))+3 #top 1% customers for recomendation
#     temp_recom = [-1]*num_of_recom
#     temp_cat_prob = prob_not_return[i]
#     for n in range(0,num_of_recom):
#         temp_max = [-1,0.0]
#         current_index=-1
#         #print "temp_cat_prob",temp_cat_prob
#         for j in range(0,len(temp_cat_prob)):
#             if temp_cat_prob[j][1]>temp_max[1] or last_visit_elapsed[temp_cat_prob[j][0]]>last_visit_elapsed[temp_max[0]]:
#                 # print "here for j= ",j
#                 temp_max=temp_cat_prob[j]
#                 current_index=j
#         temp_recom[n]=temp_cat_prob[current_index]
#         temp_cat_prob.pop(current_index)
#     recoms.append(temp_recom)

# print recoms
# #for i in range(0,len(recoms)):
#     #for j in range(0,len(recoms[i])):
#         #print "Account ID",categories.acc_id[recoms[i][j][]]



#print "sum: ",Sum
#print "Pr(return in the future|time elapsed)= ", 1.0-Sum

#print "kde.score", np.exp(kde.score(np.asarray(80)))
#print "kde.score_samples", np.exp(kde.score_samples(np.asarray(80)))






# rate_param_estimate = exp_rate_param_estimate(sample_means)


#x = np.linspace(cat_mean_estimate[1]-3*cat_var_estimate[1],cat_mean_estimate[1]+3*cat_var_estimate[1],100)
    #x = np.linspace(0,2*sample_means[i],100)
    # Generate the pdf (fitted distribution)
    #fitted_pdf = expon.pdf(x,scale = rate_param_estimate[1])

    # Generate the pdf (normal distribution non fitted)
    #normal_pdf = norm.pdf(x)# std normal dist: mu=0, sigma=1
    #fitted_pdf= stats.gaussian_kde(extract_cat_samples(categories.inter_arrivals,categories.categories,1))


#print "cat 1 samples:",extract_cat_samples(categories.inter_arrivals,categories.categories,1)
    # Type help(plot) for a ton of information on pyplot
    #plt.plot(x,fitted_pdf,"red",label="Estimated Exponential Dist",linestyle="dashed", linewidth=1.5)
    #plt.plot(x,normal_pdf,"blue",label="Standard Normal Dist", linewidth=1.5)

#plt.title("Gaussian Density Estimation of inter-arrival time Using MLE for Weekly Visitors")


#for Gaussian MLE
#print "gauss_mean_estimate: ",sample_means#
#cat_var_estimate = gauss_cat_var(categories.inter_arrivals,categories.categories)




