
import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import functools
import time
import matplotlib.pyplot as plt

###################################
########### STATISTIQUES ##########
###################################

def nbPartiesGagnees(m1, m2):
    victoiresE1 = 0
    victoiresE2 = 0
    for i in range(len(m1)):
        if m1[i] < m2[i]:
            victoiresE1 += 1
        elif m2[i] < m1[i]:
            victoiresE2 += 1
    return victoiresE1, victoiresE2

###################################
########### L'Equipe 1 a plus de liberté pour se mouvoir autour de ses objectifs.
########### L'Equipe qui commence peut ou non avoir un avantage en fonction de la stratégie employée et de la stratégie adverse.
###################################

####    Strat 1 VS Strat 1
####    Equipe 1 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s1VSs1b = np.array(([88, 76, 74, 80, 78, 98, 74, 90, 98, 90, 98, 74, 78, 80, 76, 88, 90, 80, 86, 102, 74, 86, 78, 74, 74, 74, 78, 90, 76, 74, 74, 92, 
86, 88, 88, 78, 86, 78, 90, 78, 92, 78, 80, 88, 80, 90, 88, 86, 74, 80, 90, 84, 98, 74, 86, 102, 90, 78, 74, 88, 98, 74, 98, 74, 88, 80, 90, 78, 74, 90, 
74, 86, 78, 74, 78, 74, 78, 78, 78, 88, 88, 88, 86, 92, 90, 86, 80, 92, 90, 84, 88, 88, 86, 78, 98, 86, 78, 80, 80, 78]))
#print("Moyenne Equipe 1 : ", e1s1VSs1b.mean()) # 83.6


#Total sur  100  games pour l'Equipe 2 :
e2s1VSs1f = np.array(([82, 102, 82, 80, 78, 100, 82, 84, 78, 90, 78, 80, 74, 90, 102, 82, 90, 74, 94, 72, 82, 94, 74, 94, 94, 96, 100, 90, 102, 80, 80, 90, 
94, 82, 84, 78, 94, 74, 74, 78, 80, 84, 90, 84, 80, 88, 84, 76, 96, 90, 74, 84, 100, 96, 94, 72, 74, 78, 96, 84, 100, 96, 78, 94, 82, 74, 122, 74, 82, 90, 
80, 94, 100, 80, 88, 82, 74, 78, 76, 82, 84, 84, 94, 90, 90, 94, 74, 90, 74, 84, 80, 84, 94, 76, 78, 76, 100, 90, 74, 78]))
#print("Moyenne Equipe 2 : ", e2s1VSs1f.mean()) # 85.5

# v1, v2 = nbPartiesGagnees(e1s1VSs1b, e2s1VSs1f)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 43
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 42

########## GRAPHIQUE ##########
# plt.plot(range(100), e1s1VSs1b, '.r')
# plt.plot(range(100), e2s1VSs1f, '.b')
# plt.xlabel("Partie")
# plt.ylabel("Score (minimum visé)")
# plt.show()

####    Strat 1 VS Strat 1
####    Equipe 2 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s1VSs1f = np.array(([90, 84, 78, 84, 82, 90, 92, 90, 92, 96, 82, 78, 80, 82, 74, 80, 82, 74, 96, 80, 96, 96, 90, 80, 84, 82, 82, 80, 78, 78, 76, 86, 80, 
82, 88, 84, 74, 96, 84, 80, 78, 90, 90, 90, 90, 88, 92, 74, 78, 82, 82, 80, 82, 80, 84, 88, 74, 74, 90, 82, 78, 78, 78, 88, 76, 80, 80, 84, 80, 74, 78, 84, 
84, 86, 80, 78, 76, 84, 86, 78, 78, 88, 80, 80, 78, 92, 76, 86, 82, 86, 96, 74, 90, 82, 92, 86, 74, 96, 76, 76]))
#print("Moyenne Equipe 1 : ", e1s1VSs1f.mean()) # 83.1

#Total sur  100  games pour l'Equipe 2 :
e2s1VSs1b = np.array(([90, 80, 76, 80, 76, 74, 90, 106, 90, 84, 76, 78, 90, 92, 94, 78, 92, 84, 90, 74, 90, 84, 90, 78, 80, 76, 76, 90, 78, 76, 102, 78, 74, 
76, 80, 80, 84, 90, 80, 82, 96, 74, 106, 90, 90, 80, 80, 84, 76, 76, 92, 90, 92, 74, 80, 80, 94, 76, 116, 76, 76, 78, 76, 80, 102, 90, 90, 114, 90, 76, 74, 
114, 80, 78, 74, 76, 96, 80, 88, 74, 74, 80, 78, 82, 74, 90, 96, 88, 76, 94, 84, 78, 80, 92, 90, 88, 92, 90, 102, 96]))
#print("Moyenne Equipe 2 : ", e2s1VSs1b.mean()) # 84.9

