# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme



# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----




# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()
cpt = 0

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'exAdvCoopMap'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
def main(iterations=100, Strat1=None, Strat2=None):

    #for arg in sys.argv:
    # iterations = 100 # default
    # if len(sys.argv) == 2:
    #     iterations = int(sys.argv[1])
    if (Strat1 not in range(1,5)) or (Strat2 not in range(1,5)):
        print("Il faut choisir 2 strat entre 1, 2, 3 ou 4 !")
        return
    #print ("Iterations: ")
    #print (iterations)

    init()
    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nbLignes = game.spriteBuilder.rowsize
    nbCols = game.spriteBuilder.colsize
       
    #print("lignes", nbLignes)
    #print("colonnes", nbCols)
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    score = [0]*nbPlayers
    scoreEgalite = [0]*nbPlayers
          
    # on localise tous les états initiaux (loc du joueur)
    # positions initiales des joueurs
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    #print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    # sur le layer ramassable
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
        
    # on localise tous les murs
    # sur le layer obstacle
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    def legal_position(row,col):
        # une position legale est dans la carte et pas sur un mur
        return ((row,col) not in wallStates) and row>=0 and row<nbLignes and col>=0 and col<nbCols
        
    #-------------------------------
    # Attributaion aleatoire des fioles / objectifs
    #-------------------------------
    objectifs = goalStates
    # Attribution aléatoire des fioles pour l'équipe 1
    objectifsEquipe1 = [o for o in objectifs[int(len(objectifs)/2):]]
    random.shuffle(objectifsEquipe1)
    # for j in range(len(objectifsEquipe1)):
    #     print("Objectif joueur ",j," ",objectifsEquipe1[j])
    # Attribution aléatoire des fioles pour l'équipe 2
    objectifsEquipe2 = [o for o in objectifs[:int(len(objectifs)/2)]]
    random.shuffle(objectifsEquipe2)
    #for j in range(len(objectifsEquipe2)):
    #    print("Objectif joueur ",j+len(objectifsEquipe1)," ",objectifsEquipe2[j])
    # Réassemblement des objectifs
    #print("Objectifs : ", objectifs)
    objectifs = objectifsEquipe1 + objectifsEquipe2
    #print("Objectifs reassemble : ", objectifs)

    #-------------------------------
    # Initialisation matrice d'obstacles
    #-------------------------------
    g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True  
    for w in wallStates:                       # putting False for walls
        g[w]=False
    posPlayers = initStates

    def majCollision1(g, pos):  #   Permet d'ajouter la position actuelle des joueurs comme obstacles
        for p in pos:
            g[p] = False
        return

    def majCollision2(g, pos):  #   Permet d'enlever la position actuelle des joueurs des obstacles
        for p in pos:
            g[p] = True
        return

    def majCollisionObj1(currentEquipe, currentPlayer, g):
        for p in currentEquipe:
            if p != currentPlayer:
                g[objectifs[p]] = False

    def majCollisionObj2(currentEquipe, g):
        for p in currentEquipe:
            g[objectifs[p]] = True

    #-------------------------------
    # Strat 1
    #-------------------------------
    def stratAstarRecalculTjrs(numEquipe, posPlayers, objectifsEquipe, score, scoreEgalite, g):
        """ numEquipe : 1 ou 2
            posPlayers : la position de tous les joueurs
            objectifsEquipe : les objectifs de tous les joueurs
            score : 1 si le joueur a atteint son objectif, 0 sinon (tableau)
            scoreEgalite : le nombre de déplacement effectué par chaque joueur (tableau)
            """
        currentEquipe = []
        if numEquipe == 1:
            currentEquipe = range(int(len(posPlayers)/2))
        elif numEquipe == 2:
            currentEquipe = range(int(len(posPlayers)/2), len(posPlayers))
        else:
            print("numEquipe doit être à 1 ou 2")
            return
        for playerEquipe in currentEquipe:
            print("Mon tour, joueur : ", playerEquipe, " || mon obj : ", objectifsEquipe[playerEquipe] ," || mon path : ", allPathStrat1[playerEquipe])
            if score[playerEquipe] == 1:                   # Si le joueur a déjà atteint son objectif on passe son tour
                continue
            majCollision1(g, posPlayers)        # La position des joueurs est considérée temporairement comme un obstacle
            allPathStrat1[playerEquipe] = probleme.astar(ProblemeGrid2D(posPlayers[playerEquipe], objectifsEquipe[playerEquipe], g, 'manhattan'))
            majCollision2(g, posPlayers)        # La position des joueurs est enlevée des obstacles
            row, col = allPathStrat1[playerEquipe][1]        # son déplacement 1 case plus loin
            # on met à jour la position du joueur playerEquipe1
            posPlayers[playerEquipe] = (row, col)      
            players[playerEquipe].set_rowcol(row, col)
            scoreEgalite[playerEquipe]+=1          #   On ajoute un déplacement à son score
            if (row, col) == objectifsEquipe[playerEquipe]:   # Si le joueur a atteint son objectif on met la matrice score à jour
                score[playerEquipe]+=1
                print("Le joueur ",playerEquipe," a atteint son but !")
            #game.mainiteration()
        game.mainiteration()
        return
    #-------------------------------
    # FIN   Strat 1
    #-------------------------------

    #-------------------------------
    # Strat 2
    #-------------------------------
    def stratAstarRecalculObstacle(numEquipe, posPlayers, objectifsEquipe, score, scoreEgalite, g, cptPath, cptWait, allPath):
        """ numEquipe : 1 ou 2
            posPlayers : la position de tous les joueurs
            objectifsEquipe : les objectifs de tous les joueurs
            score : 1 si le joueur a atteint son objectif, 0 sinon (tableau)
            scoreEgalite : le nombre de déplacement effectué par chaque joueur (tableau)
            """
        currentEquipe = []
        if numEquipe == 1:
            currentEquipe = range(int(len(posPlayers)/2))
        elif numEquipe == 2:
            currentEquipe = range(int(len(posPlayers)/2), len(posPlayers))
        else:
            print("numEquipe doit être à 1 ou 2")
            return
        for playerEquipe in currentEquipe:
            print("Mon tour, joueur : ", playerEquipe, " || mon obj : ", objectifsEquipe[playerEquipe] ," || mon path : ", allPath[playerEquipe])
            if score[playerEquipe] == 1:                   # Si le joueur a déjà atteint son objectif on passe son tour
                continue
            majCollision1(g, posPlayers)        # La position des joueurs est considérée temporairement comme un obstacle
            for playerEquipeBis in currentEquipe:
                if (posPlayers[playerEquipeBis] in allPath[playerEquipe]) and (posPlayers[playerEquipeBis] == objectifsEquipe[playerEquipeBis]):    #   Si un équipier est sur son objectif qui est sur le path du joueur actuel, il ne bougera pas, il faut donc que le joueur change de path
                    allPath[playerEquipe] = probleme.astar(ProblemeGrid2D(posPlayers[playerEquipe], objectifsEquipe[playerEquipe], g, 'manhattan'))   # Nouveau Path potentiel calculé avec A*
                    cptPath[playerEquipe] = 0
                    break
            if g[allPath[playerEquipe][cptPath[playerEquipe]+1]] == False:  #   Si la prochaine case de son Path est bloqué par un joueur
                # On compare le temps que prend un détour au chemin actuel
                tmpPath = probleme.astar(ProblemeGrid2D(posPlayers[playerEquipe], objectifsEquipe[playerEquipe], g, 'manhattan'))   # Nouveau Path potentiel calculé avec A*
                #### CAS PARTICULIER
                if len(tmpPath) == 2:
                    print("Exception ", posPlayers[playerEquipe])
                    cptPath[playerEquipe] = 0
                    cptWait[playerEquipe] += 1
                    majCollision2(g, posPlayers)
                    scoreEgalite[playerEquipe] += 1
                    continue
                #### FIN CAS PARTICULIER
                #### len(tmpPath) peut être = 1 si le joueur est bloqué || il faut gérer cette situation
                elif (len(tmpPath) < (len(allPath[playerEquipe])-cptPath[playerEquipe] + 1)) and (cptWait[playerEquipe] == 0) and (len(tmpPath) > 2):   # Si le joueur peut attendre mais que changer de chemin est plus rapide
                    print("Je switch ", posPlayers[playerEquipe])
                    allPath[playerEquipe] = tmpPath #   On change son chemin
                    cptPath[playerEquipe] = 0   # On avance de 1 dans ce nouveau Path
                elif ((len(tmpPath) > (len(allPath[playerEquipe])-cptPath[playerEquipe] + 1)) and (cptWait[playerEquipe] == 0)) or (len(tmpPath) == 1) or ((len(allPath[playerEquipe])-cptPath[playerEquipe]) == 2): 
                    # Si le nouveau chemin est plus long et que le joueur peut attendre
                    print("J'attends ", posPlayers[playerEquipe])
                    cptWait[playerEquipe] +=1
                    majCollision2(g, posPlayers)
                    scoreEgalite[playerEquipe] += 1
                    continue        # On passe au joueur suivant
                else:       #   Le nouveau chemin est plus long mais le joueur a déjà attendu au tour précédent
                    #rint("Je switch, j'ai pas le choix ", posPlayers[playerEquipe])
                    cptWait[playerEquipe] = 0   # Le joueur va avancer, il peut de nouveau attendre au prochain tour
                    allPath[playerEquipe] = tmpPath
                    cptPath[playerEquipe] = 0   # On avance de 1 dans ce nouveau Path
            majCollision2(g, posPlayers)        # La position des joueurs est enlevée des obstacles
            cptPath[playerEquipe]+=1
            print("Taille du path : ", len(allPath[playerEquipe])," || Taille du cptPath : ", cptPath[playerEquipe])
            row, col = allPath[playerEquipe][cptPath[playerEquipe]]        # son déplacement 1 case plus loin
            print("J'avance ",posPlayers[playerEquipe]," -> ",allPath[playerEquipe][cptPath[playerEquipe]])
            # on met à jour la position du joueur playerEquipe1
            posPlayers[playerEquipe] = (row, col)      
            players[playerEquipe].set_rowcol(row, col)
            scoreEgalite[playerEquipe]+=1          #   On ajoute un déplacement à son score
            cptWait[playerEquipe] = 0              #   Le joueur s'étant déplacer, il peut attendre si besoin à la prochaine itération
            if (row, col) == objectifsEquipe[playerEquipe]:   # Si le joueur a atteint son objectif on met la matrice score à jour
                score[playerEquipe]+=1
                print("Le joueur ",playerEquipe," a atteint son but !")
            #game.mainiteration()
        game.mainiteration()
        return
    #-------------------------------
    # FIN   Strat 2
    #-------------------------------

    #-------------------------------
    # MinMax ALGO Strat 3
    #-------------------------------
    def calculDeplacementsPossibles(posPlayers, g, numPlayer) :
        """
        renvoie un liste de (row, col) pour les places possiblement occupable par le joueur numPlayer
        """
        listMoves = []
        (rowActu, colActu) = posPlayers[numPlayer]
        if(legal_position(rowActu - 1, colActu) == True) :
            listMoves.append((rowActu - 1, colActu))
        if(legal_position(rowActu + 1, colActu) == True) :
            listMoves.append((rowActu + 1, colActu))
        if(legal_position(rowActu, colActu - 1) == True) :
            listMoves.append((rowActu, colActu - 1))
        if(legal_position(rowActu, colActu + 1) == True) :
            listMoves.append((rowActu, colActu + 1))

        listMoves.append((rowActu, colActu))       #Au choix, si le joueur peut rester sur place ou non 

        return listMoves

    def coups_possibles_equipe(numEquipe, posPlayers, g, nb_players, tab_posPlayers) : #Fonction recursive 
        """
        Sert à récupérer les coups possible pour l'équipe numEquipe au prochain tour
        rend un tableau de posPlayers
        """
        # print("Debut coups possibles equipe nb play = ", nb_players)


        currentEquipe = []
        if numEquipe == 1:
            currentEquipe = range(int(len(posPlayers)/2))
        elif numEquipe == 2:
            currentEquipe = range(int(len(posPlayers)/2), len(posPlayers))

        #if(nb_players == currentEquipe[0]) :
        if(nb_players == -1 or nb_players == len(posPlayers)/2) :
            # print("Fin coups possibles equipe, currentEquipe[0] = ", currentEquipe[0])
            tab_posPlayers.append(posPlayers)
            return posPlayers

        movesPossibles = []
        movesPossibles = calculDeplacementsPossibles(posPlayers, g, currentEquipe[nb_players - 1])
        # print("Pos de base : ", posPlayers[(currentEquipe[nb_players - 1])],"moves possibles : ", movesPossibles)

        for i in range(len(movesPossibles)) :
            (row, col) = movesPossibles[i]
            NextposPlayer = []
            for p in range(len(posPlayers)) :
                NextposPlayer.append(posPlayers[p])
            NextposPlayer[(currentEquipe[nb_players - 1])] = (row, col)
            listNextCoup = coups_possibles_equipe(numEquipe, NextposPlayer, g, nb_players - 1, tab_posPlayers)

        # print("cppossequipe : ", tab_posPlayers)        
        return tab_posPlayers

    def MinMax(numEquipe, posPlayers, objectifsEquipe, score, g, profondeur, alpha, beta):
        """ numEquipe : 1 ou 2
            posPlayers : la position de tous les joueurs
            objectifsEquipe : les objectifs de tous les joueurs
            score : 1 si le joueur a atteint son objectif, 0 sinon (tableau)
            g : matrice des obstacles
            profondeur : profondeur de recherche de MinMax
            """

        # print("Minmax : equipe = ", numEquipe,"profondeur = ", profondeur)
        currentEquipe = []
        oppositeEquipe = []
        numEquipeAdv = 0
        if numEquipe == 1:
            currentEquipe = range(int(len(posPlayers)/2))
            oppositeEquipe = range(int(len(posPlayers)/2), len(posPlayers))
            numEquipeAdv = 2
        elif numEquipe == 2:
            currentEquipe = range(int(len(posPlayers)/2), len(posPlayers))
            oppositeEquipe = range(int(len(posPlayers)/2))
            numEquipeAdv = 1


        if(profondeur == 0) :       #Fin de la pronfondeur / Branche 
            # print("Prof = 0, equipe = ", numEquipe)
            scoreEquipe = 0
            scoreAdv = 0

            for playerEquipe in currentEquipe :     #On calcule le score de l'equipe avec la distance en cases aux objectifs de chacun de joueurs de l'equipe

                majCollision1(g, posPlayers)        # La position des joueurs est considérée temporairement comme un obstacle
                allPath[playerEquipe] = probleme.astar(ProblemeGrid2D(posPlayers[playerEquipe], objectifsEquipe[playerEquipe], g, 'manhattan'))
                majCollision2(g, posPlayers)        # La position des joueurs est enlevée des obstacles
                scoreEquipe += len(allPath[playerEquipe])
                # print("Score equipe = ", scoreEquipe)

            for playerEquipe in oppositeEquipe :     #On fait pareil pour l'équipe adverse

                majCollision1(g, posPlayers)        # La position des joueurs est considérée temporairement comme un obstacle
                allPath[playerEquipe] = probleme.astar(ProblemeGrid2D(posPlayers[playerEquipe], objectifsEquipe[playerEquipe], g, 'manhattan'))
                majCollision2(g, posPlayers)        # La position des joueurs est enlevée des obstacles
                scoreAdv += len(allPath[playerEquipe])
                # print("Score adv = ", scoreAdv)


            if numEquipe == 1 :
                # print("Evaluation de la position : ", posPlayers, "\n Score = ", (scoreEquipe - scoreAdv))
                return posPlayers, (scoreEquipe - scoreAdv) 
            else : 
                # print("Evaluation de la position : ", posPlayers, "\n Score = ", (scoreAdv - scoreEquipe))
                return posPlayers, (scoreAdv - scoreEquipe)     #On renvoie dans tous les cas scoreEquipe1 - scoreEquipe2

        else :          #On doit "descendre" plus bas (pronfondeur - 1)

            #On récupère tous les coups possibles
            cp_poss_eq = coups_possibles_equipe(numEquipe, posPlayers, g, len(currentEquipe) - 1, []) #TODO
            # print("Taille cp_poss_eq :", len(cp_poss_eq), " = ", cp_poss_eq)
            score_coup_possible = []  #Matrice du score de chaque coup possible

            max = -1000
            pos_max = posPlayers
            min = 1000
            pos_min = posPlayers

            for i in range(len(cp_poss_eq)) : 
                
                position_possible, score_possible = MinMax(numEquipeAdv, cp_poss_eq[i], objectifsEquipe, score, g, profondeur - 1, alpha, beta)
                # score_coup_possible.append(score_possible)

                if numEquipe == 2 :     
                    # print("score_cp_poss", score_coup_possible[i])
                    if score_possible > max : 
                        max = score_possible
                        pos_max = position_possible
                    if(alpha > max) :
                        alpha = max
                        print("Set alpha to : ", alpha)
                    if(beta <= alpha) :
                        print("pruning alpha")
                        break
                else : 
                    # print("score_cp_poss", score_coup_possible[i])
                    if score_possible < min : 
                        min = score_possible
                        pos_min = position_possible
                    if(beta < min) :
                        beta = min
                        print("Set beta to : ", beta)
                    if(beta <= alpha) :
                        print("pruning beta")
                        break


            if numEquipe == 2 :
                # print("pos max : ", pos_max, "\nScore max = ", max, "profondeur = ", profondeur)
                return pos_max, max
            else :
                # print("pos min : ", pos_min, "\nScore min = ", min, "profondeur = ", profondeur)
                return pos_min, min

    #Debut de la strat
    def StratMinMax(numEquipe, posPlayers, objectifsEquipe, score, scoreEgalite, g, profondeur):
        position_suivante, score_position_suivante = MinMax(numEquipe, posPlayers, objectifsEquipe, score, g, profondeur, -10000, 10000)
        print("Equipe :", numEquipe, "score position suiv = ", score_position_suivante)

        currentEquipe = []
        if numEquipe == 1:
            currentEquipe = range(int(len(posPlayers)/2))
        elif numEquipe == 2:
            currentEquipe = range(int(len(posPlayers)/2), len(posPlayers))
        else:
            print("numEquipe doit être à 1 ou 2")
            return

        for playerEquipe in currentEquipe:  
                (row, col) = position_suivante[playerEquipe]        #son deplacement favorable
                # on met à jour la position du joueur playerEquipe1
                posPlayers[playerEquipe] = (row, col)      
                players[playerEquipe].set_rowcol(row, col)
                scoreEgalite[playerEquipe]+=1          #   On ajoute un déplacement à son score
                if (row, col) == objectifsEquipe[playerEquipe]:   # Si le joueur a atteint son objectif on met la matrice score à jour
                    score[playerEquipe]+=1
                    print("Le joueur ",playerEquipe," a atteint son but !")
                game.mainiteration()
        return

    #-------------------------------
    # FIN   MinMax Algo Strat 3
    #-------------------------------

    #-------------------------------
    # Strat 4
    #-------------------------------
    ######### Ebauche du path qui ne gene pas ses coéquipiers
    # def majCollision3(currentEquipe, g, posPlayer, allPath):
    #     for p in posPlayer:
    #         g[p] = False
    #     for player in currentEquipe:
    #         for pos in range(int(len(allPath[player])/5)):
    #             g[allPath[player][pos]] = False
    #         g[objectifs[player]] = False
    #     return
    # def majCollision4(currentEquipe, g, posPlayer, allPath):
    #     for p in posPlayer:
    #         g[p] = True
    #     for player in currentEquipe:
    #         for pos in range(int(len(allPath[player])/5)):
    #             g[allPath[player][pos]] = True
    #         g[objectifs[player]] = True
    #     return
    # def majPathStrat4(currentEquipe, g, posPlayer, allPath):
    #     for player in currentEquipe:    #   On remet à 0 les paths
    #         allPath[player] = []
    #     for player in currentEquipe:    #   On recalcule les paths
    #         majCollision3(currentEquipe, g, posPlayer, allPath)
    #         majCollisionObj1(currentEquipe, player, g)
    #         allPath[player] = probleme.astar(ProblemeGrid2D(posPlayers[player], objectifs[player], g, 'manhattan'))   # Nouveau Path potentiel calculé avec A*
    #         majCollisionObj2(currentEquipe, g)
    #     majCollision4(currentEquipe, g, posPlayer, allPath)
    #     return
    def stratAstarRecalculSansGene(numEquipe, posPlayers, objectifsEquipe, score, scoreEgalite, g, cptPath, cptWait, allPath):
        """ numEquipe : 1 ou 2
            posPlayers : la position de tous les joueurs
            objectifsEquipe : les objectifs de tous les joueurs
            score : 1 si le joueur a atteint son objectif, 0 sinon (tableau)
            scoreEgalite : le nombre de déplacement effectué par chaque joueur (tableau)
            """
        currentEquipe = []
        if numEquipe == 1:
            currentEquipe = range(int(len(posPlayers)/2))
        elif numEquipe == 2:
            currentEquipe = range(int(len(posPlayers)/2), len(posPlayers))
        else:
            print("numEquipe doit être à 1 ou 2")
            return
        for playerEquipe in currentEquipe:
            print("Mon tour, joueur : ", playerEquipe, " || mon obj : ", objectifsEquipe[playerEquipe] ," || mon path : ", allPath[playerEquipe])
            if score[playerEquipe] == 1:                   # Si le joueur a déjà atteint son objectif on passe son tour
                continue
            majCollision1(g, posPlayers)        # La position des joueurs est considérée temporairement comme un obstacle
            majCollisionObj1(currentEquipe, playerEquipe, g) # Les positions des objectifs des coéquipiers sont considérées comme des obstacles
            print("Tout doit être faux 1 : ", g[posPlayers[0]], g[posPlayers[1]], g[posPlayers[2]], g[posPlayers[3]], g[posPlayers[4]], g[posPlayers[5]])

            if allPath[playerEquipe][-1] != objectifsEquipe[playerEquipe]: # Si le path actuel est incohérent
                print("Tout doit être faux 2 : ", g[posPlayers[0]], g[posPlayers[1]], g[posPlayers[2]], g[posPlayers[3]], g[posPlayers[4]], g[posPlayers[5]])
                majCollisionObj2(currentEquipe, g)
                allPath[playerEquipe] = probleme.astar(ProblemeGrid2D(posPlayers[playerEquipe], objectifsEquipe[playerEquipe], g, 'manhattan'))   # Nouveau Path potentiel calculé avec A*
                print("Problème avec mon path, j'attends.")
                cptPath[playerEquipe] = 0
                cptWait[playerEquipe]+=1
                scoreEgalite[playerEquipe] += 1
                majCollision2(g, posPlayers)
                continue

            if g[allPath[playerEquipe][cptPath[playerEquipe]+1]] == False:  #   Si la prochaine case de son Path est bloqué par un joueur
                # On compare le temps que prend un détour au chemin actuel
                print("Tout doit être faux 3 : ", g[posPlayers[0]], g[posPlayers[1]], g[posPlayers[2]], g[posPlayers[3]], g[posPlayers[4]], g[posPlayers[5]])
                tmpPath = probleme.astar(ProblemeGrid2D(posPlayers[playerEquipe], objectifsEquipe[playerEquipe], g, 'manhattan'))   # Nouveau Path potentiel calculé avec A*

                if tmpPath[-1] != objectifsEquipe[playerEquipe]:
                    print("Problème avec mon path, j'attends.")
                    cptWait[playerEquipe] += 1
                    majCollision2(g, posPlayers)
                    majCollisionObj2(currentEquipe, g)
                    scoreEgalite[playerEquipe] += 1
                    continue

                #### CAS PARTICULIER (ne devrait pas arriver dans strat 4)
                if len(tmpPath) == 2:
                    print("Exception ", posPlayers[playerEquipe])
                    cptPath[playerEquipe] = 0
                    cptWait[playerEquipe] += 1
                    majCollision2(g, posPlayers)
                    majCollisionObj2(currentEquipe, g)
                    scoreEgalite[playerEquipe] += 1
                    continue
                #### FIN CAS PARTICULIER

                #### len(tmpPath) peut être = 1 si le joueur est bloqué || il faut gérer cette situation
                elif (len(tmpPath) < (len(allPath[playerEquipe])-cptPath[playerEquipe] + 1)) and (cptWait[playerEquipe] < 2) and (len(tmpPath) > 2):   # Si le joueur peut attendre mais que changer de chemin est plus rapide
                    print("Je switch ", posPlayers[playerEquipe])
                    allPath[playerEquipe] = tmpPath #   On change son chemin
                    cptPath[playerEquipe] = 0   # On avance de 1 dans ce nouveau Path
                elif ((len(tmpPath) > (len(allPath[playerEquipe])-cptPath[playerEquipe] + 1)) and (cptWait[playerEquipe] < 2)) or (len(tmpPath) == 1) or ((len(allPath[playerEquipe])-cptPath[playerEquipe]) == 2): 
                    # Si le nouveau chemin est plus long et que le joueur peut attendre
                    print("J'attends ", posPlayers[playerEquipe])
                    cptWait[playerEquipe] +=1
                    majCollision2(g, posPlayers)
                    majCollisionObj2(currentEquipe, g)
                    scoreEgalite[playerEquipe] += 1
                    continue        # On passe au joueur suivant
                else:       #   Le nouveau chemin est plus long mais le joueur a déjà attendu au tour précédent
                    print("Je switch, j'ai pas le choix ", posPlayers[playerEquipe])
                    cptWait[playerEquipe] = 0   # Le joueur va avancer, il peut de nouveau attendre au prochain tour
                    allPath[playerEquipe] = tmpPath
                    cptPath[playerEquipe] = 0   # On avance de 1 dans ce nouveau Path
            majCollisionObj2(currentEquipe, g)
            majCollision2(g, posPlayers)        # La position des joueurs est enlevée des obstacles
            cptPath[playerEquipe]+=1
            print("Taille du path : ", len(allPath[playerEquipe])," || Taille du cptPath : ", cptPath[playerEquipe])
            row, col = allPath[playerEquipe][cptPath[playerEquipe]]        # son déplacement 1 case plus loin
            print("J'avance ",posPlayers[playerEquipe]," -> ",allPath[playerEquipe][cptPath[playerEquipe]])
            # on met à jour la position du joueur playerEquipe1
            posPlayers[playerEquipe] = (row, col)      
            players[playerEquipe].set_rowcol(row, col)
            scoreEgalite[playerEquipe]+=1          #   On ajoute un déplacement à son score
            cptWait[playerEquipe] = 0              #   Le joueur s'étant déplacer, il peut attendre si besoin à la prochaine itération
            if (row, col) == objectifsEquipe[playerEquipe]:   # Si le joueur a atteint son objectif on met la matrice score à jour
                score[playerEquipe]+=1
                print("Le joueur ",playerEquipe," a atteint son but !")
            #game.mainiteration()

        game.mainiteration()
        return
    #-------------------------------
    # FIN   Strat 4
    #-------------------------------

    #-------------------------------
    # Initialisation Strat 1
    #-------------------------------
    allPathStrat1 = [0]*(len(posPlayers))
    #-------------------------------
    # Initialisation Strat 1
    #-------------------------------

    #-------------------------------
    # Initialisation de strat 2
    #-------------------------------
    cptPath = [0]*len(posPlayers)   # avancement actuel sur le path ; se réinitialise dès qu'il y a un obstacle et que le path est recalculé
    cptWait = [0]*len(posPlayers)   # le nombre de tour qu'attend le joueur sur place face à un obstacle
    allPathStrat2 = [0]*len(posPlayers)
    for i in range(len(posPlayers)):
        allPathStrat2[i] = probleme.astar(ProblemeGrid2D(posPlayers[i], objectifs[i], g, 'manhattan'))
    #-------------------------------
    # FIN   Initialisation de strat 2
    #-------------------------------

    #-------------------------------
    # Initialisation de strat 2 bis
    #-------------------------------
    cptPathbis = [0]*len(posPlayers)   # avancement actuel sur le path ; se réinitialise dès qu'il y a un obstacle et que le path est recalculé
    cptWaitbis = [0]*len(posPlayers)   # le nombre de tour qu'attend le joueur sur place face à un obstacle
    allPathStrat2bis = [0]*len(posPlayers)
    for j in range(len(posPlayers)):
        allPathStrat2bis[j] = probleme.astar(ProblemeGrid2D(posPlayers[j], objectifs[j], g, 'manhattan'))
    #-------------------------------
    # FIN   Initialisation de strat 2 bis
    #-------------------------------

    #-------------------------------
    # Initialisation de MinMax
    #-------------------------------
    if(Strat1 == 3 and Strat2 == 1) :
        for i in range(iterations):
            """
            # nombre de joueur pair
            # première moitié -> équipe 1
            # deuxième moitié -> équipe 2
            # Les joueurs se déplace par équipe chacun leur tour
            """
            allPath = [0]*(len(posPlayers))
            if 0 not in score: # Tous les joueurs ont atteint leur objectif
                break
            if i%2 != 0:
                StratMinMax(1, posPlayers, objectifs, score, scoreEgalite, g, 2)
            else:
                stratAstarRecalculObstacle(2, posPlayers, objectifs, score, scoreEgalite, g, cptPath, cptWait, allPathStrat2)
    #-------------------------------
    # FIN Initialisation MinMax
    #-------------------------------

    #-------------------------------
    # Initialisation de strat 4
    #-------------------------------
    cptPath4 = [0]*len(posPlayers)   # avancement actuel sur le path ; se réinitialise dès qu'il y a un obstacle et que le path est recalculé
    cptWait4 = [0]*len(posPlayers)   # le nombre de tour qu'attend le joueur sur place face à un obstacle
    allPathStrat4 = [0]*len(posPlayers)
    currentEquipe1 = range(int(len(posPlayers)/2))

    cptPath4bis = [0]*len(posPlayers)   # avancement actuel sur le path ; se réinitialise dès qu'il y a un obstacle et que le path est recalculé
    cptWait4bis = [0]*len(posPlayers)   # le nombre de tour qu'attend le joueur sur place face à un obstacle
    allPathStrat4bis = [0]*len(posPlayers)
    currentEquipe2 = range(int(len(posPlayers)/2), len(posPlayers))

    if Strat1 == 4:
        majCollision1(g, posPlayers)
        for p in range(len(posPlayers)):
            if p in currentEquipe1:
                majCollisionObj1(currentEquipe1, p, g)
                print("Tout doit être faux 4 : ", g[posPlayers[0]], g[posPlayers[1]], g[posPlayers[2]], g[posPlayers[3]], g[posPlayers[4]], g[posPlayers[5]])
                allPathStrat4[p] = probleme.astar(ProblemeGrid2D(posPlayers[p], objectifs[p], g, 'manhattan'))
                majCollisionObj2(currentEquipe1, g)
            if p in currentEquipe2:
                majCollisionObj1(currentEquipe2, p, g)
                print("Tout doit être faux 5 : ", g[posPlayers[0]], g[posPlayers[1]], g[posPlayers[2]], g[posPlayers[3]], g[posPlayers[4]], g[posPlayers[5]])
                allPathStrat4[p] = probleme.astar(ProblemeGrid2D(posPlayers[p], objectifs[p], g, 'manhattan'))
                majCollisionObj2(currentEquipe2, g)
        majCollision2(g, posPlayers)

    if Strat2 == 4:
        majCollision1(g, posPlayers)
        for p in range(len(posPlayers)):
            if p in currentEquipe1:
                majCollisionObj1(currentEquipe1, p, g)
                print("Tout doit être faux 6 : ", g[posPlayers[0]], g[posPlayers[1]], g[posPlayers[2]], g[posPlayers[3]], g[posPlayers[4]], g[posPlayers[5]])
                allPathStrat4bis[p] = probleme.astar(ProblemeGrid2D(posPlayers[p], objectifs[p], g, 'manhattan'))
                majCollisionObj2(currentEquipe1, g)
            if p in currentEquipe2:
                majCollisionObj1(currentEquipe2, p, g)
                print("Tout doit être faux 7 : ", g[posPlayers[0]], g[posPlayers[1]], g[posPlayers[2]], g[posPlayers[3]], g[posPlayers[4]], g[posPlayers[5]])
                allPathStrat4bis[p] = probleme.astar(ProblemeGrid2D(posPlayers[p], objectifs[p], g, 'manhattan'))
                majCollisionObj2(currentEquipe2, g)
        majCollision2(g, posPlayers)
    
    ######## Ebauche
    # if Strat1 == 4:
    #     majPathStrat4(range(int(len(posPlayers)/2)), g, posPlayers, allPathStrat4)
    # if Strat2 == 4:
    #     majPathStrat4(range(int(len(posPlayers)/2), (len(posPlayers))), g, posPlayers, allPathStrat4)
    #-------------------------------
    # FIN   Initialisation de strat 4
    #-------------------------------

    #-------------------------------
    # Strat 1 VS Strat 1
    #-------------------------------
    if Strat1 == 1 and Strat2 == 1:
        for i in range(iterations):
            """
            # nombre de joueur pair
            # première moitié -> équipe 1
            # deuxième moitié -> équipe 2
            # Les joueurs se déplace par équipe chacun leur tour
            """
            if 0 not in score: # Tous les joueurs ont atteint leur objectif
                break
            if i%2 == 0:
                stratAstarRecalculTjrs(1, posPlayers, objectifs, score, scoreEgalite, g)
            else:
                stratAstarRecalculTjrs(2, posPlayers, objectifs, score, scoreEgalite, g)
    #-------------------------------
    # FIN   Strat 1 VS Strat 1
    #-------------------------------

    #-------------------------------
    # Strat 1 VS Strat 2
    #-------------------------------
    if (Strat1 == 1 and Strat2 == 2) or (Strat1 == 2 and Strat2 == 1):
        for i in range(iterations):
            """
            # nombre de joueur pair
            # première moitié -> équipe 1
            # deuxième moitié -> équipe 2
            # Les joueurs se déplace par équipe chacun leur tour
            """
            if 0 not in score: # Tous les joueurs ont atteint leur objectif
                break
            if i%2 == 0:
                stratAstarRecalculTjrs(2, posPlayers, objectifs, score, scoreEgalite, g)
            else:
                stratAstarRecalculObstacle(1, posPlayers, objectifs, score, scoreEgalite, g, cptPath, cptWait, allPathStrat2)
    #-------------------------------
    # FIN   Strat 1 VS Strat 2
    #-------------------------------

    #-------------------------------
    # Strat 2 VS Strat 2
    #-------------------------------
    if Strat1 == 2 and Strat2 == 2:
        for i in range(iterations):
            """
            # nombre de joueur pair
            # première moitié -> équipe 1
            # deuxième moitié -> équipe 2
            # Les joueurs se déplace par équipe chacun leur tour
            """
            if 0 not in score: # Tous les joueurs ont atteint leur objectif
                break
            if i%2 != 0:
                stratAstarRecalculObstacle(1, posPlayers, objectifs, score, scoreEgalite, g, cptPath, cptWait, allPathStrat2)
            else:
                stratAstarRecalculObstacle(2, posPlayers, objectifs, score, scoreEgalite, g, cptPathbis, cptWaitbis, allPathStrat2bis)
    #-------------------------------
    # FIN   Strat 2 VS Strat 2
    #-------------------------------

    #-------------------------------
    # Strat 1 VS Strat 4
    #-------------------------------
    if (Strat1 == 1 and Strat2 == 4) or (Strat1 == 4 and Strat2 == 1):
        for i in range(iterations):
            """
            # nombre de joueur pair
            # première moitié -> équipe 1
            # deuxième moitié -> équipe 2
            # Les joueurs se déplace par équipe chacun leur tour
            """
            if 0 not in score: # Tous les joueurs ont atteint leur objectif
                break
            if i%2 != 0:
                stratAstarRecalculTjrs(1, posPlayers, objectifs, score, scoreEgalite, g)
            else:
                stratAstarRecalculSansGene(2, posPlayers, objectifs, score, scoreEgalite, g, cptPath4, cptWait4, allPathStrat4)
    #-------------------------------
    # FIN   Strat 1 VS Strat 4
    #-------------------------------

    #-------------------------------
    # Strat 2 VS Strat 4
    #-------------------------------
    if (Strat1 == 2 and Strat2 == 4) or (Strat1 == 4 and Strat2 == 2):
        for i in range(iterations):
            """
            # nombre de joueur pair
            # première moitié -> équipe 1
            # deuxième moitié -> équipe 2
            # Les joueurs se déplace par équipe chacun leur tour
            """
            if 0 not in score: # Tous les joueurs ont atteint leur objectif
                break
            if i%2 != 0:
                stratAstarRecalculObstacle(1, posPlayers, objectifs, score, scoreEgalite, g, cptPath, cptWait, allPathStrat2)
            else:
                stratAstarRecalculSansGene(2, posPlayers, objectifs, score, scoreEgalite, g, cptPath4, cptWait4, allPathStrat4)
    #-------------------------------
    # FIN   Strat 2 VS Strat 4
    #-------------------------------

    #-------------------------------
    # Strat 4 VS Strat 4
    #-------------------------------
    if Strat1 == 4 and Strat2 == 4:
        for i in range(iterations):
            """
            # nombre de joueur pair
            # première moitié -> équipe 1
            # deuxième moitié -> équipe 2
            # Les joueurs se déplace par équipe chacun leur tour
            """
            if 0 not in score: # Tous les joueurs ont atteint leur objectif
                break
            if i%2 != 0:
                stratAstarRecalculSansGene(1, posPlayers, objectifs, score, scoreEgalite, g, cptPath4, cptWait4, allPathStrat4)
            else:
                stratAstarRecalculSansGene(2, posPlayers, objectifs, score, scoreEgalite, g, cptPath4bis, cptWait4bis, allPathStrat4bis)
            print("PTITE ITE : ", i)
    #-------------------------------
    # FIN   Strat 4 VS Strat 4
    #-------------------------------

    #-------------------------------
    # Affichage des scores
    #-------------------------------
    print ("scores : ", score)
    print("Détails des scores : ", scoreEgalite)
    scoreEquipe1 = 0
    scoreEquipe2 = 0
    if 0 not in score:          # Tous les joueurs ont fini dans le nombre d'itérations donné 
        for i in range(int(len(scoreEgalite)/2)):
            scoreEquipe1 += scoreEgalite[i]
        for i in range(int(len(scoreEgalite)/2), len(scoreEgalite)):
            scoreEquipe2 += scoreEgalite[i]
        if scoreEquipe1 > scoreEquipe2:
            print("Equipe 2 a gagné !")
        elif scoreEquipe2 > scoreEquipe1:
            print("Equipe 1 a gagné !")
        else:
            print("Egalité !")
        print("Score Equipe 1 : ",scoreEquipe1)
        print("Score Equipe 2 : ",scoreEquipe2)
    else:                       # Tous les joueurs n'ont pas fini, on compare le nombre de joueur arrivé
        for i in range(int(len(score)/2)):
            scoreEquipe1 += score[i]
        for i in range(int(len(score)/2), len(score)):
            scoreEquipe2 += score[i]
        if scoreEquipe1 > scoreEquipe2:
            print("Equipe 1 a gagné !")
        elif scoreEquipe2 > scoreEquipe1:
            print("Equipe 2 a gagné !")
        else:                   # S'il y a autant de joueur arrivé dans chaque équipe on compare finalement le scoreEgalite
            for i in range(int(len(scoreEgalite)/2)):
                scoreEquipe1 += scoreEgalite[i]
            for i in range(int(len(scoreEgalite)/2), len(scoreEgalite)):
                scoreEquipe2 += scoreEgalite[i]            
            if scoreEquipe1 > scoreEquipe2:
                print("Equipe 2 a gagné !")
            elif scoreEquipe2 > scoreEquipe1:
                print("Equipe 1 a gagné !")
            else:
                print("Egalité !")
            print("Score Equipe 1 : ",scoreEquipe1)
            print("Score Equipe 2 : ",scoreEquipe2)

    pygame.quit()
    #-------------------------------
    # FIN   Affichage des scores
    #-------------------------------
    return scoreEquipe1, scoreEquipe2

    #-------------------------------

# if __name__ == '__main__':
#     main(150, 2, 4)

# -------------------------------
# STATISTIQUES
# -------------------------------
s1 = 0
s2 = 0
if len(sys.argv) > 1:
    iterations = int(sys.argv[1])
if len(sys.argv) > 3:
    s1 = int(sys.argv[2])
    s2 = int(sys.argv[3])
else :
    print("Usage : python main.py <Iteration> <Strat Equipe 1> <Strat Equipe 2>")
allScoreEquipe1 = []
allScoreEquipe2 = []
for i in range(100): # Nombre de parties
    if s1 == 0 or s2 == 0:
        break
    print("ITERATION : ",i+1)
    x, y = main(iterations, s1, s2)
    allScoreEquipe1.append(x)
    allScoreEquipe2.append(y)

print("Total sur ",i+1," games pour l'Equipe 1 : ",allScoreEquipe1)
print("Total sur ",i+1," games pour l'Equipe 2 : ",allScoreEquipe2)
#-------------------------------
# FIN   STATISTIQUES
#-------------------------------