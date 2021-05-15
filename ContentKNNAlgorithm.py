# -*- coding: utf-8 -*-
"""
Created on Fri May  4 13:08:25 2018

@author: Frank
"""

from surprise import AlgoBase
from surprise import PredictionImpossible
from sklearn.metrics.pairwise import cosine_similarity
from MovieLens import MovieLens
import numpy as np
import heapq
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
import math
class ContentKNNAlgorithm(AlgoBase):

    def __init__(self, k=10, sim_options={}):
        AlgoBase.__init__(self)
        self.k = k
        #create the file csv
        #get array from file csv 
        #id_oa | latent_X | number of cluster 
        
    def setOas(self,arr):
        self.oas = arr
    def fit(self,trainset):
        AlgoBase.fit(self,trainset)
        ml = MovieLens()

        self.similarities = np.zeros((trainset.n_items,trainset.n_items))
        for i in range(self.trainset.n_items):
            for j in range(i+1,self.trainset.n_items):
                idmovie1 = int(self.trainset.to_raw_iid(i))
                idmovie2 = int(self.trainset.to_raw_iid(j))
                self.similarities[i][j] = self.computeSimilarity(idmovie1,idmovie2)
                self.similarities[j][i] = self.similarities[i][j]

        np.savetxt("foo.csv", self.similarities, delimiter=",")
        return self
    
    def computeSimilarity(self,idoa1,idoa2):
        row_oa1 = self.oas[self.oas[:,0]==idoa1]

        row_oa2 = self.oas[self.oas[:,0]==idoa2]

        #GET LATENT_X FROM IDOA1
        latent_oa1 = row_oa1[:,1:-1]
        #GET LATENT_X FROM IDOA2
        latent_oa2 = row_oa2[:,1:-1]
        
        matrix_cosine= np.array(cosine_similarity(latent_oa1,latent_oa2))
                  
        #apply cosine metric or another
        return np.average(matrix_cosine) 

    #revisar el estimate para calcular 
    def estimate(self, u, i):
        
        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unkown.')
        
        # Build up similarity scores between this item and everything the user rated
        neighbors = []

        cluster_item_i = self.oas[self.oas[:,0]==i][0][-1]
        for rating in self.trainset.ur[u]:
            #get "m" oas that belongs to cluster of oa "i"
            similar_oas = self.oas[self.oas[:,-1]==cluster_item_i]
            for similar_idoa in similar_oas:
                similitud_oas = self.similarities[similar_idoa,rating[0]]
                neighbors.append( (similitud_oas, rating[1]) )
        
        # Extract the top-K most-similar ratings
        k_neighbors = heapq.nlargest(self.k, neighbors, key=lambda t: t[0])
        
        # Compute average sim score of K neighbors weighted by user ratings
        simTotal = weightedSum = 0
        for (simScore, rating) in k_neighbors:
            if (simScore > 0):
                simTotal += simScore
                weightedSum += simScore * rating
            
        if (simTotal == 0):
            raise PredictionImpossible('No neighbors')

        predictedRating = weightedSum / simTotal

        return predictedRating
    