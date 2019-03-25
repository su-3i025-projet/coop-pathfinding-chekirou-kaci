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
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2)

class Noeud:
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
        
    def expand(self, wallStates):
        """ étend un noeud avec ces fils
            """
        
        nouveaux_fils = []
        for s in [(1,0), (0,1), (0,-1), (-1,0)]:
            if (self.x + s[0],self.y+ s[1]) not in wallStates and self.x + s[0]>=0 and self.x + s[0]< nbLignes and self.y+ s[1]>=0 and self.y+ s[1]<nbColonnes:
                nouveaux_fils.append(Noeud(self.x + s[0],self.y+ s[1], self.g+1,self))
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
    




def astar(initState, goalState, wallStates, obstacles =[]):
    """ application de l'algorithme a-star sur un probleme donné
        """
    nodeInit = Noeud(initState[0], initState[1],0,None)
    frontiere = [(nodeInit.g+distManhattan((nodeInit.x, nodeInit.y),goalState),nodeInit)] 
    reserve = {}        
    bestNoeud = nodeInit
    
    while frontiere != [] and not (goalState==(bestNoeud.x, bestNoeud.y)):              
        (min_f,bestNoeud) = heapq.heappop(frontiere)         
    # Suppose qu'un noeud en réserve n'est jamais ré-étendu 
    # Hypothèse de consistence de l'heuristique
    # ne gère pas les duplicatas dans la frontière
    
        if str(bestNoeud.x) + " " + str(bestNoeud.y) not in reserve:            
            reserve[str(bestNoeud.x) + " " + str(bestNoeud.y)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(wallStates)            
            for n in nouveauxNoeuds:
                if (n.x,n.y) not in wallStates and n.x>=0 and n.x< nbLignes and n.y>=0 and n.y< nbColonnes and (n.x, n.y) not in obstacles:
                    f = n.g+distManhattan((n.x, n.y),goalState)
                    heapq.heappush(frontiere, (f,n))       
    # Afficher le résultat  
    res = []
    while(bestNoeud.pere != None):
        res.append((bestNoeud.x , bestNoeud.y ))   
        bestNoeud = bestNoeud.pere   
    reversed(res)  
       
    
    return res








def occupied(position ,posPlayers):
    for i in range(len(posPlayers)):
        if position == posPlayers[i]:
            return (True, i)
    return (False, -1)

#===================================================================================================================================== 
#=====================================================================================================================================
#=====================================================================================================================================
#=====================================================================================================================================    


def cross_each_other(posPlayers,wallStates, other_path,actual_path,other, actual):
    """ verifie si deux chemins se croisent"""
    for i in  actual_path:
        if i in other_path:
            return True
    else:
        return False


def Base_strategy1(nbPlayers, posPlayers, initStates,  wallStates, goalStates):
    """ calcul les chemins en utilisant A* puis les met par groupe.
    le chemins dans un meme groupe peuvent d'executer en parallele
    """


    #calculer le chemin sans croiser les autres

    paths = [ [] ]* nbPlayers
    #etablir les chemins 
    for joueur in range(nbPlayers):
        others_goals = [ (goalStates[k] if k!= joueur else None )for k in range(nbPlayers) ]
        others_initialStates = [ (initStates[k] if k!= joueur else None )for k in range(nbPlayers) ]
        paths[joueur] = astar(initStates[joueur], goalStates[joueur], wallStates, others_initialStates+others_goals)
    Lots = [[]]
    for joueur, path in zip(range(nbPlayers), paths):
        classé = False
        index_lots = 0
        while not classé and index_lots < len(Lots):
            paralelle = True
            index_path = 0
            while paralelle and index_path < len(Lots[index_lots]):
                if cross_each_other(posPlayers,wallStates, Lots[index_lots][index_path][1], path, Lots[index_lots][index_path][0], joueur):
                    paralelle = False
                index_path +=1
            if paralelle:
                Lots[index_lots].append((joueur, path))
                classé = True
            index_lots += 1
        if not classé:
            Lots.append([(joueur, path)])
    return Lots



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
    print("==========================================")
    print("|  cooperative pathfinding strategy 2    |")
    print("==========================================")
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
    
    
    found = [ False for i in range(nbPlayers)]
    t1 = time.clock()
    Lots  = Base_strategy1(nbPlayers,posPlayers, initStates,  wallStates, goalStates)
    t2 = time.clock()
    iteration = 0
    

    #calcul des iterations necessaires 
    #le nombre d'iterations par groupe est la taille du plus grand chemin  
    maxi_time_per_lot = 0
    for lot in Lots:
        
        maxi_time_per_lot = -float("inf")
        for joueur_path in lot: # on fait bouger chaque joueur séquentiellement
            j, path = joueur_path
            if(len(path) > maxi_time_per_lot):
                maxi_time_per_lot = len(path)
        iteration += maxi_time_per_lot


    #execution 
    for lot in Lots: # pour chaque groupe ou lot 
        # on execute iterations fois au maximum
        for i in range(iterations):
            
            for joueur_path in lot: # on fait bouger chaque joueur séquentiellement
                j, path = joueur_path
                if not found[j]: # s'il n'a pas encore trouvé
                    x_inc,y_inc = path.pop()
                    next_row = x_inc
                    next_col = y_inc
                    players[j].set_rowcol(next_row,next_col)
                    col=next_col
                    row=next_row
                    game.mainiteration()
                    posPlayers[j]=(row,col)
                    # si on a  trouvé un objet on le ramasse
                    if (row,col) in goalStates and goalStates.index((row, col)) == j:
                        o = players[j].ramasse(game.layers)
                        print ("Objet trouvé par le joueur ", j)
                        score[j]+=1
                        game.mainiteration()                
                        found[j] = True
                        break
    print ("scores:", score)
    print("temps " + str(t2 - t1) + " iterations" + str(iteration))
    pygame.quit()

if __name__ == '__main__':
    main()
    


