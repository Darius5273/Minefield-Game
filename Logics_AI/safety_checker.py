from nltk.inference.prover9 import convert_to_prover9
from nltk.sem.logic import Expression, LogicParser
from nltk.inference import Prover9



class MineSafetyChecker:
    def __init__(self, grid_size,step):
        self.parser = LogicParser()
        self.rules = []
        self.grid_size = grid_size
        self.prover = Prover9()

        self.replacements = {
            "∀": "all ",
            "∃": "exists ",
            "¬": "-",
            "∧": "&",
            "∨": "|",
            "⇒": "->",
            "↔": "<->",
            "≠": "!=",
        }

        self.domain = {(x, y) for x in range(1, grid_size + 1) for y in range(1, grid_size + 1)}

        match step:
            case 0:
                self.generate_sum_rules()
            case 1:
                self.generate_comp_rules()
                self.generate_equality_rules()
            case 2:
                self.generate_comp_rules()
                self.generate_equality_rules()
        self.add_rule("-mine(1,1)")

    def _preprocess_formula(self, formula):
        for symbol, replacement in self.replacements.items():
            formula = formula.replace(symbol, replacement)
        return formula

    def _convert_formula_to_fol(self,formula):
        replacements = {"+":"sum",
                        "< = ":"sm",
                        }
        for symbol in replacements.keys():
            pos = formula.find(symbol)
            while pos != -1:
                if formula[pos] == "+":
                    formula = formula[:pos - 1] + replacements[symbol] + "(" + formula[pos - 1] + "," + formula[
                    pos + 1] + ")" + formula[pos + 2:]
                else:
                    formula = formula[:pos-1] + replacements[symbol] + "(" + formula[pos + -1] + "," + formula[
                        pos + 4] + ")" + formula[pos + 5:]
                pos = formula.find(symbol)

        return formula

    def ensure_parentheses_after_quantifiers(self,formula):
        quantifiers = ["all", "exists"]
        i = 0
        while i < len(formula):
            for quantifier in quantifiers:
                if formula[i:i + len(quantifier)] == quantifier:
                    j = i + len(quantifier)
                    while j < len(formula) and formula[j] == " ":
                        j += 1
                    if j < len(formula) and formula[j].isalpha() and len(formula[j:j + 1]) == 1:
                        j += 1
                        while j < len(formula) and formula[j] == " ":
                            j += 1
                        if j >= len(formula) or formula[j] != "(":
                            formula = formula[:j] + "(" + formula[j:] + ")"
                            i = j + 1
            i += 1
        return formula

    def add_rule(self, rule_str):

        preprocessed_rule = self._preprocess_formula(rule_str)
        parsed_rule = self.parser.parse(preprocessed_rule)
        prover9_rule = convert_to_prover9(parsed_rule)
        correct_formula = self.ensure_parentheses_after_quantifiers(prover9_rule)
        new_rule = self._convert_formula_to_fol(correct_formula)
        self.rules.append(new_rule)

    def check_safety(self, x, y):

        conclusion_str = f"-mine({x},{y})"
        preprocessed_conclusion = self._preprocess_formula(conclusion_str)
        conclusion = self.parser.parse(preprocessed_conclusion)

        premises = " & ".join(str(rule) for rule in self.rules)

        if self.prover.prove(conclusion, assumptions=[Expression.fromstring(premises)]):
            return "safe"
        else:
            return "unsafe"

    def show_rules(self):
        for rule in self.rules:
            print(rule)

    def generate_sum_rules(self):
        for x in range(1, self.grid_size + 1):
            for y in range(x, self.grid_size + 1):
                equation = f"sum({x},{y}) = {x + y}"
                self.rules.append(equation)
        commutativity_rule = "all x all y (sum(x, y) = sum(y,x))"
        self.rules.append(commutativity_rule)

    def generate_comp_rules(self):
        for x in range(1, self.grid_size + 1):
            for y in range(x, self.grid_size + 1):
                equation = f"sm({x},{y})"
                self.rules.append(equation)
    def generate_equality_rules(self):
        for x in range(1, self.grid_size + 1):
            for y in range(x+1, self.grid_size + 1):
                equation = f"({x}!={y})"
                self.rules.append(equation)