# v1, v2 = nbPartiesGagnees(e1s1VSs1f, e2s1VSs1b)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 38
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 55

############# Conclusion ############
###### L'Equipe 1 a ici toujours l'avantage, mais l'Equipe 2 a amélioré ses performances :
######      Être en haut est plus avantageux que de commencer mais commencer aiderait quand même un peu.
#########################


####    Strat 1 VS Strat 2
####    Equipe 1 Strat 1 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s1VSs2b = np.array(([86, 86, 82, 82, 98, 80, 94, 92, 80, 92, 92, 90, 80, 94, 98, 92, 80, 86, 98, 84, 96, 92, 86, 86, 80, 94, 96, 80, 86, 80, 94, 90, 80, 98, 
80, 86, 80, 86, 82, 80, 98, 96, 82, 84, 96, 90, 80, 90, 92, 80, 80, 90, 80, 96, 86, 80, 88, 90, 98, 82, 98, 94, 94, 86, 84, 82, 80, 98, 86, 82, 86, 98, 98, 84, 
104, 90, 84, 90, 86, 80, 90, 98, 82, 86, 90, 90, 88, 96, 80, 98, 94, 94, 86, 98, 98, 86, 98, 92, 86, 92]))
#print("Moyenne Equipe 1 : ", e1s1VSs2b.mean()) # 88.6

#Total sur  100  games pour l'Equipe 2 :
e2s2VSs1f = np.array(([85, 75, 79, 79, 107, 75, 68, 75, 85, 80, 80, 85, 75, 68, 90, 89, 95, 89, 89, 68, 68, 75, 85, 85, 75, 80, 80, 95, 89, 95, 68, 68, 85, 75, 
85, 75, 85, 85, 79, 95, 75, 80, 85, 68, 68, 85, 85, 85, 80, 85, 85, 68, 75, 80, 75, 75, 80, 95, 89, 79, 90, 80, 68, 89, 79, 75, 75, 89, 85, 79, 75, 89, 107, 68, 
90, 89, 68, 68, 89, 95, 85, 89, 75, 89, 95, 85, 80, 80, 75, 90, 80, 68, 95, 107, 107, 68, 75, 89, 85, 80]))
#print("Moyenne Equipe 2 : ", e2s2VSs1f.mean()) # 82.04

# v1, v2 = nbPartiesGagnees(e1s1VSs2b, e2s2VSs1f)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 25
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 75

####    Strat 1 VS Strat 2
####    Equipe 2 Strat 2 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s1VSs2f = np.array(([80, 96, 104, 82, 82, 97, 90, 84, 92, 82, 104, 78, 91, 80, 94, 92, 92, 86, 96, 86, 80, 96, 84, 82, 104, 80, 82, 80, 91, 84, 82, 92, 86, 88, 
86, 82, 96, 80, 92, 105, 94, 86, 82, 88, 80, 97, 82, 86, 104, 92, 94, 80, 92, 91, 92, 96, 105, 86, 105, 78, 90, 104, 82, 86, 80, 90, 97, 82, 82, 86, 92, 90, 82, 
82, 78, 80, 82, 105, 84, 82, 80, 80, 80, 82, 80, 94, 82, 80, 104, 80, 84, 84, 80, 86, 82, 86, 82, 96, 86, 94]))
#print("Moyenne Equipe 1 : ", e1s1VSs2f.mean()) # 87.9

#Total sur  100  games pour l'Equipe 2 :
e2s2VSs1b = np.array(([95, 90, 85, 68, 68, 100, 90, 90, 95, 95, 85, 80, 100, 95, 75, 85, 95, 69, 68, 75, 95, 90, 90, 68, 85, 95, 68, 95, 116, 90, 68, 80, 75, 68, 
85, 80, 90, 75, 80, 116, 75, 69, 95, 68, 75, 100, 80, 69, 95, 80, 75, 95, 75, 116, 80, 68, 116, 69, 116, 80, 80, 85, 80, 95, 95, 90, 100, 68, 68, 75, 85, 80, 75, 
68, 80, 95, 68, 116, 90, 68, 95, 85, 85, 95, 85, 68, 75, 75, 85, 95, 90, 90, 95, 95, 80, 95, 95, 90, 95, 68]))
#print("Moyenne Equipe 2 : ", e2s2VSs1b.mean()) # 85.1

