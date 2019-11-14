from Exo1 import *

"""

    Question 2 : minimiser g(x) = max ∑ ( dij xij ) + epsilon * f(x)

"""

# Param k : nombre de ressources
# Param alpha : valeur strictement positif 
# Param ressources : les villes sélectionnées à la main
# Param objValFx : valeur de la fonction objectif f
# Return : valeur de la fonction objectif, Xij, satisfaction des maires
def getGx(k,alpha,ressources,objValFx):
    
    # initialisation du solveur Gurobi
    mG = Model("mogplex")     
    
    # declaration variables de decision
    xG = []
    for i in range(nbVilles*k):
        xG.append(mG.addVar(vtype=GRB.BINARY, lb=0, name="x%d" % (i+1)))
        
    # ajout var max
    max = mG.addVar(vtype=GRB.CONTINUOUS, obj=0, name="max")   
    
    # conversion liste à matrice
    dataG = np.array(xG)
    shape = (nbVilles,k)
    new_dataG = dataG.reshape(shape)
    
    # maj du modele pour integrer les nouvelles variables
    mG.update()
    
    # Contrainte numéro une : gamma
    
    for j in range(k):
        mG.addConstr(quicksum(matPopulations[i][j]*new_dataG[i][j] for i in range(nbVilles)) <= gamma, "Contrainte%d" % i)
            
    # Contrainte numéro deux : la somme des lignes de xij doivent être égale à 1
            
    nbLignes,nbColonnes = new_dataG.shape
    
    for i in range(nbLignes):
        mG.addConstr(quicksum(new_dataG[i,j] for j in range(nbColonnes)) == 1, "Contrainte%d" % i)
        
    # Contrainte numéro trois : une ville doit être affectée à son secteur si cette ville a été choisie explicitement
        
    for i in range(k):
        mG.addConstr(new_dataG[ressources[i]][i] == 1)
    
    # Contrainte numéro quatre : max
    
    for i in range(nbVilles):
        mG.addConstr(quicksum(d[i][j]*new_dataG[i][j] for j in range(k)) <= max, "Contrainte%d" % (i+nbLignes+k))
    
    # fonction objectif
    objG = LinExpr();
    objG = max + epsilon*objValFx
    
    # definition de l'objectif
    mG.setObjective(objG,GRB.MINIMIZE)
    
    # Resolution
    mG.optimize()
    
    # conversion "matrice gurobi" en une matrice normale
    X = np.zeros((nbVilles,k))
    for i in range(nbVilles):
        for j in range(k):
            X[i,j] = new_dataG[i][j].x
    
    # satisfaction moyenne et moins bien servi
    satisfactionsG = getSatisfactions(X,ressources)

    return mG.objVal, X, satisfactionsG

objValG,Xg,satG = getGx(k,alpha,ressources,objVal)

showResult(Xg,ressources,coordVilles,"fonction g(x)","g5")

fxg = getFxg(Xg,d,nbVilles)

PE = getPrixEquite(objVal,fxg)