# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo
import heapq
import random 
import numpy as np
import sys
import time

def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1, y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2)



#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================



class Space_Noeud:
    def __init__(self, x,y,  g, pere=None):
        self.x = x
        self.y = y 
        self.g = g
        self.pere = pere
        
    def __str__(self):
        #return np.array_str(self.etat) + "valeur=" + str(self.g)
        return str(self.x)+", " +str(self.y)  + " valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self):
        """ étend un noeud avec ces fils
            pour un probleme de taquin p donné
            """
        nouveaux_fils = [Space_Noeud(self.x + s[0],self.y+ s[1], self.g+1,self) for s in [(1,0), (0,1), (0,-1), (-1,0)]]
        return nouveaux_fils
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
        """
        nouveaux_fils = self.expand()
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand()[k-1]
            
    def trace(self):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0    
        while n!=None :
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return
    


    
#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================

 
class true_Distance:
    """ calculer la true distance"""
    def __init__(self, goal, depart,wallStates ):
        self.nodeInit = Space_Noeud(goal[0], goal[1], 0,None)
        self.reserve = {} 
        self.bestNoeud = self.nodeInit
        self.depart = depart
        self.wallStates = wallStates
        self.frontiere = [(self.nodeInit.g+distManhattan((self.nodeInit.x, self.nodeInit.y), self.depart),self.nodeInit)] 
    def get_distance_to(self,place):
        if str(place[0]) + " " + str(place[1]) in self.reserve:
            return self.reserve[str(place[0]) + " " + str(place[1])]
        else:
            while self.frontiere != [] and str(place[0]) + " " + str(place[1]) not in self.reserve:
                (min_f,self.bestNoeud) = heapq.heappop(self.frontiere)
                if str(self.bestNoeud.x) + " " + str(self.bestNoeud.y) not in self.reserve:
                    self.reserve[str(self.bestNoeud.x) + " " + str(self.bestNoeud.y)] = self.bestNoeud.g #maj de reserve
                    nouveauxNoeuds = self.bestNoeud.expand()            
                    for n in nouveauxNoeuds:
                        if (n.x,n.y) not in self.wallStates and n.x>=0 and n.x<nbLignes and n.y>=0 and n.y<nbColonnes:
                            f = n.g+distManhattan((n.x, n.y),self.depart)
                            heapq.heappush(self.frontiere, (f,n))              
            if(str(place[0]) + " " + str(place[1]) in self.reserve):
                return self.reserve[str(place[0]) + " " + str(place[1])]
            else: print("pas trouvé")



    
#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================


class spaceTime_Noeud:
    def __init__(self, x,y,t,  g, pere=None):
        self.x = x
        self.y = y
        self.t = t 
        self.g = g
        self.pere = pere
        
    def __str__(self):
        return str(self.x)+", " +str(self.y)  +", " +str(self.t)+ " valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self, wallStates):
        """ étend un noeud avec ces fils
            """
        
        nouveaux_fils = []
        for s in [(1,0), (0,1), (0,-1), (-1,0), (0,0)]:
            if (self.x + s[0],self.y+ s[1]) not in wallStates and self.x + s[0]>=0 and self.x + s[0]< nbLignes and self.y+ s[1]>=0 and self.y+ s[1]<nbColonnes:
                nouveaux_fils.append(spaceTime_Noeud(self.x + s[0],self.y+ s[1], self.t+1, self.g+1,self))
        return nouveaux_fils
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
        """
        nouveaux_fils = self.expand()
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand()[k-1]
            
    def trace(self):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0    
        while n!=None :
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return
    


#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================



