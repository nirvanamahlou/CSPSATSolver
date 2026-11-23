from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QFileDialog, QLabel, QMessageBox, QTextEdit, QApplication
)
import time
from csp import CSP
from cnf import CNF

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.solve_button = None
        self.select_file_button = None
        self.lcv_checkbox = None
        self.mcv_checkbox = None
        self.mrv_checkbox = None
        self.bb_checkbox = None  
        self.quit_button = None
        self.selected_file = None
        self.setWindowTitle("SAT Solver using CSP")
        self.setGeometry(200, 200, 500, 300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.cnf_display = QTextEdit()
        self.cnf_display.setPlaceholderText("CNF formula will appear here after selecting a file")
        self.cnf_display.setReadOnly(True)

       
        self.mcv_checkbox = QCheckBox("Use MCV (Most Constraining Variable)")
        self.mrv_checkbox = QCheckBox("Use MRV (Minimum Remaining Value)")
        self.lcv_checkbox = QCheckBox("Use LCV (Least Constraining Value)")

        
        self.bb_checkbox = QCheckBox("Use Branch and Bound")

        self.select_file_button = QPushButton("Select CNF File")
        self.select_file_button.clicked.connect(self.open_file_dialog)

        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.handle_solve_button)
        self.solve_button.setEnabled(False)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(QApplication.instance().quit)

        options_layout = QHBoxLayout()
        options_layout.addWidget(self.mcv_checkbox)
        options_layout.addWidget(self.mrv_checkbox)
        options_layout.addWidget(self.lcv_checkbox)

        
        options_layout.addWidget(self.bb_checkbox)

        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Choose Test File:"))
        file_layout.addWidget(self.select_file_button)

        layout.addWidget(QLabel("SAT CNF Formula:"))
        layout.addWidget(self.cnf_display)
        layout.addLayout(options_layout)
        layout.addLayout(file_layout)
        layout.addWidget(self.solve_button)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CNF File", "", "Text Files (*.txt)")

        if file_path:
            self.selected_file = file_path
            self.solve_button.setEnabled(True)
            with open(file_path, 'r') as file:
                cnf_formula = file.read()
                self.cnf_display.setText(cnf_formula)
        else:
            self.solve_button.setEnabled(False)

    def handle_solve_button(self):
        use_mcv = self.mcv_checkbox.isChecked()
        use_mrv = self.mrv_checkbox.isChecked()
        use_lcv = self.lcv_checkbox.isChecked()
        use_bb  = self.bb_checkbox.isChecked()  
        file_path = self.selected_file

        
        if use_mrv and use_mcv:
            QMessageBox.warning(
                self, "Error", "MRV and MCV cannot be used synchronously.")
            return

        self.solve_cnf_csp(use_mcv, use_mrv, use_lcv, use_bb, file_path)

    def read_test_case(self, filename):
        hard_clauses = []
        soft_clauses = []
        variables = []
        with open(filename, 'r') as f:
            lines = f.readlines()
            num_vars, num_hard_clauses, num_soft_clauses = map(
                int, lines[0].split())
            lines.pop(0)
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                line_vars = line.split()
                if line_vars[0] == 'SOFT_CLAUSE':
                    line_vars.pop(0)
                    soft_clauses.append(line_vars)
                else:
                    hard_clauses.append(line_vars)

            for clause in hard_clauses:
                for variable in clause:
                    negation = variable[1:] if '~' in variable else ('~' + variable)
                    variables.append(variable)
                    variables.append(negation)

            for _clause in soft_clauses:
                clause = _clause[:-1]
                for variable in clause:
                    negation = variable[1:] if '~' in variable else ('~' + variable)
                    variables.append(variable)
                    variables.append(negation)

            variables = set(variables)
       
        return (variables, hard_clauses, soft_clauses)

    def solve_cnf_csp(self, use_mcv, use_mrv, use_lcv, use_bb, file_path):
        if not file_path:
            QMessageBox.warning(self, "Error", "No file selected!")
            return

        variables, hard_clauses, soft_clauses = self.read_test_case(file_path)
        if variables is None:
            QMessageBox.warning(self, "Error", "Wrong format !")
            return

        cnf = CNF(variables, hard_clauses, soft_clauses)
        csp = CSP(cnf, use_mcv, use_mrv, use_lcv)

        start_time = time.time()
        if use_bb:
           
            result, answer = csp.branch_and_bound_solve()
        else:
            
            result, answer = csp.solve()

        end_time = time.time()

        if result:
            result = {key: value for (key, value)
                      in result.items() if not key.startswith('~')}
            sorted_result = "\n".join(
                f"{var} = {value}"
                for var, value in sorted(result.items(),
                                         key=lambda x: int(x[0][1:].replace('~','') or "0"))
            )
            formatted_result = (
                f"Maximum weight: {answer}\n"
                f"Execution time: {(end_time - start_time):.4f}s\n"
                f"MCV: {use_mcv}, MRV: {use_mrv}, LCV: {use_lcv}, Branch&Bound: {use_bb}\n\n"
                f"Assignments:\n{sorted_result}"
            )
        else:
            formatted_result = "No solution found."

        QMessageBox.information(self, "Result", formatted_result)
