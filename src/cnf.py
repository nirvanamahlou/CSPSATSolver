class CNF:
    def __init__(self, variables, hard_clauses, soft_clauses):
        """
        Initializes a Conjunctive Normal Form (CNF) object.

        Args:
            variables (list): List of variable names.
            hard_clauses (list): List of hard clauses.
            soft_clauses (list): List of soft clauses with weights at the end.
        """
        self.hard_clauses = hard_clauses
        self.soft_clauses = soft_clauses
        self.variables = variables

    def evaluate_clause(self, clause, assignments):
        """
        Evaluates if a clause is satisfied given the assignments.

        Args:
            clause (list): The list of literals in the clause.
            assignments (dict): Current assignments of variables.

        Returns:
            bool: True if the clause is satisfied, False otherwise.
        """
        for literal in clause:
            if literal[0] == '~':  
                var = literal[1:]  
                value = assignments.get(var, None)  
                if value is None:
                    continue  

                
                if value == False:
                    return True
            else:
                var = literal
                value = assignments.get(var, None)  
                if value is None:
                    continue 

                
                if value == True:
                    return True
        return False

    def calculate_weight(self, assignments):
        """
        Calculates the weight of satisfied soft clauses.

        Args:
            assignments (dict): Current assignments of variables.

        Returns:
            int: The sum of weights for satisfied soft clauses.
        """
        total_weight = 0
        for clause in self.soft_clauses:
            clause_variables = clause[:-1]  
            weight = int(clause[-1])  
            if self.evaluate_clause(clause_variables, assignments):
                total_weight += weight
        return total_weight
