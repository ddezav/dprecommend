import os
import csv
import sys
import re

from surprise import Dataset
from surprise import Reader

from collections import defaultdict
import numpy as np
import pandas as pd

class MovieLens:

    movieID_to_name = {}
    name_to_movieID = {}
    ratingsPath = './data/ratings.csv'
    moviesPath = './data/oas.csv'
    
    def actualizarRatings(self):
        import mysql.connector

        mydb = mysql.connector.connect(
          host="173.208.198.3",
          user="unsaelors_elors",
          password="6kda(i$qJ4%^",
          database="unsaelors_4"
        )
        mycursor = mydb.cursor()

        #sql = "SELECT est.id,oaps.oa_id,oapsd.valoracion FROM `OAPersonaSesionDatos` oapsd inner join OAPersonaSesions oaps on oapsd.oapersonasesion_id=oaps.id inner join Estudiantes est on est.Persona_id = oaps.persona_id where oapsd.valoracion >0 UNION select idEstudiante,idTemaOA,valoracion from DatosTemaOA where valoracion>0"
        sql = "SELECT est.id,oaps.oa_id,oapsd.valoracion FROM `OAPersonaSesionDatos` oapsd inner join OAPersonaSesions oaps on oapsd.oapersonasesion_id=oaps.id inner join Estudiantes est on est.Persona_id = oaps.persona_id where oapsd.valoracion >0"
        mycursor.execute(sql)
        list_of_tuples = mycursor.fetchall()

        df = pd.DataFrame(list_of_tuples,columns = ['idEstudiante', 'idTemaOA','valoracion'])
        
        df.to_csv('./data/ratings.csv',index=False)

    def loadMovieLensLatestSmall(self):

        # Look for files relative to the directory we are running from
        #os.chdir(os.path.dirname(sys.argv[0]))

        ratingsDataset = 0
        self.movieID_to_name = {}
        self.name_to_movieID = {}

        reader = Reader(sep=',', skip_lines=1)

        ratingsDataset = Dataset.load_from_file(file_path=self.ratingsPath, reader=reader)

        with open(self.moviesPath, newline='') as csvfile:
                movieReader = csv.reader(csvfile)
                next(movieReader)  #Skip header line
                for row in movieReader:
                    movieID = int(row[0])
                    movieName = row[1]
                    self.movieID_to_name[movieID] = movieName
                    self.name_to_movieID[movieName] = movieID

        return ratingsDataset

    def getUserRatings(self, user):
        userRatings = []
        hitUser = False
        with open(self.ratingsPath, newline='') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                userID = int(row[0])
                if (user == userID):
                    movieID = int(row[1])
                    rating = float(row[2])
                    userRatings.append((movieID, rating))
                    hitUser = True
                if (hitUser and (user != userID)):
                    break

        return userRatings

    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratingsPath, newline='') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                movieID = int(row[1])
                ratings[movieID] += 1
        rank = 1
        for movieID, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[movieID] = rank
            rank += 1
        return rankings
    def getKeyWords(self):
        df_oas =pd.read_csv(self.moviesPath,encoding='latin-1',delimiter=',')
        return df_oas

    def getMovieName(self, movieID):
        if movieID in self.movieID_to_name:
            return self.movieID_to_name[movieID]
        else:
            return ""
        
    def getMovieID(self, movieName):
        if movieName in self.name_to_movieID:
            return self.name_to_movieID[movieName]
        else:
            return 0