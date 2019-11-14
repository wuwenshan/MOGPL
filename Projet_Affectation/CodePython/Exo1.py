from Utilitaire import *

"""

    Question 1 : minimiser le coût social de la solution, défini par f(x) = ∑ ∑ ( dij xij )

"""

# Param k : nombre de ressources
# Param alpha : valeur strictement positif 
# Param ressources : les villes sélectionnées à la main
# Return : valeur de la fonction objectif, Xij, satisfaction des maires
def getFx(k,alpha,ressources):
    
    # initialisation du solveur Gurobi
    m = Model("mogplex")     

    # declaration variables de decision
    x = []
    for i in range(nbVilles*k):
        x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="x%d" % (i+1)))

    # maj du modele pour integrer les nouvelles variables
    m.update()

    # conversion de la liste x à une matrice
    data = np.array(x)
    shape = (nbVilles,k)
    new_data = data.reshape(shape)

    # Matrice Dij
    d = getMatriceDij(villes,distances,k,ressources)
    
    # Fonction objectif
    obj = LinExpr();
    obj = 0
    for i in range(nbVilles):
        for j in range(k):
            obj += d[i][j] * new_data[i][j]
    
    # definition de l'objectif
    m.setObjective(obj,GRB.MINIMIZE)
    
    ## définition des contraintes
    
    # Contrainte numéro une : gamma
    
    for j in range(k):
        m.addConstr(quicksum(matPopulations[i][j]*new_data[i][j] for i in range(nbVilles)) <= gamma, "Contrainte%d" % i)
            
    # Contrainte numéro deux : la somme des lignes de xij doivent être égale à 1
            
    nbLignes,nbColonnes = new_data.shape
    
    for i in range(nbLignes):
        m.addConstr(quicksum(new_data[i,j] for j in range(nbColonnes)) == 1, "Contrainte%d" % i)
        
    # Contrainte numéro trois : une ville doit être affectée à son secteur si cette ville a été choisie explicitement
        
    for i in range(k):
        m.addConstr(new_data[ressources[i]][i] == 1)
    
    # Resolution
    m.optimize()
    
    # Conversion matrice gurobi à matrice normale
    X = np.zeros((nbVilles,k))
    for i in range(nbVilles):
        for j in range(k):
            X[i,j] = new_data[i][j].x
    
    # satisfaction moyenne et moins bien servi
    satisfactions = getSatisfactions(X,ressources)

    return m.objVal,X,satisfactions

objVal,X,sat = getFx(k,alpha,ressources)    

showResult(X,ressources,coordVilles,"fonction f(x)","f3")