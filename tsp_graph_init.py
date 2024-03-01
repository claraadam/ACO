import csv
import random
import numpy as np
import tkinter as tk
from tkinter import Canvas, Label, Text
import time

class Lieu():
    """Mémoriser les coordonnées x et y du lieu à visiter et son nom"""
    def __init__(self, x, y):
        """Initialiser un lieu"""
        self.x = x
        self.y = y

    def distance(self, autre_lieu):
        """Calcul de distance entre 2 lieux"""
        distance = np.sqrt((self.x-autre_lieu.x)**2+(self.y-autre_lieu.y)**2)
        return distance


class Graph:
    LARGEUR=800
    HAUTEUR=600
    NB_LIEUX = 20
    def __init__(self,fichier_csv):
        
        self.matrice_od = np.zeros((self.NB_LIEUX,self.NB_LIEUX))
        self.fichier_csv =fichier_csv 

        self.liste_lieux=self.generer_coordonnees_lieux()
        self.liste_lieux = self.charger_graph()
        self.matrice_od=self.calcul_matrice_cout_od()
        self.pheromone_matrix = np.ones((Graph.NB_LIEUX, Graph.NB_LIEUX))
    
    def generer_coordonnees_lieux(self):
        self.liste_lieux = []
        if self.fichier_csv == None:
            for i in range(self.NB_LIEUX):
                self.liste_lieux.append((random.randint(0, self.LARGEUR), random.randint(0, self.HAUTEUR)))
        return self.liste_lieux

    def calcul_matrice_cout_od(self):
        
        for i in range(self.NB_LIEUX):
            for j in range(i+1,self.NB_LIEUX):
                    lieu1 = Lieu(self.liste_lieux[i][0],self.liste_lieux[i][1])
                    lieu2 = Lieu(self.liste_lieux[j][0],self.liste_lieux[j][1])
                    distance = lieu1.distance(lieu2)
                    self.matrice_od[i][j] = distance
                    self.matrice_od[j][i] = distance
        return self.matrice_od
    
    def plus_proche_voisin(self, lieu,voisins):
        ligne = self.matrice_od[lieu,[voisins]]
        indice =voisins[np.argmin(ligne)]
        return indice
    
    def charger_graph(self):
        if self.fichier_csv != None :
            with open(self.fichier_csv, 'r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader: 
                    self.liste_lieux.append((float(row[0]),float(row[1])))
        return self.liste_lieux

    def calcul_distance_route(self,route=None):
        longueur_totale = 0
        if route == None:
            longueur_totale=float('inf')
        else:
            for index in range(len(route)-1):
                i = route[index]
                j = route[index+1]
                longueur_totale+=self.matrice_od[i][j]
        return longueur_totale


class Route():
    """Générer une route traversant tous les lieux d'un graph"""
    def __init__(self,graphe,tsp_aco):
        """Initialiser une route possible"""
        self.tsp_aco = tsp_aco
        self.routes = []
        self.graphe = graphe
        self.liste_lieux = list(np.arange(0,graphe.NB_LIEUX))
        #self.distance_route = graphe.calcul_distance_route(self.ordre)
        
        
    def generer_route(self,i):
        """Génère une route traversant tous les lieux avec la contrainte de la base."""
        route = [0]  # Le premier lieu à visiter est toujours le lieu de la base
        lieux_non_visites =self.liste_lieux
        lieux_non_visites.remove(0)
        while len(lieux_non_visites)>0:
            if i==0:
                prochain_lieu = self.graphe.plus_proche_voisin(route[-1],lieux_non_visites)
            else:
                prochain_lieu = self.tsp_aco.proba(route[-1],lieux_non_visites)
            route.append(prochain_lieu)
            lieux_non_visites.remove(prochain_lieu)

        route.append(0)  # Le dernier lieu à visiter est à nouveau le lieu de la base
        self.routes.append(route)
        return route


class Affichage :
    def __init__(self, graphe):
        self.graphe = graphe
        self.root = tk.Tk()
        self.root.title("G1 - Clara Adam - Julie Guitton - Fourmis")

        self.LARGEUR = 800
        self.HAUTEUR = 550

        self.canvas = Canvas(self.root, width=self.LARGEUR, height=self.HAUTEUR, bg="white")
        self.canvas.pack()

        self.texte_info = Text(self.root, height=90, width=60)
        self.texte_info.pack()
        
        self.phe=False
        self.root.bind("<KeyPress>", lambda event: self.gerer_touche(event))
        self.root.bind("<Escape>", lambda event: self.quitter_programme(event))
        
    def afficher_lieux(self):
        for lieu in self.graphe.liste_lieux:
            x, y = lieu[0], lieu[1]
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="lightblue")
            self.canvas.create_text(x, y, text=str(self.graphe.liste_lieux.index(lieu)), fill="black")

    def afficher_meilleure_route(self, meilleure_route):
        for i in range(len(meilleure_route) - 1):
            lieu_actuel = self.graphe.liste_lieux[meilleure_route[i]]
            prochain_lieu = self.graphe.liste_lieux[meilleure_route[i + 1]]

            x1, y1 = lieu_actuel[0], lieu_actuel[1]
            x2, y2 = prochain_lieu[0], prochain_lieu[1]

            self.canvas.create_line(x1, y1, x2, y2, fill="blue", dash=(4, 2))
            self.canvas.create_text(x2-15, y2-15, text=str(meilleure_route[1::].index(self.graphe.liste_lieux.index(prochain_lieu))+1), fill="blue")

    def afficher_pheromones(self, pheromones):
        for i in self.graphe.liste_lieux:
            for j in self.graphe.liste_lieux[self.graphe.liste_lieux.index(i)+1::]:
                    lieu1 = Lieu(i[0],i[1])
                    lieu2 = Lieu(j[0],j[1])
                    self.canvas.create_line(lieu1.x, lieu1.y, lieu2.x, lieu2.y, fill="grey", width = pheromones[self.graphe.liste_lieux.index(i)][self.graphe.liste_lieux.index(j)],)

    def gerer_touche(self, event):
        touche = event.keysym

        if touche == "a":
            if self.phe == False:
                self.phe = True
            else:
                self.phe = False

    def afficher_texte(self,i,meilleure_route,distance):
        texte = f"Iteration : {i}\nMeilleure distance : {distance}, \n meilleure route:{meilleure_route}"
        self.texte_info.delete(1.0, tk.END)  # Efface le texte actuel
        self.texte_info.insert(tk.END, texte)

    def quitter_programme(self, event):
        self.root.destroy()

    def update(self, pheromones, meilleure_route,i, distance):
        self.canvas.delete("all")
        if self.phe == True:
            self.afficher_pheromones(pheromones)
        self.afficher_lieux()
        self.afficher_meilleure_route(meilleure_route)
        self.afficher_texte(i,meilleure_route,distance)
        self.root.update_idletasks()
        self.root.update()