# v1, v2 = nbPartiesGagnees(e1s1VSs2f, e2s2VSs1b)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 43
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 55

############# Conclusion ############
###### Ici, la stratégie 2 est meilleure que la 1 mais il est aussi clair que commencer est un désavantage.
######      La strat 1 et la strat 2 préfèrent commencer lorsqu'elles s'affrontent.
#########################


####    Strat 2 VS Strat 1
####    Equipe 1 Strat 2 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s2VSs1b = np.array(([79, 75, 70, 80, 80, 71, 75, 82, 71, 86, 82, 86, 79, 82, 75, 71, 80, 75, 70, 75, 86, 82, 82, 86, 70, 82, 82, 82, 71, 70, 75, 79, 86, 76, 82, 
70, 86, 70, 80, 82, 86, 82, 70, 86, 70, 70, 70, 70, 79, 75, 79, 70, 70, 75, 70, 82, 80, 71, 76, 79, 86, 76, 82, 86, 75, 70, 70, 82, 79, 71, 79, 70, 79, 82, 82, 70, 
82, 70, 79, 79, 76, 82, 70, 86, 79, 70, 79, 86, 70, 79, 79, 70, 70, 82, 79, 82, 80, 70, 70, 86]))
#print("Moyenne Equipe 1 : ", e1s2VSs1b.mean()) # 77.3 !!

#Total sur  100  games pour l'Equipe 2 :
e2s1VSs2f = np.array(([76, 78, 90, 80, 98, 92, 78, 80, 84, 116, 78, 72, 92, 90, 86, 74, 80, 78, 78, 96, 90, 78, 94, 90, 94, 94, 78, 100, 74, 76, 100, 92, 74, 80, 
100, 76, 90, 76, 98, 78, 80, 80, 78, 90, 90, 94, 100, 76, 92, 86, 118, 94, 90, 78, 92, 76, 98, 92, 80, 92, 72, 98, 90, 74, 78, 92, 92, 94, 76, 74, 118, 76, 118, 78, 
90, 94, 76, 92, 80, 118, 80, 78, 94, 72, 76, 90, 118, 72, 100, 118, 76, 92, 100, 94, 76, 76, 80, 92, 76, 80]))
#print("Moyenne Equipe 2 : ", e2s1VSs2f.mean()) # 87.2

# v1, v2 = nbPartiesGagnees(e1s2VSs1b, e2s1VSs2f)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 73
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 24

####    Strat 2 VS Strat 1
####    Equipe 2 Strat 1 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s2VSs1f = np.array(([82, 70, 70, 70, 70, 79, 86, 86, 75, 70, 86, 70, 82, 82, 70, 75, 70, 79, 70, 84, 70, 70, 83, 83, 82, 75, 70, 82, 79, 70, 70, 75, 70, 82, 83, 79, 
82, 79, 79, 79, 70, 70, 70, 84, 70, 83, 79, 86, 86, 82, 71, 75, 70, 79, 79, 70, 70, 70, 70, 75, 70, 75, 75, 82, 70, 84, 75, 86, 83, 70, 79, 83, 79, 75, 70, 79, 86, 70, 
70, 86, 71, 75, 70, 75, 83, 70, 79, 75, 79, 79, 79, 86, 75, 75, 86, 79, 75, 79, 83, 70]))
#print("Moyenne Equipe 1 : ", e1s2VSs1f.mean()) # 76.7

#Total sur  100  games pour l'Equipe 2 :
e2s1VSs2b = np.array(([94, 94, 76, 76, 76, 118, 76, 98, 100, 94, 74, 84, 94, 78, 92, 100, 94, 98, 94, 90, 76, 92, 76, 80, 78, 84, 94, 78, 76, 92, 76, 92, 74, 78, 76, 76, 
78, 82, 82, 94, 74, 78, 76, 90, 74, 94, 98, 90, 80, 94, 88, 84, 94, 80, 118, 92, 94, 76, 78, 82, 78, 90, 102, 78, 76, 90, 84, 112, 76, 76, 82, 76, 76, 82, 92, 98, 90, 84, 
92, 76, 88, 82, 94, 100, 76, 74, 82, 82, 94, 80, 76, 112, 102, 84, 76, 94, 102, 98, 76, 84]))
#print("Moyenne Equipe 2 : ", e2s1VSs2b.mean()) # 86.3

# v1, v2 = nbPartiesGagnees(e1s2VSs1f, e2s1VSs2b)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 78
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 22

