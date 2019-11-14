# -*- coding: utf-8 -*-

#!/usr/bin/python

# Copyright 2013, Gurobi Optimization, Inc.

from gurobipy import *
import numpy as np
from math import *
from pylab import *
import random
import matplotlib.pyplot as plt


"""
    
    Liste des fonctions utilitaires utilisées 

"""

# Lit un fichier de format <.txt> et renvoie son contenu
# Param filename : nom du fichier à lire
def read_file ( filename ):
    
    # lecture de l'en-tête
    infile = open ( filename, "r" )
    
    data = []
    
    # Si le fichier traite des villes
    if ( filename.find("villes") == 0 ):
        for ligne in infile:
            data.append(ligne[:-1]) # le "-1" sert à retirer le retour à la ligne "\n"
    
    # Si le fichier traite des populations     
    elif ( filename.find("populations") == 0 ):
        for ligne in infile:
            villes = ligne.split(',')[0]
            populations = ligne.split(',')[1][:-1]
            data.append([villes,populations])
    
    # Si le fichier traite des coordonnées des villes
    elif ( filename.find("coordvilles") == 0 ):
        for ligne in infile:
            villes = ligne.split(',')[0]
            coord1 = ligne.split(',')[1]
            coord2 = ligne.split(',')[2][:-1]
            data.append([villes,coord1,coord2])
            
    # Si le fichier traite des distances des villes
    elif ( filename.find("distances") == 0 ):
        
        #count = 0
        tab = []
        debut = True;
        for ligne in infile:
            if(ligne[:-1].isalpha() or "-" in ligne):
                if(not debut):
                    data.append(tab)
                else:
                    debut = False
                tab = []
            tab.append(ligne[:-1])
        data.append(tab)
        
    infile.close ()

    return data
    

# Param populations : liste des villes candidates
# Param k : le nombre de villes souhaitées où les ressources seront situées 
# Return : les indices de la liste des villes choisies aléatoirement
def getLocalisationRessourcesRandom(villes,k):
    villesChoisies = random.sample(villes,k)
    villesIndices = []
    for i in range(len(villesChoisies)):
        villesIndices.append(villes.index(villesChoisies[i]))
    return villesIndices


# Param k : entier compris entre 3 et 5
# Return l'indice des villes choisies manuellement 
def getLocalisationRessourcesChosen(k):
    if k == 3:
        villesChoisies = [0,15,28] # ['Antony','Saint-Cloud','Gennevilliers']
    elif k == 4:
        villesChoisies = [0,15,22,27] # ['Antony','Gennevilliers','Meudon','Rueil-Malmaison']
    elif k == 5:
        villesChoisies = [0,9,15,24,34] # ['Antony','Clamart','Gennevilliers','Nanterre','Ville d'Avray']
    else:
        villesChoisies = []
        print("k doit être compris entre 3 et 5 inclus")
    return villesChoisies

# Param villes : liste de villes
# Param distances : matrice des distances entre toutes les villes
# Param k : nombre de secteurs choisis
# Param ressources : indices des villes choisies
# Return : matrice dij (i = les villes, j = les k secteurs)
def getMatriceDij(villes,distances,k,ressources):
    
    # Adapté à la question 3 avec k = 36 villes
    if (k == len(villes)):
        d = np.zeros((k,k))
        for i in range(k):
            for j in range(k):
                d[i][j] = distances[i][j+1]
        return d
    
    # Adapté à la question 1 et 2 avec les villes choisies "à la main"
    else:
        # initialisation
        nbLignes = len(villes)
        nbColonnes = len(ressources)
        d = np.zeros((nbLignes,nbColonnes))
        for i in range(nbLignes):
            for j in range(nbColonnes):
                d[i][j] = distances[i][ressources[j]+1]
        return d


# Param alpha : paramètre strictement positif donné
# Param k : nombre de secteurs choisis
# Populations : liste des populations des villes
# Return : contrainte gamma
def getGamma(alpha,k,populations):
    nbPopulations = 0
    for i in range(len(populations)):
        nbPopulations += float(populations[i][1])
    gamma = ((1+alpha)/k)*nbPopulations
    return gamma


# Param populations : liste des populations des villes
# Param k : nombre de secteurs choisis
# Param ressources : indices des villes choisies
# Return : duplique les distances des villes k fois sous forme de matrice
def getMatricePopulations(populations,k):
    matPopulations = np.zeros((len(populations),k))
    for i in range(len(populations)):
        for j in range(k):
            matPopulations[i][j] = populations[i][1]
    return matPopulations


