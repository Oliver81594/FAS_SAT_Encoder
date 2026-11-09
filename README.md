# Feedback Arc Set - SAT Encoder and Solver

This project is part of Propositional and Predicate Logic (NAIL062) course assesment. 

## Problem Description
We are given a directed graph, a natural number $k$ and need to answer whether it is possible to remove at most $k$ edges such that the resulting subgraph is acyclic.
The set of removed edges is called Feedback Arc Set.

**Input:** 
- natural number $k$
- graph $G$
	- we assume the nodes are numbered from $0$
	- lets denote: 
		- $n = |G(V)|$
		- $m = |G(E)|$

**Output:** 
- Feedback Arc Set of size at most $k$ if possible
- a negative answer if not possible

## Main Idea
We take all the vertices, arrange them on a line (as if in topological sort), and get two types of edges:
 - *forward* - going from $i$ to $j$, where $i<j$
 - *backward* - going from $i$ to $j$, where $j<i$
If the number of backward edges is at most k, we can remove them and thus get a valid topological sort which means that the remaining subgraph is acyclic.

## Encoding
### Variables
- $P_{i, j}$ 
	- states that node $i$ is on position $j$
	- we will define this for all nodes and positions, which gives us $n^2$ variables
- $BE_{i,j}$ 
	- states that there is a back edge going from node on $i$-th position to node on $j$-th position
	- exists only for $j < i$, otherwise it would not be a back edge
	- this produces $\frac{n^2 - n}{2}$ variables

### Rules
For our permutation of nodes to be valid we need:
- every node to have exactly one position
	- $\{\bigvee_{i \in V(G)} P_{v, i} | \forall v \in V(G)\}$
	- $\{\bigwedge_{j, k \in V(G), j\neq k} \neg P_{v,j} \vee \neg P_{v,k}  | \forall v \in V(G)\}$
- every position to be occupied by exactly one node
	- $\{\bigvee_{v \in V(G)} P_{v, i} | \forall i \in V(G)\}$
	- $\{\bigwedge_{u,v \in V(G), u \neq v} \neg P_{u, i} \vee \neg P_{v, i} | \forall i \in V(G)\}$

For our back edges we need:
- the back edge to exist
	- $\forall (u,v) \in G(E),\ \forall\, 0 \le j < i \lt n: P_{u,i} \wedge P_{v,j} \implies BE_{i,j}$ 
		which in CNF can be written as 
		$\forall (u,v) \in G(E),\ \forall\, 0 \le j < i \lt n: \neg P_{u,i} \vee \neg P_{v,j} \vee BE_{i,j}$
- there is at most $k$ of them
	- $\{\bigvee_{(i,j) \in S} \neg BE_{i,j}  | S \subseteq \{(i,j) | 0 \leq j < i \lt n \}, |S|=k+1 \}$


Questions:
- weighted or unweighted graph
- can k be zero
- are there loops
- can we use built in "at most k" rule
- can I use combinations lib for subsets of size k+1

