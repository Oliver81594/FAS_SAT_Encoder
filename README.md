# Feedback Arc Set - SAT Encoder and Solver

This project is part of Propositional and Predicate Logic (NAIL062) course assesment. 

## Problem Description
We are given a directed graph and a number $k$ and need to answer whether it is possible to remove at most k edges such that the resulting subgraph is acyclic.
The set of removed edges is called Feedback Arc Set.
**Input:** graph G and natural number k
**Output:** YES/NO answered by the SAT Solver

## Main Idea
We can take all the vertices arrange them on a line and get two types of edges:
 - *forward* - going from $i$ to $j$, where $i<j$
 - *backward* - going from $i$ to $j$, where $j<i$
If the number of backward edges is at most k, we can remove them and thus get a acyclic graph.
 
## Encoding
On input we receive a Graph, that is a set of nodes and edges.
Lets nunmber the nodes from 1 to n. Variable $E_{ij}$ will denote whether there is an edge from node i to node j.


Questions:
- weighted or unweighted graph
- can k be zero?
