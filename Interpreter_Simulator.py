import re


class Token:
    """
    Represents a lexical token in the input.

    Attributes:
        type (str): The type of the token (e.g., 'NUMBER', 'OPERATOR').
        value (str or int): The value of the token (e.g., '5', '+').
    """

    def __init__(self, type, value):
        """
        Initializes a Token with a specified type and value.

        Args:
            type (str): The type of the token.
            value (str or int): The value of the token.
        """
        self.type = type
        self.value = value


class Lexer:
    """
    Performs lexical analysis, converting an input string into tokens.

    Attributes:
        text (str): The input string to be tokenized.
        pos (int): The current position in the input string.
    """

    def __init__(self, text):
        """
        Initializes the Lexer with the input text.

        Args:
            text (str): The input string to be tokenized.
        """
        self.text = text
        self.pos = 0

    def tokenize(self):
        """
        Tokenizes the input text into a list of tokens.

        Returns:
            list: A list of Token objects.
        """
        tokens = []
        while self.pos < len(self.text):
            if self.text[self.pos].isspace():
                self.pos += 1
                continue
            elif self.text[self.pos].isdigit():
                tokens.append(self.get_number())
            elif self.text[self.pos].isalpha():
                tokens.append(self.get_identifier())
            elif self.text[self.pos] in "+-*/()=<>":
                tokens.append(Token("OPERATOR", self.text[self.pos]))
                self.pos += 1
            else:
                raise Exception(f"Unknown symbol: {self.text[self.pos]}")
        return tokens

    def get_number(self):
        """
        Extracts a number token from the input text.

        Returns:
            Token: A Token object representing a number.
        """
        num = ""
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            num += self.text[self.pos]
            self.pos += 1
        return Token("NUMBER", int(num))

    def get_identifier(self):
        """
        Extracts an identifier or keyword token from the input text.

        Returns:
            Token: A Token object representing an identifier or keyword.
        """
        id = ""
        while self.pos < len(self.text) and self.text[self.pos].isalnum():
            id += self.text[self.pos]
            self.pos += 1
        keywords = ["if", "else", "while", "def"]
        if id in keywords:
            return Token("KEYWORD", id)
        return Token("IDENTIFIER", id)


##########################################


class ASTNode:
    """Base class for all nodes in the Abstract Syntax Tree (AST)."""
    pass


class BinaryOpNode(ASTNode):
    """
    Represents a binary operation node in the AST.

    Attributes:
        left (ASTNode): The left operand of the operation.
        op (str): The operator (e.g., '+', '-', '*', '/').
        right (ASTNode): The right operand of the operation.
    """

    def __init__(self, left, op, right):
        """
        Initializes a BinaryOpNode with the given left operand, operator, and right operand.

        Args:
            left (ASTNode): The left operand.
            op (str): The operator.
            right (ASTNode): The right operand.
        """
        self.left = left
        self.op = op
        self.right = right


class NumberNode(ASTNode):
    """
    Represents a number node in the AST.

    Attributes:
        value (int): The numeric value of the node.
    """

    def __init__(self, value):
        """
        Initializes a NumberNode with a given value.

        Args:
            value (int): The numeric value.
        """
        self.value = value


class VariableNode(ASTNode):
    """
    Represents a variable node in the AST.

    Attributes:
        name (str): The name of the variable.
    """

    def __init__(self, name):
        """
        Initializes a VariableNode with a given variable name.

        Args:
            name (str): The name of the variable.
        """
        self.name = name


class AssignmentNode(ASTNode):
    """
    Represents an assignment operation node in the AST.

    Attributes:
        name (str): The name of the variable to assign a value to.
        value (ASTNode): The value to be assigned.
    """

    def __init__(self, name, value):
        """
        Initializes an AssignmentNode with the given variable name and value.

        Args:
            name (str): The name of the variable.
            value (ASTNode): The value to be assigned.
        """
        self.name = name
        self.value = value


class IfNode(ASTNode):
    """
    Represents an if-else conditional node in the AST.

    Attributes:
        condition (ASTNode): The condition to evaluate.
        if_body (ASTNode): The statement(s) to execute if the condition is true.
        else_body (ASTNode, optional): The statement(s) to execute if the condition is false.
    """

    def __init__(self, condition, if_body, else_body=None):
        """
        Initializes an IfNode with a condition, if body, and optional else body.

        Args:
            condition (ASTNode): The condition to evaluate.
            if_body (ASTNode): The statement(s) to execute if true.
            else_body (ASTNode, optional): The statement(s) to execute if false.
        """
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body


class WhileNode(ASTNode):
    """
    Represents a while loop node in the AST.

    Attributes:
        condition (ASTNode): The loop condition to evaluate.
        body (ASTNode): The statement(s) to execute while the condition is true.
    """

    def __init__(self, condition, body):
        """
        Initializes a WhileNode with a condition and body.

        Args:
            condition (ASTNode): The loop condition.
            body (ASTNode): The statement(s) to execute while the condition is true.
        """
        self.condition = condition
        self.body = body


