class SudokuMineSolver:
    def __init__(self, input_file):
        """
        Initialization
        """
        self.grid = []  # 9x9 grid with initial values (0-8)
        self.solution = [[0] * 9 for _ in range(9)]  # Solution grid (0 or 1)
        self.variables = []  # List of (row, col) tuples for empty cells
        self.domains = {}  # Domain for each variable: {(r,c): {0, 1}}
        self.nodes_generated = 0  # Count of nodes in search tree
        self.goal_depth = 0  # Depth at which solution was found

        self.read_input(input_file)
        self.initialize_csp()

    def read_input(self, input_file):
        """Read the input puzzle from file"""
        with open(input_file, 'r') as f:
            for line in f:
                row = list(map(int, line.strip().split()))
                self.grid.append(row)

    def initialize_csp(self):
        """
        Initialize the CSP formulation
        """
        # Identify variables (empty cells only)
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    self.variables.append((r, c))
                    self.domains[(r, c)] = {0, 1}

        print(f"Total variables (empty cells): {len(self.variables)}")

    def get_neighbors(self, row, col):
        """
        Get the 8-neighbors of a cell (horizontally, vertically, diagonally adjacent)
        """
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 9 and 0 <= nc < 9:
                    neighbors.append((nr, nc))
        return neighbors

    def get_block(self, row, col):
        """Get the 3x3 block index (0-8) for a given cell"""
        return (row // 3) * 3 + (col // 3)

    def check_row_constraint(self, row, assignment):
        mines = 0
        unassigned = 0
        
        for c in range(9):
            var = (row, c)
            if var in self.variables:
                if var in assignment:
                    mines += assignment[var]
                else:
                    unassigned += 1
        
        # Cannot exceed 3 mines
        if mines > 3:
            return False
        
        # If all variables in row are assigned, must have exactly 3 mines
        if unassigned == 0 and mines != 3:
            return False
        
        # Check if remaining unassigned cells can still reach exactly 3
        if mines + unassigned < 3:
            return False
        
        return True

    def check_col_constraint(self, col, assignment):
        mines = 0
        assigned_cells = 0
        
        for r in range(9):
            var = (r, col)
            if var in assignment:
                assigned_cells += 1
                mines += assignment[var]
        
        # Cannot exceed 3 mines
        if mines > 3:
            return False
        
        # If all cells in column that are variables are assigned, must have exactly 3 mines
        if assigned_cells == len([1 for r in range(9) if (r, col) in self.variables]):
            if mines != 3:
                return False
        
        return True


    def check_block_constraint(self, row, col, assignment):
        pass

    def check_numbered_constraints(self, var, value, assignment):
        pass

    def is_consistent(self, var, value, assignment):
        """
        Check if assigning value to var is consistent with current assignment
        """
        # Create temporary assignment
        temp_assignment = assignment.copy()
        temp_assignment[var] = value

        row, col = var

        # Check all constraints
        if not self.check_row_constraint(row, temp_assignment):
            return False

        if not self.check_col_constraint(col, temp_assignment):
            return False

        if not self.check_block_constraint(row, col, temp_assignment):
            return False

        if not self.check_numbered_constraints(var, value, temp_assignment):
            return False

        return True

    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        
        if not unassigned:
            return None
        
        min_domain_size = min(len(self.domains[v]) for v in unassigned)
        mrv_vars = [v for v in unassigned if len(self.domains[v]) == min_domain_size]
        
        if len(mrv_vars) == 1:
            return mrv_vars[0]
        
        best_var = None
        max_degree = -1
        
        for v in mrv_vars:
            degree = self.count_constraints(v, assignment)
            if degree > max_degree:
                max_degree = degree
                best_var = v
        
        return best_var

    def count_constraints(self, var, assignment):
        row, col = var
        constrained_vars = set()
        
        # Row constraint neighbors
        for c in range(9):
            v = (row, c)
            if v in self.variables and v not in assignment and v != var:
                constrained_vars.add(v)
        
        # Column constraint neighbors
        for r in range(9):
            v = (r, col)
            if v in self.variables and v not in assignment and v != var:
                constrained_vars.add(v)
        
        # Block constraint neighbors
        block_row = (row // 3) * 3
        block_col = (col // 3) * 3
        for r in range(block_row, block_row + 3):
            for c in range(block_col, block_col + 3):
                v = (r, c)
                if v in self.variables and v not in assignment and v != var:
                    constrained_vars.add(v)
        
        # 8-neighbors constraint
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] > 0:  # Numbered cell
                    neighbors = self.get_neighbors(r, c)
                    if var in neighbors:
                        # All neighbors of this numbered cell are constrained together
                        for nr, nc in neighbors:
                            v = (nr, nc)
                            if v in self.variables and v not in assignment and v != var:
                                constrained_vars.add(v)
        
        return len(constrained_vars)

    def forward_check(self, var, value, assignment):
        pass

    def restore_domains(self, removed):
        """
        Restore domains after backtracking
        """
        for var, values in removed.items():
            self.domains[var] |= values

    def backtrack(self, assignment, depth):
        """
        Backtracking search algorithm
        """
        print("Assignment size:", len(assignment), " out of ", len(self.variables))
        var = self.select_unassigned_variable(assignment)
        print("Selected var:", var)

        self.nodes_generated += 1

        # Check if assignment is complete
        if len(assignment) == len(self.variables):
            self.goal_depth = depth
            return assignment

        # Select unassigned variable using MRV + Degree heuristic
        var = self.select_unassigned_variable(assignment)

        # Try values in order {0, 1}
        for value in [0, 1]:
            if value not in self.domains[var]:
                continue

            if self.is_consistent(var, value, assignment):
                # Make assignment
                assignment[var] = value

                # Forward checking
                removed = self.forward_check(var, value, assignment)

                if removed is not None:  # No domain wipeout
                    result = self.backtrack(assignment, depth + 1)
                    if result is not None:
                        return result

                    # Restore domains
                    self.restore_domains(removed)

                # Remove assignment (backtrack)
                del assignment[var]

        return None

    def solve(self):
        """Solve the Sudoku Mine puzzle"""
        print("Starting backtracking search...")
        assignment = self.backtrack({}, 0)

        if assignment is None:
            print("No solution found!")
            return False

        # Convert assignment to solution grid
        for (r, c), value in assignment.items():
            self.solution[r][c] = value

        print(f"Solution found at depth {self.goal_depth}")
        print(f"Total nodes generated: {self.nodes_generated}")
        return True

    def write_output(self, output_file):
        """Write solution to output file"""
        with open(output_file, 'w') as f:
            # Write depth and nodes generated
            f.write(f"{self.goal_depth}\n")
            f.write(f"{self.nodes_generated}\n")

            # Write solution grid
            for row in self.solution:
                f.write(" ".join(map(str, row)) + "\n")

        print(f"Output written to {output_file}")

    def print_solution(self):
        """Print the solution grid in readable format"""
        print("\n=== SOLUTION ===")
        for i, row in enumerate(self.solution):
            if i % 3 == 0 and i != 0:
                print()
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    print(" ", end="")
                print(val, end=" ")
            print()
        print()


def main():
    """Main function to run the solver"""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python sudoku_mine.py <input_file> <output_file>")
        print("\nExample:")
        print("  python sudoku_mine.py Input1-new.txt Output1.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Reading puzzle from: {input_file}")
    solver = SudokuMineSolver(input_file)

    if solver.solve():
        solver.print_solution()
        solver.write_output(output_file)
        print(f"✓ Solution successfully written to: {output_file}")
    else:
        print("✗ Failed to find solution")


if __name__ == "__main__":
    main()