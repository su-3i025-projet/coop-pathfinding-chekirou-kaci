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
        
    def expand(self):
        """ étend un noeud avec ces fils
            pour un probleme de taquin p donné
            """
        nouveaux_fils = [Noeud(self.x + s[0],self.y+ s[1], self.g+1,self) for s in [(1,0), (0,1), (0,-1), (-1,0)]]
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
            nouveauxNoeuds = bestNoeud.expand()            
            for n in nouveauxNoeuds:
                if (n.x,n.y) not in wallStates and n.x>=0 and n.x<=19 and n.y>=0 and n.y<=19 and (n.x, n.y) not in obstacles:
                    f = n.g+distManhattan((n.x, n.y),goalState)
                    heapq.heappush(frontiere, (f,n))              
    # Afficher le résultat  
    res = []
    while(bestNoeud.pere != None):
        res.append((bestNoeud.x - bestNoeud.pere.x, bestNoeud.y - bestNoeud.pere.y))   
        bestNoeud = bestNoeud.pere   
    reversed(res)  
       
    return res

def occupied(position ,posPlayers):
	for i in range(len(posPlayers)):
		if position == posPlayers[i]:
			return (True, i)
	return (False, -1)

    
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
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player

def stratégie_opportuniste(posPlayers , j, res,initStates,  wallStates, goalStates ):
    row,col = posPlayers[j]
    #print("liste ", j, "   ", res[j])
    x_inc,y_inc = res[j].pop()
    # si quelqu'un se trouve a la prochaine case
    print("next step", x_inc,y_inc)
    occupieda,person = occupied((row+x_inc,col+y_inc), posPlayers)
    if(occupieda):
        print("je suis ", j ,"case occupée par " , person)
        print("j", j, res[j])
        initStates[j] = posPlayers[j]
        obstacle = [(posPlayers[k] if k!= j else None ) for k in range(len(posPlayers))]

        next_hop = res[j].pop()
        deviation = astar(initStates[j], (row+x_inc +next_hop[0] ,col+y_inc+ next_hop[1]), wallStates, obstacle)
        new_path = deviation + res[j]
        if(len(res[j]) <= int(2* len(new_path))):
                res[j] = astar(initStates[j], goalStates[j], wallStates, obstacle)
        else:
            res[j]= new_path
        x_inc,y_inc = res[j].pop()
    next_row = row+x_inc
    next_col = col+y_inc
    return next_row, next_col




def main():

    #for arg in sys.argv:
    iterations = 50 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    

    
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
    posPlayers = initStates
    #res = [[] for i in range(nbPlayers)]
    res= []
    #obj = astar([initStates[0]], [goalStates[0]], wallStates, 0 )
    found = [ False for i in range(nbPlayers)]
    for i in range(nbPlayers):
        print(i)
        #Base_strategy(posPlayers,i, res,initStates,  wallStates, goalStates )
        res.append(astar(initStates[i], goalStates[i], wallStates))
    

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
            if not found[j]:
                #row,col = posPlayers[j]
                #x_inc,y_inc = res[j].pop()
                #next_row = row+x_inc
                #next_col = col+y_inc
                #print("=====================================")
                #print(" joueur : " + str(j))
                #print("chemin " + str(res[j]))
                # and ((next_row,next_col) not in posPlayers)
                next_row, next_col = stratégie_opportuniste(posPlayers , j, res,initStates,  wallStates, goalStates )
                if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                    players[j].set_rowcol(next_row,next_col)
                    col=next_col
                    row=next_row
                    game.mainiteration()
                    posPlayers[j]=(row,col)
                # si on a  trouvé un objet on le ramasse
                if (row,col) in goalStates and goalStates.index((row, col)) == j:
                    o = players[j].ramasse(game.layers)
                    print ("Objet trouvé par le joueur ", j)
                    #goalStates.remove((row,col)) # on enlève ce goalState de la liste
                    #indice = goalStates.index((row, col))
                    score[j]+=1
                    game.mainiteration()
                    # et on remet un même objet à un autre endroit
                    #x = random.randint(1,19)
                    #y = random.randint(1,19)
                    #while (x,y) in wallStates:
                    #    x = random.randint(1,19)
                    #    y = random.randint(1,19)
                    #o.set_rowcol(x,y)
                    #goalStates.append((x,y)) # on ajoute ce nouveau goalState
                    #goalStates[indice] = (x,y) # on ajoute ce nouveau goalState
                    #initStates[j] = posPlayers[j]
                    #res[j] = astar(initStates[j], goalStates[j], wallStates )
                    #game.layers['ramassable'].add(o)
                    game.mainiteration()                
                    found[j] = True
                    break
    print ("scores:", score)
    pygame.quit()

if __name__ == '__main__':
    main()
    


