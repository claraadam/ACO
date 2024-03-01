import numpy as np
import random
from tsp_graph_init import Graph
from tsp_graph_init import Route
from tsp_graph_init import Affichage

class TSP_ACO:
    def __init__(self, graph, alpha=0.1, beta=0.9,rho =0.1):
        self.graph = graph
        self.alpha = alpha
        self.rho = rho
        self.beta = beta
        self.best_distance = float('inf')
        self.pheromone_matrix = np.ones((graph.NB_LIEUX, graph.NB_LIEUX))
        self.pheromone_matrix *= 1 / graph.NB_LIEUX

    def proba(self,lieu,voisins):
        pheromones = self.pheromone_matrix[lieu, [voisins]][0]
        distances = self.graph.matrice_od[lieu, [voisins]][0]
        inverse_distances= list(map(lambda x: 1/x, distances))
        proba_distance =[]
        proba_pheromone=[]
        probas = []
        sum_distances = sum(inverse_distances)
        sum_pheromones = sum(pheromones)
        for distance in inverse_distances :
            proba_distance.append(distance/sum_distances)
        for pheromone in pheromones:
            proba_pheromone.append(pheromone/sum_pheromones)
 
        for i in range(len(proba_distance)):
            probas.append(self.alpha*proba_distance[i]+self.beta*proba_pheromone[i])
        #indice = voisins[probas.index(random.choices(probas))]
        indice = random.choices(voisins,probas)
        return indice[0]
    
    def update_pheromones(self, route, graphe, q):
        
        # Dépôt des phéromones par les fourmis
        pheromone_deposit = q / graphe.calcul_distance_route(route)
        for i in range(len(route) - 1):
            
        
            self.pheromone_matrix[route[i]][route[i + 1]] += pheromone_deposit
            self.pheromone_matrix[route[i + 1]][route[i]] += pheromone_deposit
           
        
    def update_evaporation(self):
            self.pheromone_matrix *= (1-self.rho)

# Example of usage
if __name__ == "__main__":
    graphe = Graph("graph_20.csv")
    aco = TSP_ACO(graphe)
    affichage = Affichage(graphe)
    meilleure_route=None
    num_ant = 200
   
    for i in range(1000):
        routes=[]
        for j in range(num_ant):
    
            R = Route(graphe,aco)

            route = R.generer_route(i)
            routes.append(route)
            print(route)
            print(graphe.calcul_distance_route(route))
            if graphe.calcul_distance_route(route) <= graphe.calcul_distance_route(meilleure_route):
                meilleure_route = route 
            
        for route in routes: 
            aco.update_pheromones(route,graphe,100)
        aco.update_evaporation()
       
                
        affichage.update(aco.pheromone_matrix,meilleure_route,i, graphe.calcul_distance_route(meilleure_route))
        