# Param X : matrice xij remplie avec 0 ou 1
# Param indice_secteur : liste des indices des secteurs
# Param coord : liste des coordonnées des villes
# Param title : titre de la figure affichée
# Return : affichage des secteurs     
def showResult(X, indice_secteur, coord, title, fileTitle) :
    # initialisation
    img = plt.imread("92.png")
    colors = ['b','r','g','y','c','p']
    fig, ax = plt.subplots()
    row,col = X.shape
    
    # coordonnées des secteurs 
    coord_secteur = []
    for i in range(len(indice_secteur)):
        coord_secteur.append(coord[indice_secteur[i]])
    
    # Affichage des secteurs sur la carte
    if (col!=row):
        for k in range(col) :
            x=[]
            y=[]
            for i in range(row) :     
                if i != indice_secteur[k] and X[i][k]==1 :
                    x.append(int(coord[i][1]))
                    y.append(int(coord[i][2]))
            ax.plot(x, y , colors[k]+'o') 
    
    else:
        for i in range(len(indice_secteur)):
            x=[]
            y=[]
            for j in range(row):
                
                if (X[j][indice_secteur[i]] == 1 and indice_secteur[i] != j ):
                    
                    x.append(int(coord[j][1]))
                    y.append(int(coord[j][2]))
                    
                    ax.plot(x, y , colors[i]+'o')
                
    # Affichage étoilé des k ressources
    for i in range(len(coord_secteur)):
        x = int(coord_secteur[i][1])
        y = int(coord_secteur[i][2])
        lab = 'secteur'+str(i+1)
        ax.plot(x, y, '*', label=lab, markersize=np.sqrt(25.), c=colors[i])        
    
    # Plot legend.
    ax.legend(loc="lower right", numpoints=1, fontsize='x-small')
    
    # titre de la figure
    plt.title(title)
    
    # Affichage image à la compilation
    ax.imshow(img)
    
    # Sauvegarde de l'image
    plt.savefig(fileTitle)


# Param x : matrice xij remplie avec 0 ou 1
# Return : satisfaction de chaque ville exprimée par la distance entre la ville i et j , le moins satisfait
def getSatisfactions(x,ressources):
    lig,col = x.shape
    satisfactionMoy = 0
    max = 0.0 # satisfaction moins bien servi, ie plus grande distance
    
    if (col != len(ressources)):
        for i in range(len(ressources)):
            for j in range(lig):
                if x[j][ressources[i]] == 1:
                    satisfactionMoy += float(distances[j][ressources[i]+1])
                    if float(distances[j][ressources[i]+1]) > max:
                        max = float(distances[j][ressources[i]+1])
    else:
        for i in range(col):
            for j in range(lig):
                if x[j][i] == 1:
                    satisfactionMoy += float(distances[j][ressources[i]+1])
                    #satisfactions.append([distances[j][0],distances[j][ressources[i]+1]])
                    if float(distances[j][ressources[i]+1]) > max:
                        max = float(distances[j][ressources[i]+1])
                        
    return satisfactionMoy/nbVilles,max
    

def getSatisfactionsBis(x,ressources):
    lig,col = x.shape
    satisfactionMoy = 0
    #max = 0.0
    for i in range(len(ressources)):
        for j in range(lig):
            if x[j][ressources[i]] == 1:
                satisfactionMoy += float(distances[j][ressources[i]+1])
    return satisfactionMoy/lig

# Param villes : liste de villes
# Param k_ressources : vecteur contenant les indices des villes choisies
# Return indices des villes choisies
def getVillesFromIndices(villes,k_ressources):
    ressources = []
    for i in range(len(k_ressources)):
        if (k_ressources[i].x == 1 ):
            ressources.append(i)
    return ressources


# Param fxf : solution trouvée en minimisant f appliquée sur F(x)
# Param fxg : solution trouvée en minimisant g appliquée sur F(x)
# Return : ratio du prix de l'équité
def getPrixEquite(fxf,fxg):
    return 1 - ( fxf / fxg )

# Param X : matrice Xij de la fonction G(x)
# Param d : matrice Dij de dimension n x k
# Param nbVilles : nombre de villes
# Return fxg
def getFxg(X,d,nbVilles):
    fxg = 0
    for i in range(nbVilles):
        for j in range(k):
            if (X[i][j] == 1):
                fxg += d[i][j]
    return fxg

"""

    Initialisation de notre jeu de données ainsi que les variables nécessaires

"""

villes = read_file ( "villes92.txt" )
populations = read_file ( "populations92.txt" )
coordVilles = read_file ( "coordvilles92.txt" )
distances = read_file ( "distances92.txt" )

nbVilles = len(villes)
k = 5
alpha = 0.2
gamma = getGamma(alpha,k,populations)
epsilon = 10E-6

# relatif f(x) et g(x)
ressources = getLocalisationRessourcesChosen(k) 
d = getMatriceDij(villes,distances,k,ressources) 
matPopulations = getMatricePopulations(populations,k)