class Parser:
    """
    Parses a list of tokens into an Abstract Syntax Tree (AST).

    Attributes:
        tokens (list): The list of tokens to parse.
        pos (int): The current position in the list of tokens.
    """

    def __init__(self, tokens):
        """
        Initializes the Parser with a list of tokens.

        Args:
            tokens (list): The list of tokens to parse.
        """
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        """
        Parses the tokens into an AST.

        Returns:
            ASTNode: The root node of the parsed AST.
        """
        return self.statement()

    def statement(self):
        """
        Parses a statement, which could be a control structure or an expression.

        Returns:
            ASTNode: The parsed statement node.
        """
        if self.pos >= len(self.tokens):
            return None
        if self.current_token().type == "KEYWORD":
            if self.current_token().value == "if":
                return self.if_statement()
            elif self.current_token().value == "while":
                return self.while_statement()
        elif (self.current_token().type == "IDENTIFIER" and self.peek_next_token() and
              self.peek_next_token().type == "OPERATOR" and self.peek_next_token().value == "="):
            return self.assignment()
        else:
            return self.expression()

    def if_statement(self):
        """
        Parses an if-else statement.

        Returns:
            IfNode: The parsed if-else node.
        """
        self.consume("KEYWORD", "if")
        condition = self.expression()
        if_body = self.statement()
        else_body = None
        if (self.pos < len(self.tokens) and self.current_token().type == "KEYWORD" and
                self.current_token().value == "else"):
            self.consume("KEYWORD", "else")
            else_body = self.statement()
        return IfNode(condition, if_body, else_body)

    def while_statement(self):
        """
        Parses a while loop statement.

        Returns:
            WhileNode: The parsed while loop node.
        """
        self.consume("KEYWORD", "while")
        condition = self.expression()
        body = self.statement()
        return WhileNode(condition, body)

    def assignment(self):
        """
        Parses an assignment statement.

        Returns:
            AssignmentNode: The parsed assignment node.
        """
        name = self.consume("IDENTIFIER").value
        self.consume("OPERATOR", "=")
        value = self.expression()
        return AssignmentNode(name, value)

    def expression(self):
        """
        Parses an expression, starting with addition and subtraction.

        Returns:
            ASTNode: The parsed expression node.
        """
        return self.addition()

    def addition(self):
        """
        Parses an addition or subtraction operation.

        Returns:
            ASTNode: The parsed addition or subtraction node.
        """
        node = self.multiplication()
        while (self.pos < len(self.tokens) and self.current_token().type == "OPERATOR" and
               self.current_token().value in ("+", "-")):
            op = self.consume("OPERATOR").value
            right = self.multiplication()
            node = BinaryOpNode(node, op, right)
        return node

    def multiplication(self):
        """
        Parses a multiplication or division operation.

        Returns:
            ASTNode: The parsed multiplication or division node.
        """
        node = self.primary()
        while (self.pos < len(self.tokens) and self.current_token().type == "OPERATOR" and
               self.current_token().value in ("*", "/")):
            op = self.consume("OPERATOR").value
            right = self.primary()
            node = BinaryOpNode(node, op, right)
        return node

    def primary(self):
        """
        Parses a primary expression, which could be a number or an identifier.

        Returns:
            ASTNode: The parsed primary expression node.
        """
        if self.current_token().type == "NUMBER":
            return NumberNode(self.consume("NUMBER").value)
        elif self.current_token().type == "IDENTIFIER":
            return VariableNode(self.consume("IDENTIFIER").value)
        else:
            raise Exception("Number or identifier expected")

    def current_token(self):
        """
        Returns the current token.

        Returns:
            Token: The current token.
        """
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def peek_next_token(self):
        """
        Peeks at the next token without consuming it.

        Returns:
            Token: The next token, or None if at the end.
        """
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def consume(self, expected_type, expected_value=None):
        """
        Consumes the current token if it matches the expected type and value.

        Args:
            expected_type (str): The expected token type.
            expected_value (str, optional): The expected token value.

        Returns:
            Token: The consumed token.
        """
        if self.pos >= len(self.tokens):
            raise Exception("Unexpected end of input")
        if self.current_token().type != expected_type:
            raise Exception(f"Expected token of type {expected_type}, received {self.current_token().type}")
        if expected_value and self.current_token().value != expected_value:
            raise Exception(f"Expected value {expected_value}, received {self.current_token().value}")
        token = self.current_token()
        self.pos += 1
        return token


#######################################


class Interpreter:
    """
    Interprets the Abstract Syntax Tree (AST) to execute the code.

    Attributes:
        variables (dict): A dictionary that stores variable values.
    """

    def __init__(self):
        """
        Initializes the Interpreter with an empty variables' dictionary.
        """
        self.variables = {}

    def interpret(self, node):
        """
        Interprets the AST node and executes the corresponding action.
        Args:
            node (ASTNode): The AST node to interpret.
        Returns:
            int: The result of the interpretation.
        """
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, VariableNode):
            return self.variables.get(node.name, 0)
        elif isinstance(node, BinaryOpNode):
            left = self.interpret(node.left)
            right = self.interpret(node.right)
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                if right == 0:
                    raise Exception("Division by zero")
                return left / right
        elif isinstance(node, AssignmentNode):
            value = self.interpret(node.value)
            self.variables[node.name] = value
            return value
        elif isinstance(node, IfNode):
            if self.interpret(node.condition):
                return self.interpret(node.if_body)
            elif node.else_body:
                return self.interpret(node.else_body)
        elif isinstance(node, WhileNode):
            result = None
            while self.interpret(node.condition):
                result = self.interpret(node.body)
            return result
        else:
            raise Exception(f"Unknown node type: {type(node)}")


######################################


def run_test(code):
    print(f"Testing code: {code}")
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    print("AST:", ast)
    interpreter = Interpreter()
    result = interpreter.interpret(ast)
    print("Result:", result)
    return result


# Tests
run_test("2 + 3 * 4")
run_test("x = 5\ny = 3\nx + y")
run_test("x = 10\nif x > 5\n    x * 2\nelse\n    x / 2")
run_test("x = 0\nwhile x < 5\n    x = x + 1\nx")
