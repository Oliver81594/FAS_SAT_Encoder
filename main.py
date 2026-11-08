import subprocess
from argparse import ArgumentParser

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

def variable_to_id(var, n):
    if var[0] == "P":
        i, j = map(int, [var[1], var[2]])
        return i*n + j
    else:
        i, j = map(int, [var[2], var[3]])
        return n**2 + i*n + j

def id_to_variable(id, n):
    prefix = "P"

    # we are decoding BE_ij
    if id > n**2:
        n -= n**2
        prefix = "BE"

    i, j = id // n, id % n
    return f"{prefix}{i}{j}"


def encode(instance):
    (k, n, m, edges) = instance

    cnf = []

    # encode the rules for permuting nodes

    # each node has at least one new position
    for u in range(n):
        clause = []
        for j in range(n):
            clause.append(variable_to_id(f"P{u}{i}"))
        cnf += clause

    # each position has at least one node assigned
    for i in range(n):
        clause = []
        for u in range(n):
            clause.append(variable_to_id(f"P{u}{i}"))
        cnf += clause

    # each node has at most one new position
    for u in range(n):
        clause = []
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                clause += [-variable_to_id(f"P{u}{i}"), -variable_to_id(f"P{u}{j}")]
        cnf += clause

    # each position has at most one node assigned
    for i in range(n):
        clause = []
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                clause += [-variable_to_id(f"P{u}{i}"), -variable_to_id(f"P{v}{i}")]
        cnf += clause


    # encode the rules for back edges
    for (u, v) in edges:
        for i in range(n):
            for j in range(i):
                clause = [-variable_to_id(f"P{u}{i}"), -variable_to_id(f"P{v}{j}"), variable_to_id(f"BE{i}{j}")]
                cnf += clause

    # encode "at most k" back edges
    

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into formula.cnf in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + '\n')

    # call the solver and return the output
    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)



if __name__ == "__main__":

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
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # load the input instance
    instance = load_instance(args.input)

    # encode the problem to create CNF formula
    cnf, nr_vars = encode(instance)

    # call the SAT solver and get the result
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)