def spaceTime_astar(initState, goalState, wallStates,obstacles, time ,steps, reservations=[]):
    """ application de l'algorithme a-star spatio-temporel sur un probleme donné
        """
    distance = true_Distance(goalState, initState,wallStates)
    nodeInit = spaceTime_Noeud(initState[0], initState[1],time, 0,None)

    frontiere = [(nodeInit.g+distance.get_distance_to(initState),nodeInit)] 
    reserve = {}        
    bestNoeud = nodeInit
    i = 0
    while frontiere != [] and not (goalState==(bestNoeud.x, bestNoeud.y)) and i < steps:              
        (min_f,bestNoeud) = heapq.heappop(frontiere)
        i+= 1
        if str(bestNoeud.x) + " " + str(bestNoeud.y) + " " + str(bestNoeud.t) not in reserve:            
            reserve[str(bestNoeud.x) + " " + str(bestNoeud.y) + " " + str(bestNoeud.t)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(wallStates)            
            for n in nouveauxNoeuds:
                if (((n.x,n.y) not in wallStates+obstacles) and n.x>=0 and n.x< nbLignes and n.y>=0 and n.y<nbColonnes and (n.x, n.y, n.t) not in reservations):
                    f = n.g+distance.get_distance_to((n.x, n.y))
                    heapq.heappush(frontiere, (f,n))        
    res = []
    while(bestNoeud.pere != None):
        res.append((bestNoeud.x , bestNoeud.y, bestNoeud.t ))   
        bestNoeud = bestNoeud.pere   
    res= list(reversed(res))  
    return res








def occupied(j, position ,posPlayers):
    for i in range(len(posPlayers)):
    
        if  i != j and position == posPlayers[i]:
            return (True, i)
    return (False, -1)

#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================    

def others_path(paths, i):
    """ permet d'avoir les chemins des autres joueurs sous forme de liste"""
    reservations = []
    for j in range(len(paths)):
        if j!= i:
            reservations = reservations + [ (n[0], n[1], n[2]-1) for n in paths[j] ] + [ (n[0], n[1], n[2]+1) for n in paths[j] ] + paths[j]
    return reservations


#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================



#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================



# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer1'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 25  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player



def main():
    print("======================================================")
    print("|  cooperative pathfinding advanced search depth     |")
    print("======================================================")
    #for arg in sys.argv:
    iterations = 50 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    global nbColonnes, nbLignes
    nbColonnes = game.spriteBuilder.colsize
    nbLignes = game.spriteBuilder.rowsize
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    score = [0]*nbPlayers
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wallstates:", wallStates)
    posPlayers = initStates
    res= []
    found = [ False for i in range(nbPlayers)]
    temps = 0
    t1 = time.clock()
    reservations = []
    for i in range(nbPlayers):
        print(i)
        others_goals = [ (goalStates[k] if k!= i else None )for k in range(nbPlayers) ]
        others_initialStates = [ (initStates[k] if k!= i else None )for k in range(nbPlayers) ]
        res.append(spaceTime_astar(initStates[i], goalStates[i], wallStates ,others_goals+ others_initialStates, 0,12, reservations ))
        
        reservations = reservations +[ (n[0], n[1], n[2]-1) for n in res[i] ] + [ (n[0], n[1], n[2]+1) for n in res[i] ] + res[i]
        print("joueur " , i, res[i])
        print("===================================================================")
    t2 = time.clock()
    temps += t2 - t1
    iteration = 0 
    for i in range(1, iterations):
        if found != [True for i in range(nbPlayers)]:
            iteration+=1
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
            if not found[j]:
                if(len(res[j]) ==0):#si on est arrivé a la fin du chemin partiel
                    t1 = time.clock()
                    others_goals = [ (goalStates[k] if k!= j else None )for k in range(nbPlayers) ]
                    others_positions = [ (posPlayers[k] if k!= j else None )for k in range(nbPlayers) ]
                    res[j]= spaceTime_astar(posPlayers[j], goalStates[j], wallStates ,others_goals +others_positions , i,12, others_path(res, j) )
                    t2 = time.clock()
                    temps += t2 - t1
                next_row, next_col, t = res[j].pop(0)
                c, k = occupied(j, (next_row, next_col) ,posPlayers)
                if(c):
                    print("iteration ", i )
                    print("je suis , " , j, "a ", next_row, next_col, " croisement avec " , k, t)
                players[j].set_rowcol(next_row,next_col)
                col=next_col
                row=next_row
                game.mainiteration()
                posPlayers[j]=(row,col)
                if (row,col) in goalStates and goalStates.index((row, col)) == j:
                    o = players[j].ramasse(game.layers)
                    print ("Objet trouvé par le joueur ", j)
                    score[j]+=1
                    game.mainiteration()              
                    found[j] = True
                    
    print("scores:", score)
    print("temps " + str(t2 - t1) + " iterations" + str(iteration))
    pygame.quit()

if __name__ == '__main__':
    main()
