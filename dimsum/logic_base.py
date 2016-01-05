"""
base classes for logic like rules
"""
from pygments.token import Token
from enum import Enum

class Rule(object):
    """
    Basic building block for logic
    """
    ast = list()
    head = None
    body = None

    def __init__(self, token_list):
        self.token_list = token_list
        if len(token_list) > 3:
            parts = list(self.__partition(token_list))
            self.head = self.__create_head(parts[0])
            if len(parts) > 1:
                self.body = self.__create_body(parts[1])
                self.confidence = 0.5
            else:
                self.confidence = 1


    def __repr__(self):
        return self.rule_name()

    def is_fact(self):
        return not self.body

    def rule_name(self):
        rulename = ""
        if self.head.variable:
            rulename = self.head.variable + " "
        if self.head.func_name and self.head.const:
            rulename += self.head.func_name + " " + self.head.const

        return rulename

    def add_to_root_operation(self, operand):
        self.body.add_sibling(operand)
        return self

    def apply(self, exec_ctx):
        """
        Returns true or false
        """
        if self.is_fact():
            return True
        else:
            return self.body.apply(exec_ctx)

    def __partition(self, tokens):
        """Yield head and body"""
        j = 0
        i = 0
        for val in tokens:
            if val[0] is Token.Punctuation and val[1] == ':-':
                j = i
            i = i + 1

        if not j == 0:
            return [tokens[0:j], tokens[j:]]
        else:
            return [tokens]

    def __create_head(self, tokens):
        var = None
        func = None
        const = None
        for token in tokens:
            if token[0] is Token.Name.Function:
                func = token[1]
            elif token[0] is Token.Name.Variable:
                var = token[1]
            elif token[0] is Token.Literal.String.Atom:
                const = token[1]

        return Head(var, func, const)

    def __create_body(self, tokens):
        return Body(tokens)

class Head(object):
    """
    Internal to a rule
    """
    def __init__(self, variable, func_name, const):
        self.variable = variable
        self.func_name = func_name
        self.const = const


    def __repr__(self):
        return self.func_name



class Body(object):
    """
    Internal to a rule
    """
    def __init__(self, tokens):
        self.tokens = tokens
        # ideally we should not initialize to And
        self.root_operation = Operation(Operators.And)
        self.operation = self.__create_operation(tokens)

    def __create_operation(self, tokens):
        try:
            curr_position = 0
            nesting_level = 0
            for token in tokens:
                token_type = token[0]
                if token_type is Token.Name.Function:
                    curr_operator = Operation(Operators.InvokeFunction)
                    curr_operator.add_operand(token[1])
                elif token_type is Token.Punctuation and token[1] == '(':
                    nesting_level += 1
                elif token_type is Token.Punctuation and token[1] == ')':
                    nesting_level -= 1
                elif token_type is Token.Name.Variable or token_type is Token.Literal.String.Atom:
                    curr_operator.add_operand(token[1])
                elif token_type is Token.Punctuation and token[1] == ',' and nesting_level == 0:
                    self.root_operation.add_operand(curr_operator)
                elif token_type is Token.Punctuation and token[1] == '.':
                    self.root_operation.add_operand(curr_operator)

            curr_position += 1
        except AttributeError as err:
            print str(tokens) + " prob at " + str(tokens[curr_position]) + "error: {0}".format(err.message)

    def add_sibling(self, operation):
        new_root_op = Operation(Operators.Or)
        new_root_op.add_operand(self.root_operation)
        new_root_op.add_operand(operation)
        self.root_operation = new_root_op
        return self

    def apply(self, exec_ctx):
        return self.root_operation.apply(exec_ctx)



class Operation(object):
    def __init__(self, operator):
        self.operator = operator
        self.operands = []

    def add_operand(self, operand):
        self.operands.append(operand)

    def __repr__(self):
        return str(self.operator) + " on " + str(self.operands)

    def apply(self, exec_ctx):
        return exec_ctx.invoke(self.operator, self.operands)


class Operators(Enum):
    And = 1
    Or = 2
    InvokeFunction = 3
    Not = 4
