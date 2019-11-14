from Exo1 import *

"""

    Question 3 
    
"""

# Param alpha : valeur strictement positif
# Param objValFx : valeur de la fonction objectif f
# Return : matrice Xij, valeur de la fonction objectif h, les indices des villes implémentant les ressources, satisfactions
def getHx(alpha,objValFx):

    # initialisation du solveur Gurobi
    mH = Model("mogplex")
    
    # initialisation des matrices Dij et de populations
    dH = getMatriceDij(villes,distances,len(villes),ressources)
    pH = getMatricePopulations(populations,len(villes))
    
    # declaration variables de decision
    xH = []
    for i in range(nbVilles*nbVilles):
        xH.append(mH.addVar(vtype=GRB.BINARY, lb=0, name="x%d" % (i+1)))
        
    k_ressources = []
    for i in range(nbVilles):
        k_ressources.append(mH.addVar(vtype = GRB.BINARY, lb=0, name = "k_res%d" % (i+1) ))
        
    # ajout var max
    maxH = mH.addVar(vtype=GRB.CONTINUOUS, obj=0, name="max")
    
    # conversion liste à matrice
    dataH = np.array(xH)
    shape = (nbVilles,nbVilles)
    new_dataH = dataH.reshape(shape)
    
    # maj du modele pour integrer les nouvelles variables
    mH.update()   
    
    # Contrainte numéro une : gamma
    
    for j in range(k):
        mH.addConstr(quicksum(pH[i][j]*new_dataH[i][j] for i in range(nbVilles)) <= gamma, "Contrainte%d" % i)
            
    # Contrainte numéro deux : la somme des lignes de xij doivent être égale à 1
            
    nbLignes,nbColonnes = new_dataH.shape
    
    for i in range(nbLignes):
        mH.addConstr(quicksum(new_dataH[i,j] for j in range(nbColonnes)) == 1, "Contrainte%d" % i)
        
    # Contrainte numéro trois : max
    for i in range(nbVilles):
        mH.addConstr(quicksum(dH[i][j]*new_dataH[i][j] for j in range(nbVilles)) <= maxH, "Contrainte%d" % (i+nbLignes+k))
        
    # Contrainte numéro quatre : la somme de chaque colonne de xij doit être comprise entre 1 et nbVilles
    for i in range(nbLignes):
        mH.addConstr(quicksum(new_dataH[j,i] for j in range(nbColonnes)) >= k_ressources[i], "Contrainte%d" % i)
        mH.addConstr(quicksum(new_dataH[j,i] for j in range(nbColonnes)) <= k_ressources[i]*nbVilles, "Contrainte%d" % i)
    
    # Contrainte numéro cinq : la somme du vecteur k_ressources doit contenir k*1
    mH.addConstr(quicksum(k_ressources[i] for i in range(nbVilles)) == k, "Contrainte%d" % (i+1))
        
    objH = LinExpr();
    objH = maxH + epsilon*objValFx
    
    # definition de l'objectif
    mH.setObjective(objH,GRB.MINIMIZE)
    
    # Resolution
    mH.optimize()
    
    # indices des k ressources obtenues
    k_villes = getVillesFromIndices(villes,k_ressources)
    
    X = np.zeros((nbVilles,nbVilles))
    for i in range(nbVilles):
        for j in range(nbVilles):
            X[i,j] = new_dataH[i][j].x

    satH = getSatisfactions(X,k_villes)

    return X,mH.objVal,k_villes, satH

Xh, objValH, ressources, satH = getHx(alpha,objVal)


showResult(Xh,ressources,coordVilles,"h(x)","h")