############# Conclusion ############
###### L'Equipe 1 avec la stratégie 2 est définitivement meilleure que l'Equipe 2 qui a la stratégie 1.
######          On remarque que les deux Equipes sont meilleures lorsque l'Equipe 2 commence, probablement une coïncidence.
#########################


####    Strat 2 VS Strat 2
####    Equipe 1 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s2VSs2b = np.array(([84, 82, 87, 87, 80, 93, 81, 81, 85, 83, 93, 86, 84, 80, 86, 83, 83, 83, 72, 93, 81, 87, 93, 81, 86, 84, 80, 93, 73, 87, 81, 71, 72, 77, 72, 
87, 81, 79, 82, 87, 83, 81, 72, 83, 83, 83, 86, 83, 90, 84, 84, 81, 81, 83, 93, 72, 71, 72, 84, 72, 90, 80, 72, 72, 72, 81, 71, 84, 87, 84, 80, 79, 79, 81, 83, 72, 
83, 83, 84, 72, 84, 84, 83, 72, 87, 83, 79, 84, 81, 72, 84, 72, 80, 81, 81, 83, 79, 85, 93, 72]))
#print("Moyenne Equipe 1 : ", e1s2VSs2b.mean()) # 81.5

#Total sur  100  games pour l'Equipe 2 :
e2s2VSs2f = np.array(([114, 96, 108, 108, 81, 69, 110, 87, 103, 71, 69, 80, 78, 80, 80, 90, 71, 90, 107, 80, 78, 105, 69, 97, 80, 114, 81, 69, 98, 108, 110, 79, 107, 
90, 101, 105, 78, 89, 96, 88, 71, 110, 96, 71, 80, 71, 80, 90, 69, 115, 114, 87, 110, 80, 80, 107, 79, 96, 114, 107, 69, 80, 96, 101, 97, 110, 79, 114, 108, 114, 81, 
107, 89, 87, 79, 97, 79, 90, 78, 96, 115, 78, 90, 97, 88, 90, 107, 114, 78, 101, 115, 96, 81, 97, 110, 80, 89, 103, 69, 97]))
#print("Moyenne Equipe 2 : ", e2s2VSs2f.mean()) # 91.9

# v1, v2 = nbPartiesGagnees(e1s2VSs2b, e2s2VSs2f)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 69
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 29

####    Strat 2 VS Strat 2
####    Equipe 2 Commence
####    Echantillon 100 games

#Total sur  100  games pour l'Equipe 1 :  
e1s2VSs2f = np.array(([79, 74, 86, 95, 74, 91, 91, 77, 83, 88, 86, 76, 95, 80, 90, 74, 76, 76, 95, 74, 91, 76, 81, 91, 93, 91, 76, 76, 80, 91, 98, 90, 95, 100, 82, 
80, 88, 95, 82, 98, 88, 95, 91, 74, 82, 98, 87, 83, 100, 98, 86, 74, 98, 83, 89, 79, 77, 93, 74, 82, 83, 91, 74, 74, 82, 74, 86, 80, 80, 87, 91, 86, 77, 98, 74, 80, 
74, 95, 98, 80, 87, 74, 91, 86, 100, 79, 93, 98, 95, 81, 77, 86, 81, 93, 76, 76, 89, 90, 88, 98]))
# print("Moyenne Equipe 1 : ", e1s2VSs2f.mean()) # 85.5

#Total sur  100  games pour l'Equipe 2 :
e2s2VSs2b = np.array(([83, 76, 104, 86, 76, 90, 90, 79, 99, 79, 104, 85, 86, 75, 72, 86, 85, 85, 96, 86, 90, 75, 85, 96, 90, 90, 75, 85, 82, 96, 91, 72, 86, 89, 69, 
96, 84, 86, 85, 77, 84, 86, 96, 76, 69, 91, 79, 99, 89, 77, 104, 86, 77, 99, 83, 83, 79, 90, 76, 95, 99, 90, 76, 86, 69, 86, 104, 96, 82, 77, 96, 104, 79, 77, 86, 75, 
76, 86, 91, 75, 79, 86, 90, 104, 89, 83, 90, 77, 86, 85, 79, 104, 85, 90, 85, 85, 83, 72, 84, 77]))
# print("Moyenne Equipe 2 : ", e2s2VSs2b.mean()) # 85.6

# v1, v2 = nbPartiesGagnees(e1s2VSs2f, e2s2VSs2b)
# print("Nombre de victoires de l'Equipe 1 : ", v1) # 51
# print("Nombre de victoires de l'Equipe 2 : ", v2) # 49

############# Conclusion ############
######
######
#########################