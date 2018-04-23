import numpy

"""
This function computes the prediction matrix using technique Matrix factorization. Since we cannot use this method directly on implicit datasets, the confidence/preference framework is implimented. For more information about how the method works refer the link below:

https://ieeexplore.ieee.org/document/4781121/
"""
def collaborativeFilteringOnImplicitDataset(utility_matrix,number_of_factors=2,learning_rate = 0.01,regularization=0.01,number_of_iterations=10,confidence_value = 20):
    users, pods = utility_matrix.shape
	
    r=number_of_factors                			#number of latent factors
	
    ita=learning_rate            				#learning rate
	
    beta=regularization          				#regularization constant
	
    epoch=number_of_iterations           		#number of iterations
	
    alpha = confidence_value         			#value in confidence equation

    # Initialize latent factor matrice
    P = numpy.random.normal(scale=1.0/r, size=(users, r))
    Q = numpy.random.normal(scale=1.0/r, size=(pods, r))
    confidence = numpy.zeros((users, pods))
    preference = numpy.zeros((users, pods))
    
    #create training data    
    training_data = []
    for i in range(users):
        for j in range(pods):
            if utility_matrix[i][j] > 0:
                training_data.append((i,j))
                preference[i][j] = 1.0
                confidence[i][j] = 1.0 + alpha*utility_matrix[i][j]
    
    cost_per_iteration = []    
    for k in range(epoch):
        numpy.random.shuffle(training_data)
        
        ### Stocastic Gradient Descent
        for i,j in training_data:
            predicted_rating = numpy.dot(P[i, :],Q[j, :].T)
            error = preference[i][j] - predicted_rating
            
            P[i, :] += (2*ita*confidence[i][j]*error*Q[j, :] - ita*beta*P[i, :])
            Q[j, :] += (2*ita*confidence[i][j]*error*P[i, :] - ita*beta*Q[j, :])
    
        ### SSE
        # finding value of J(w) i.e. optimization function
        x_list, y_list = utility_matrix.nonzero()
        predicted = numpy.dot(P,Q.T)
        error = 0
        for x, y in zip(x_list, y_list):
            error += confidence[x][y]*pow(preference[x][y] - predicted[x][y], 2)
        numpy.sqrt(error)
        cost_per_iteration.append((k,error))
    
    prediction = numpy.dot(P,Q.T)
    return prediction,cost_per_iteration

"""
Evaluation metric is "Expected Percentile Rank". Check out above mentioned paper to know more about it.
"""
def evaluate(prediction,test):
                
    numerator = 0
    denominator = 0
            
    for j in range(len(test)):
        sorted_indexes = list(prediction[j].argsort()[::-1])
        for i in range(len(test[j])):
            if test[j][i]!=0:
                #print test[user][i]
                denominator+=test[j][i]
                k = sorted_indexes.index(i)
                percentile = float(k)/(len(sorted_indexes)-1)*100
                numerator += percentile*test[j][i]
    return float(numerator)/float(denominator)
