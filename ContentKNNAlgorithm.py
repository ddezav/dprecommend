# -*- coding: utf-8 -*-
"""
Created on Fri May  4 13:08:25 2018

@author: Frank
"""

from surprise import AlgoBase
from surprise import PredictionImpossible
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
        self.w2v= KeyedVectors.load_word2vec_format("modelowithpretrainded3.vec",binary=False)


    def fit(self,trainset):
        AlgoBase.fit(self,trainset)
        ml = MovieLens()
        df_oas = ml.getKeyWords()

        self.similarities = np.zeros((trainset.n_items,trainset.n_items))
        for i in range(self.trainset.n_items):
            for j in range(i+1,self.trainset.n_items):
                idmovie1 = int(self.trainset.to_raw_iid(i))
                idmovie2 = int(self.trainset.to_raw_iid(j))
                self.similarities[i][j] = self.computeSimilarity(idmovie1,idmovie2,df_oas)
                self.similarities[j][i] = self.similarities[i][j]

        np.savetxt("foo.csv", self.similarities, delimiter=",")
        return self
    
    def normalize(s):
        replace = (("á","a"),
            ("é","e"),
            ("í","i"),
            ("ó","o"),
            ("ú","u"),
            ("ñ","n"),
            ("Á","A"),
            ("É","E"),
            ("Í","I"),
            ("Ó","O"),
            ("Ú","U"),
            ("Ñ","N"))
        for a, b in replace:
            s= s.replace(a,b).replace(a.upper(),b.upper())
        return s

    def computeSimilarity(self,idoa1,idoa2,df_oas):
        #GET KEYWORDS FROM IDOA1
        kw_oa1 = df_oas.iloc[idoa1,7]
        list_kw_oa1 = ContentKNNAlgorithm.normalize(str(kw_oa1)).lower().split(",")
        list_kw_oa1 = (' '.join(list_kw_oa1)).split(" ")
        #GET KEYWORDS FROM IDOA2
        kw_oa2 = df_oas.iloc[idoa2,7]
        list_kw_oa2 = ContentKNNAlgorithm.normalize(str(kw_oa2)).lower().split(",")
        list_kw_oa2 = (' '.join(list_kw_oa2)).split(" ")
        
        result = 0.0

        for i in range(len(list_kw_oa1)):
            for j in range(len(list_kw_oa2)):
                try:
                    result+=(self.w2v.similarity(list_kw_oa1[i], list_kw_oa2[j]))
                except:
                    continue
        return result        


    def estimate(self, u, i):
        
        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unkown.')
        
        # Build up similarity scores between this item and everything the user rated
        neighbors = []
        for rating in self.trainset.ur[u]:
            genreSimilarity = self.similarities[i,rating[0]]
            neighbors.append( (genreSimilarity, rating[1]) )
        
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
    