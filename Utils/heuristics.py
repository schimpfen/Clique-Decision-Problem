import numpy as np
from numba import jit
import networkx as nx
from Utils import dataloader as dl

@jit(nopython=True, cache=True)
def isClique(nodes: np.array, adjmat: np.array):
    """
    Verify the current selection of nodes constitutes a clique
    method for checking edges from:
    :param nodes:
    :param adjmat:
    :return:
    """
    submat = adjmat[nodes == 1][:, nodes == 1]
    np.fill_diagonal(submat,1)
    return submat.sum() == submat.size

@jit(nopython=True)
def get_edgecount(adjmat: np.array):
    edgecount = np.zeros(len(adjmat))
    for i in range(len(edgecount)):
        edgecount[i] = adjmat[i].sum()
    return edgecount

@jit(nopython=True)
def BackKhuriFitness(ind: np.array, adjMat: np.array):
    """
    Proposed fitness function
    incorporates graded penalty to harshly reduce the presence of infeasible individuals
    :param pop: population, each individual is indicating the presence of each node
    :return: fitness score of the individual
    """
    fit = 0.
    for i in range(len(ind)):
        pen = 0
        for j in range(i,len(ind)):
            pen += ind[j]*adjMat[i,j]
        fit += (ind[i] - len(ind)*ind[i]*pen)
    return fit


def cliqueSize(nodelist: np.array, adjMat: np.array):
    if isClique(nodelist, adjMat): return nodelist.sum()
    else: return 0

@jit(nopython=True)
def BKFitPop(pop: np.array, adjmat: np.array):
    """
    wrapper for BackKhuriFitness across complete population
    :param pop: population matrix
    :param adjmat:adjacency matrix
    :return:
    """
    fit = np.zeros((len(pop)))
    for i in range(len(fit)):
        fit[i] = BackKhuriFitness(pop[i], adjmat)
    # total = fit.sum()
    # for i in range(len(fit)): fit[i] = fit[i] / total
    return fit

def MarchRecursive(population: np.array, adjMat: np.array):
    """
    Wrapper function for MarchioriRepair
    :param population:
    :param adjMat:
    :return:
    """
    for i in range(len(population)):
        population[i] = MarchioriRepair(population[i], adjMat)
    return population

def MarchioriRepair(individual: np.array, adjMat: np.array):
    """
    Steps 2 and 3 of the heuristic algorithm in
    "A Simple Heuristic Based Genetic Algorithm for the Maximum Clique Problem" (Marchiori)
    :param individual: a nodelist
    :param adjMat: the adjacency matrix of the complete graph
    :return: repaired nodelists
    """
    # Step 1. Repair by deleting nodes until a clique is formed
    while (not isClique(individual, adjMat)) and (individual.sum() > 1):
        idx_ones = np.where(individual == 1)[0]
        individual[idx_ones[np.random.randint(0,high=len(idx_ones))]] = 0

    # Step 2. Extend the clique with randomly-selected node
    accept = False; idx_node = -1
    while not accept:
        idx_node = np.random.randint(0,high=len(individual))
        if individual[idx_node] == 0: accept = True

    tmp = individual.copy()
    tmp[idx_node] = 1
    if isClique(tmp, adjMat): return tmp
    else: return individual