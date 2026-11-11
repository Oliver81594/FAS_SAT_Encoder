# Feedback Arc Set - SAT Encoder and Solver

This project is part of Propositional and Predicate Logic (NAIL062) course assesment. Goal is to choose a problem, Feedback Arc Set in my case, encode it to CNF feed it to a SAT solver and decode the result back into a human readable format.

The SAT solver used is [Glucose](https://www.labri.fr/perso/lsimon/research/glucose/), more specifically [Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1). There is a compiled version present in the repository. For the best experience it is encouraged to compile your own.

# Documentation
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


## User documentation
**Basic usage:** 
```
main.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]
```

**Command-line options:**
* `-h`, `--help` : Show a help message and exit.
* `-i INPUT`, `--input INPUT` : The instance file. Default: "input.in".
* `-o OUTPUT`, `--output OUTPUT` : Output file for the DIMACS format (i.e. the CNF formula).
* `-s SOLVER`, `--solver SOLVER` : The SAT solver to be used.
*  `-v {0,1}`, `--verb {0,1}` :  Verbosity of the SAT solver used.

**Input format:**
The input for this problem has to have the following format in order to work:
**FileName:** *Example.in*
- **First Line:** nonnegative integer $k$
- **Second Line:** integers $n$ and $m$, separated by whitespace, indicating number of vertices and edges respectively
- **m lines:** each containing two integers, vertices which are connected by an edge

**Example:**
```
1 
2 2
1 2
2 1
```
This is an encoding of a graph with $2$ vertices and $2$ edges, creating a single cycle. For this particular problem with $k=1$ the solver should output $True$ and either of the edges - it is enought to remove $1$ edge to destroy the only cycle present.

**Important Note:**  Vertices need to be numbered from $0$ to $n-1$

## Technical Documentation
### Main Idea
We take all the vertices, arrange them on a line (as if in topological sort), and get two types of edges:
 - *forward* - going from $i$ to $j$, where $i<j$
 - *backward* - going from $i$ to $j$, where $j<i$
 
If the number of backward edges is at most k, we can remove them and thus get a valid topological sort which means that the remaining subgraph is acyclic.

### Encoding
#### Variables
- $P_{i, j}$ 
	- states that node $i$ is on position $j$
	- we will define this for all nodes and positions, which gives us $n^2$ variables
- $BE_{i,j}$ 
	- states that there is a back edge going from node on $i$-th position to node on $j$-th position
	- exists only for $j < i$, otherwise it would not be a back edge
	- this produces $\frac{n^2 - n}{2}$ variables

#### Rules
For our permutation of nodes to be valid we need:
- every node to have exactly one position
	- $`\{\bigvee_{i \in V(G)} P_{v, i} | \forall v \in V(G)\}`$
	- $`\{\bigwedge_{j, k \in V(G), j\neq k} \neg P_{v,j} \vee \neg P_{v,k}  | \forall v \in V(G)\}`$
- every position to be occupied by exactly one node
	- $`\{\bigvee_{v \in V(G)} P_{v, i} | \forall i \in V(G)\}`$
	- $`\{\bigwedge_{u,v \in V(G), u \neq v} \neg P_{u, i} \vee \neg P_{v, i} | \forall i \in V(G)\}`$

For our back edges we need:
- the back edge to exist
	- $`\forall (u,v) \in G(E),\ \forall\, 0 \le j < i \lt n: P_{u,i} \wedge P_{v,j} \implies BE_{i,j}`$ 

		which in CNF can be written as 
		
		$`\forall (u,v) \in G(E),\ \forall\, 0 \le j < i \lt n: \neg P_{u,i} \vee \neg P_{v,j} \vee BE_{i,j}`$
- there is at most $k$ of them
	- $`\{\bigvee_{(i,j) \in S} \neg BE_{i,j}  | S \subseteq \{(i,j) | 0 \leq j < i \lt n \}, |S|=k+1 \}`$


Questions:
- are there loops
- can I use combinations lib for subsets of size k+1
- paralel edges

