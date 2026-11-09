import subprocess
from argparse import ArgumentParser

from itertools import combinations

# Load problem instance from file
# Input description can be found in README
def load_instance(input_file_name):
    k, n, m, edges = 0, 0, 0, []
    with open(input_file_name, "r") as file:
        lines = file.readlines()
        k = int(lines[0].strip())
        n, m = map(int, lines[1].strip().split())
        for i in range(m):
            i, j = map(int, lines[2+i].strip().split())
            edges.append((i,j))

    return (k, n, m, edges)


# DIMACS requires all variables to be positive integer
# Negation of a variable is its negative value

# Translate variable to integer ID
def variable_to_id(var, n):
    if var[0] == "P":
        i, j = map(int, var[1:].split(","))
        return i*n + j + 1
    
    i, j = map(int, var[2:].split(","))
    return n**2 + i*n + j + 1

# Translate integer ID back to variable 
def id_to_variable(id, n):
    prefix = "P"
    id -= 1
    # we are decoding BE_ij
    if id >= n**2:
        id -= n**2
        prefix = "BE"

    i, j = id // n, id % n
    return f"{prefix}{i},{j}"


# Encode the problem instance into DIMACS CNF
def encode(instance):
    (k, n, m, edges) = instance

    cnf = []

    # Encode the rules for permuting nodes

    # Each node has at least one new position
    for u in range(n):
        clause = []
        for i in range(n):
            clause.append(variable_to_id(f"P{u},{i}", n))
        cnf.append(clause)

    # Each position has at least one node assigned
    for i in range(n):
        clause = []
        for u in range(n):
            clause.append(variable_to_id(f"P{u},{i}", n))
        cnf.append(clause)

    # Each node has at most one new position
    for u in range(n):
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                cnf.append([-variable_to_id(f"P{u},{i}", n), -variable_to_id(f"P{u},{j}", n)])
        
    # Each position has at most one node assigned
    for i in range(n):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                cnf.append([-variable_to_id(f"P{u},{i}", n), -variable_to_id(f"P{v},{i}", n)])

    # Encode the rules for back edges
    for (u, v) in edges:
        for i in range(n):
            for j in range(i):
                clause = [-variable_to_id(f"P{u},{i}", n), -variable_to_id(f"P{v},{j}", n), variable_to_id(f"BE{i},{j}", n)]
                cnf.append(clause)

    # Encode "at most k" back edges
    # At most k === at least one false in every subset of size k+1
    # Generate subsets of size k+1
    ij = []
    for i in range(n):
        for j in range(i):
            ij.append((i,j))
    subsets = list(combinations(ij, k+1))

    # Add clauses requiring at least one false in each subset
    for subset in subsets:
        cnf.append([-variable_to_id(f"BE{i},{j}", n) for (i,j) in subset])

    return cnf


# Call the compiled sovler with CNF
def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into formula.cnf in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + ' 0\n')

    # call the solver and return the output
    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)

# Apply inverse permution on a node
def unpermute(permutation, u):
    for p in permutation:
        if p[1] == u:
            return p[0]
        
# Decode the model returned by solver
def decode_model(model, n):
    permutation = []
    removed_edges_permuted = []
    removed_edges_original = []

    for m in model:
        # Ignore false variables
        if m < 0:
            continue

        # Decode the variable from ID
        var = id_to_variable(m, n)
        if var[0] == "P":
            i, j = map(int, var[1:].split(","))
            permutation.append((i,j))

        else:
            u, v = map(int, var[2:].split(","))
            removed_edges_permuted.append((u,v))

    # Apply reverse permutation on the edges
    for (u, v) in removed_edges_permuted:
        original_u_pos = unpermute(permutation, u)
        original_v_pos = unpermute(permutation, v)
        removed_edges_original.append((original_u_pos, original_v_pos))

    return removed_edges_original

# Print SAT solver output and statistics
def print_result(result, n, edges):
    # Print the whole output of the SAT solver to stdout
    for line in result.stdout.decode('utf-8').split('\n'):
        print(line)                 

    # Check the returned result
    # Returncode for SAT is 10, for UNSAT is 20

    if (result.returncode == 20):
        print("The given problem does not have a solution")
        return

    # Parse the model from the output of the solver
    # The model starts with 'v'
    model = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if line.startswith("v"):
            vars = line.split(" ")
            vars.remove("v")
            model.extend(int(v) for v in vars)      
    # 0 is the end of the model, just ignore it
    model.remove(0)

    print("\n##################################################################")
    print("#######################[ Feedback Arc Set ]#######################")
    print("##################################################################\n")
    
    # Decode the meaning of the assignment
    feedback_arc_set = decode_model(model, n)

    print("Remove the following edges to get an acyclic graph: ")
    for (u, v) in feedback_arc_set:
        if (u, v) in edges:
            print(f"{u} -> {v}")

# Parse CLI arguments
def parse_arguments():
    parser = ArgumentParser()
    
    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # Load the input instance
    instance = load_instance(args.input)
    (k, n, m, edges) = instance

    # Dumb Heuristics
    # If k > number of edges, we remove all of them = the resulting graph is acyclic
    if k >= m:
        print("Remove the following edges to get an acyclic graph: ")
        for edge in edges:
            print(edge)
    
    else:
        # Encode the problem to create CNF formula
        cnf = encode(instance)
        nr_vars = max(abs(lit) for clause in cnf for lit in clause)

        # Call the SAT solver and get the result
        result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)

        print_result(result, n, edges)