# -*- coding: utf-8 -*-
"""
Created on Thu May  3 10:22:34 2018

@author: Frank
"""
from EvaluationData import EvaluationData
from EvaluatedAlgorithm import EvaluatedAlgorithm

class Evaluator:
    
    algorithms = []
    
    def __init__(self, dataset, rankings):
        ed = EvaluationData(dataset, rankings)
        self.dataset = ed
        
    def AddAlgorithm(self, algorithm, name):
        alg = EvaluatedAlgorithm(algorithm, name)
        self.algorithms.append(alg)
        
    def Evaluate(self, doTopN):
        results = {}
        for algorithm in self.algorithms:
            print("Evaluating ", algorithm.GetName(), "...")
            results[algorithm.GetName()] = algorithm.Evaluate(self.dataset, doTopN)

        # Print results
        print("\n")
        
        if (doTopN):
            print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                    "Algorithm", "RMSE", "MAE", "HR", "cHR", "ARHR", "Coverage", "Diversity", "Novelty"))
            for (name, metrics) in results.items():
                print("{:<10} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f}".format(
                        name, metrics["RMSE"], metrics["MAE"], metrics["HR"], metrics["cHR"], metrics["ARHR"],
                                      metrics["Coverage"], metrics["Diversity"], metrics["Novelty"]))
        else:
            print("{:<10} {:<10} {:<10}".format("Algorithm", "RMSE", "MAE"))
            for (name, metrics) in results.items():
                print("{:<10} {:<10.4f} {:<10.4f}".format(name, metrics["RMSE"], metrics["MAE"]))
                
        print("\nLegend:\n")
        print("RMSE:      Root Mean Squared Error. Lower values mean better accuracy.")
        print("MAE:       Mean Absolute Error. Lower values mean better accuracy.")
        if (doTopN):
            print("HR:        Hit Rate; how often we are able to recommend a left-out rating. Higher is better.")
            print("cHR:       Cumulative Hit Rate; hit rate, confined to ratings above a certain threshold. Higher is better.")
            print("ARHR:      Average Reciprocal Hit Rank - Hit rate that takes the ranking into account. Higher is better." )
            print("Coverage:  Ratio of users for whom recommendations above a certain threshold exist. Higher is better.")
            print("Diversity: 1-S, where S is the average similarity score between every possible pair of recommendations")
            print("           for a given user. Higher means more diverse.")
            print("Novelty:   Average popularity rank of recommended items. Higher means more novel.")
        
    def SampleTopNRecs(self, ml, testSubject=85, k=10):
        
        for algo in self.algorithms:
            print("\nUsing recommender ", algo.GetName())
            
            print("\nBuilding recommendation model...")
            trainSet = self.dataset.GetFullTrainSet()
            algo.GetAlgorithm().fit(trainSet)
            
            print("Computing recommendations...")
            testSet = self.dataset.GetAntiTestSetForUser(testSubject)
        
            predictions = algo.GetAlgorithm().test(testSet)
            
            recommendations = []
            
            print ("\nWe recommend:")
            for userID, movieID, actualRating, estimatedRating, _ in predictions:
                intMovieID = int(movieID)
                recommendations.append((intMovieID, estimatedRating))
            
            recommendations.sort(key=lambda x: x[1], reverse=True)
            
            for ratings in recommendations[:10]:
                #ml.getMovieName(
                print(ratings[0], ratings[1])

    def conexion(self):
        import mysql.connector

        mydb = mysql.connector.connect(
          host="173.208.198.3",
          user="unsaelors_elors",
          password="6kda(i$qJ4%^",
          database="unsaelors_4"
        )
        mycursor = mydb.cursor()
        return (mycursor,mydb)

    def getIDbyTable(self,mycursor,table):
        (mycursor,mydb) = self.conexion()

        sql_select = "SELECT id FROM "+table
        mycursor.execute(sql_select)
        result = mycursor.fetchall()
        lista = list()   
        for fila in result:
            lista.append(fila[0])
        return lista

    def globalRecommendation(self):
        
        (mycursor,mydb) = self.conexion()

        list_estudiantes = self.getIDbyTable(mycursor,"Estudiantes")
        list_oas = self.getIDbyTable(mycursor,"OAs")

        list_prediction = list()

        algo = self.algorithms[0]
        trainSet = self.dataset.GetFullTrainSet()
        algo.GetAlgorithm().fit(trainSet)

        for id_estudiante in list_estudiantes:
            for id_oa in list_oas:
                user = str(id_estudiante)
                item = str(id_oa)
                obj_predict = algo.GetAlgorithm().predict(user,item)
                list_prediction.append(obj_predict)
        return list_prediction
            
    def get_top_n(self,predictions,n=5):
        trainSet = self.dataset.GetFullTrainSet()
        (mycursor,mydb) = self.conexion()
        top_n = dict()

        for uid, iid, true_r, est, _ in predictions:
            top_n[uid] = list()

        for uid, iid, true_r, est, _ in predictions:            
            user_items = set([j for (j, _) in trainSet.ur[uid]])
            if iid not in user_items:
                top_n[uid].append((iid, est))
        
        sql_insert = "INSERT INTO recomendaciones (oa_id,estudiante_id) VALUES (%s,%s)"
        
        sql_update = "UPDATE recomendaciones SET oa_id=%s WHERE estudiante_id=%s"

        sql_select = "SELECT id FROM recomendaciones where estudiante_id=%s"
        # Then sort the predictions for each user and retrieve the k highest ones. 

        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]
            s=""
            for idoa,predrating in top_n[uid]:
                s+=(str(idoa)+',')
            
            s = s[0:-1]
            val = (s,uid)

            mycursor.execute(sql_select,(uid,))
            result = mycursor.fetchall()   

            if(len(result)>0):
                mycursor.execute(sql_update,val)
            else:
                mycursor.execute(sql_insert,val)
            mydb.commit()

            
            
    
    