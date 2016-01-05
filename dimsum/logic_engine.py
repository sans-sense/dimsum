"""
parse, run and refine rules, what people see of the logic engine
"""
from pygments.lexers import PrologLexer
from pygments.token import Token
from pydispatch import dispatcher

from dimsum.logic_base import Rule
from dimsum.logic_base import Operators

RULE_EXECUTED_SIGNAL = 'rule_executed'

class LogicEngine(object):
    """
    what the outside world will ever see
    """
    def __init__(self):
        self.parser = PrologParser()
        self.runner = ConfidenceBasedRunner()
        self.refiner = HistoryBasedRefiner()
        self.rules = {}

    def prime(self, rules_file="./examples/poa_rules.pl"):
        self.rules = self.parser.parse(open(rules_file).read())

    def run(self, data):
        return self.runner.run(self.rules, data)

class PrologParser(object):
    def __init__(self):
        self.pro_lexer = PrologLexer()

    def parse(self, text):
        """
        for the given text parse into rules
        """
        rules = {}
        tokens = self.__parse_into_tokens(text)
        rules_unrefined = self.__get_rules_with_lazy_body(tokens)
        # make the first pass adding rules to dictionary
        self.__merge_duplicates(rules, rules_unrefined)
        return rules

    def __parse_into_tokens(self, text):
        return list(self.pro_lexer.get_tokens(text))

    def __merge_duplicates(self, rule_dictionary, rules_with_possible_duplicates):
        for rule in rules_with_possible_duplicates:
            rulename = rule.rule_name()
            if rulename in rule_dictionary:
                rule_dictionary[rulename].add_to_root_operation(rule.body.root_operation)
            else:
                rule_dictionary[rulename] = rule
        return rule_dictionary


    def __get_rules_with_lazy_body(self, tokens):
        rules = []
        curr_rule = []
        for token in tokens:
            if not token[0] is Token.Text:
                curr_rule.append(token)

                # if we reached end of rule, create a rule from prev values
                if token[0] is Token.Punctuation and token[1] == '.':
                    if curr_rule:
                        rules.append(Rule(curr_rule))
                        curr_rule = list()

        return rules

# exec(open("ruleProcessor.py").read(), globals()); from dimsum.logic_engine import PrologParser;
#parser = PrologParser(); rules = parser.parseRules(open("./examples/poa_rules.pl").read())


class ConfidenceBasedRunner(object):
    def __init__(self):
        self.run_id = 0
        self.ops_impl = {
            Operators.And: self.and_op,
            Operators.Or : self.or_op,
            Operators.InvokeFunction: self.invoke_function_op
        }
        self.rule_dictionary = {}
        self.data = {}
        self.func_dict = {}
        self.results = {}


    def run(self, rules, data):
        self.run_id += 1
        self.data.update(data)
        self.rule_dictionary = rules
        for key in rules:
            rule = rules[key]
            result = rule.apply(self)
            dispatcher.send(RULE_EXECUTED_SIGNAL, dispatcher.Any, result, rule, self.run_id)
            self.register_result(rule, result)
        return self

    def and_op(self, operands):
        result = True
        for operation in operands:
            result = result and operation.apply(self)
        return result

    def or_op(self, operands):
        result = False
        for operation in operands:
            result = result or operation.apply(self)
        return result


    def invoke_function_op(self, operands):
        func_name = operands[0]
        tail_operands = operands[1:]
        # check if func_name is a rule
        if len(operands) == 3:
            rule_name = "{0} {1} {2}".format(operands[1], operands[0], operands[2])
            rule = self.rule_dictionary.get(rule_name, None)
            if rule:
                return rule.apply(self)

        func = self.func_dict.get(func_name, lambda _: True)
        real_operands = self.__lookup_in_data(tail_operands)
        return func(real_operands)


    def register_function(self, name, func):
        self.func_dict[name] = func

    def invoke(self, operator, operands):
        operation = self.ops_impl.get(operator, lambda: True)
        return operation(operands)

    def register_result(self, rule, result):
        self.results[rule.rule_name()] = result

    def __lookup_in_data(self, var_names):
        operands = {}
        for var_name in var_names:
            operands[var_name] = self.data[var_name]
            if not operands[var_name]:
                operands[var_name] = var_name
        return operands



class HistoryBasedRefiner(object):

    def __init__(self):
        self.run_results = []
        dispatcher.connect(self.capture, signal=RULE_EXECUTED_SIGNAL, sender=dispatcher.Any)

    def capture(self, result, rule, run_id):
        self.run_results.append(History(run_id, rule.rule_name(), result))


class History(object):
    def __init__(self, run_id, rule_name, result):
        self.run_id = run_id
        self.rule_name = rule_name
        self.result = result
