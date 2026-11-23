from cnf import CNF

class CSP:
    def __init__(self, cnf: CNF, use_mcv=True, use_mrv=True, use_lcv=True):
        self.cnf = cnf
        self.use_mcv = use_mcv
        self.use_mrv = use_mrv
        self.use_lcv = use_lcv
        self.assigned_variables = {var: None for var in cnf.variables}
        self.constraints = []
        self.var_constraints = {}
        self.best_solution = None
        self.best_weight = -1

    def add_variable(self, variable, domain):
        self.assigned_variables[variable] = None

    def add_constraint(self, constraint_function, variables):
        self.constraints.append((constraint_function, variables))

    def assign(self, variable, value):
        self.assigned_variables[variable] = value
        if variable.startswith('~'):
            self.assigned_variables[variable[1:]] = not value
        else:
            self.assigned_variables['~' + variable] = not value

    def unassign(self, variable):
        self.assigned_variables[variable] = None
        if variable.startswith('~'):
            self.assigned_variables[variable[1:]] = None
        else:
            self.assigned_variables['~' + variable] = None

    def is_consistent(self, variable, value):
        self.assign(variable, value)
        for constraint_function, variables in self.constraints:
            if variable in variables:
                if not constraint_function(self.assigned_variables, variables):
                    self.unassign(variable)
                    return False
        self.unassign(variable)
        return True

    def is_complete(self):
        return all(value is not None for value in self.assigned_variables.values())

    def select_unassigned_variable(self):
        unassigned_vars = [var for var, value in self.assigned_variables.items() if value is None]
        if self.use_mcv:
            return self.most_constraining_variable(unassigned_vars)
        elif self.use_mrv:
            return self.minimum_remaining_value()
        else:
            return unassigned_vars[0]

    def most_constraining_variable(self, unassigned_variables):
        most_constrained_var = None
        max_constraints = -1
        for var in unassigned_variables:
            num_constraints = len([c for c in self.constraints if var in c[1]])
            if num_constraints > max_constraints:
                most_constrained_var = var
                max_constraints = num_constraints
        return most_constrained_var

    def minimum_remaining_value(self):
        min_remaining_values_var = None
        min_remaining_values = float('inf')
        for var in self.assigned_variables:
            if self.assigned_variables[var] is None:
                remaining_values = 2
                if remaining_values < min_remaining_values:
                    min_remaining_values_var = var
                    min_remaining_values = remaining_values
        return min_remaining_values_var

    def solve(self):
        if self.is_complete():
            if all(self.cnf.evaluate_clause(clause, self.assigned_variables) for clause in self.cnf.hard_clauses):
                solution = {var: val for var, val in self.assigned_variables.items() if not var.startswith('~')}
                total_weight = self.cnf.calculate_weight(self.assigned_variables)
                if total_weight > self.best_weight:
                    self.best_weight = total_weight
                    self.best_solution = solution
                return solution, total_weight
            else:
                return None, 0

        variable = self.select_unassigned_variable()

        if self.use_lcv:
            domain_values = self.least_constraining_value(variable)
        else:
            domain_values = [True, False]

        for value in domain_values:
            if self.is_consistent(variable, value):
                self.assign(variable, value)
                result, answer = self.solve()
                if result:
                    return result, answer
                self.unassign(variable)

        return None, 0

    def least_constraining_value(self, unassigned_variables):
        possible_values = [True, False]
        value_costs = []

        for value in possible_values:
            self.assign(unassigned_variables, value)
            cost = 0
            for constraint_function, variables in self.constraints:
                if not constraint_function(self.assigned_variables, variables):
                    cost += 1
            value_costs.append((value, cost))
            self.unassign(unassigned_variables)

        value_costs.sort(key=lambda x: x[1])

        return [value for value, _ in value_costs]
    def calculate_upper_bound(self):
        upper_bound = 0
        for clause in self.cnf.soft_clauses:
            clause_vars = clause[:-1]
            weight = int(clause[-1])
            is_contradicted = True
            for lit in clause_vars:
                if lit[0] == '~':
                    var = lit[1:]
                    val = self.assigned_variables.get(var, None)
                    if val is None or val is False:
                        is_contradicted = False
                        break
                else:
                    var = lit
                    val = self.assigned_variables.get(var, None)
                    if val is None or val is True:
                        is_contradicted = False
                        break
            if not is_contradicted:
                upper_bound += weight
        return upper_bound

    def branch_and_bound_solve(self):
        """
        حل مسئله با روش Branch and Bound
        """
        stack = []
        stack.append(dict(self.assigned_variables))

        while stack:
            current_assign = stack.pop()
            self.assigned_variables = dict(current_assign)

            if self.is_complete():
                
                if all(self.cnf.evaluate_clause(clause, self.assigned_variables) 
                       for clause in self.cnf.hard_clauses):
                    total_weight = self.cnf.calculate_weight(self.assigned_variables)
                    if total_weight > self.best_weight:
                        self.best_weight = total_weight
                        self.best_solution = {
                            var: val for var, val in self.assigned_variables.items()
                            if not var.startswith('~')
                        }
            else:
                
                upper_bound = self.calculate_upper_bound()
                if upper_bound > self.best_weight:
                    var = self.select_unassigned_variable()
                    if var is None:
                        continue
                    if self.use_lcv:
                        domain_values = self.least_constraining_value(var)
                    else:
                        domain_values = [True, False]
                    for val in domain_values:
                        if self.is_consistent(var, val):
                            self.assign(var, val)
                            new_assign = dict(self.assigned_variables)
                            stack.append(new_assign)
                            self.unassign(var)

        
        if self.best_solution:
            for v in self.best_solution:
                self.assigned_variables[v] = self.best_solution[v]
        else:
            for v in self.assigned_variables:
                self.assigned_variables[v] = None

        return self.best_solution, self.best_weight