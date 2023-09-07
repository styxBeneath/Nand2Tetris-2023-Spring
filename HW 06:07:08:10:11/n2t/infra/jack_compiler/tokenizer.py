import re
from enum import Enum
from re import findall
from typing import List, TextIO

from n2t.infra.jack_compiler.constants import DOUBLE_QUOTE

keywords = {
    "class",
    "constructor",
    "function",
    "method",
    "field",
    "static",
    "var",
    "int",
    "char",
    "boolean",
    "void",
    "true",
    "false",
    "null",
    "this",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return",
}

symbols = {
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    ".",
    ",",
    ";",
    "+",
    "-",
    "*",
    "/",
    "&",
    "|",
    "<",
    ">",
    "=",
    "~",
}

specific_symbols = {"<": "&lt;", ">": "&gt;", '"': "&quot;", "&": "&amp;"}


class StatementType(Enum):
    LET, IF, WHILE, DO, RETURN, NOT_STATEMENT = range(6)


class TokenType(Enum):
    KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST = range(5)


class KeywordType(Enum):
    (
        CLASS,
        CONSTRUCTOR,
        FUNCTION,
        METHOD,
        FIELD,
        STATIC,
        VAR,
        INT,
        CHAR,
        BOOLEAN,
        VOID,
        TRUE,
        FALSE,
        NULL,
        THIS,
        LET,
        DO,
        IF,
        ELSE,
        WHILE,
        RETURN,
    ) = range(len(keywords))


class Tokenizer:
    def __init__(self, file_name: str, out_file_name: str):
        self.file_name = file_name
        self.out_file_name = out_file_name
        self.file_str = self.parse_file()

        self.quotes = self.get_quote_indexes()
        self.tokens = self.generate_tokens()
        self.curr_token_index = 0

    def reset(self) -> None:
        self.curr_token_index = 0

    def parse_file(self) -> str:
        with open(self.file_name, "r") as jack_file:
            file_contents = jack_file.read()
            cleaned_contents = re.sub(
                r"(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)", "", file_contents
            )
            return cleaned_contents

    def get_quote_indexes(self) -> List[int]:
        res = [i for i, ch in enumerate(self.file_str) if ch == DOUBLE_QUOTE]
        assert len(res) % 2 == 0, "Syntax error, quotes are odd"

        return res

    def generate_tokens(self) -> List[str]:
        all_tokens = findall(r"\w+|[{}()<>.,;=~|&*/+\-\"\[\]]", self.file_str)

        res, i = [], -1
        for token in all_tokens:
            if token == DOUBLE_QUOTE:
                if i % 2 == 0:
                    res.append(
                        DOUBLE_QUOTE
                        + self.file_str[self.quotes[i] + 1: self.quotes[i + 1]]
                        + DOUBLE_QUOTE
                    )
                i += 1
            elif i % 2 == 1:
                res.append(token)

        return res

    def write_in_file(self) -> None:
        with open(self.out_file_name, "w") as file:
            writer_functions = {
                TokenType.KEYWORD: self.write_keyword,
                TokenType.SYMBOL: self.write_symbol,
                TokenType.IDENTIFIER: self.write_identifier,
                TokenType.INT_CONST: self.write_int_const,
                TokenType.STRING_CONST: self.write_string_const,
            }
            file.write("<tokens>\n")
            while self.has_more_tokens():
                writer_functions[self.token_type()](file)
                self.advance()
            file.write("</tokens>\n")

    def write_keyword(self, file: TextIO) -> None:
        file.write(self.keyword_xml() + "\n")

    def write_symbol(self, file: TextIO) -> None:
        file.write(self.symbol_xml() + "\n")

    def write_identifier(self, file: TextIO) -> None:
        file.write(self.identifier_xml() + "\n")

    def write_int_const(self, file: TextIO) -> None:
        file.write(self.int_xml() + "\n")

    def write_string_const(self, file: TextIO) -> None:
        file.write(self.string_xml() + "\n")

    def advance(self) -> None:
        self.curr_token_index += 1

    def has_more_tokens(self) -> bool:
        return self.curr_token_index < len(self.tokens)

    def token_type(self) -> TokenType:
        if self.tokens[self.curr_token_index][0] == DOUBLE_QUOTE:
            return TokenType.STRING_CONST
        elif self.tokens[self.curr_token_index] in keywords:
            return TokenType.KEYWORD
        elif self.tokens[self.curr_token_index] in symbols:
            return TokenType.SYMBOL
        elif self.tokens[self.curr_token_index].isdigit():
            return TokenType.INT_CONST
        else:
            return TokenType.IDENTIFIER

    def statement(self) -> StatementType:
        statement_dict = {
            KeywordType.LET: StatementType.LET,
            KeywordType.IF: StatementType.IF,
            KeywordType.WHILE: StatementType.WHILE,
            KeywordType.DO: StatementType.DO,
            KeywordType.RETURN: StatementType.RETURN,
        }

        if self.token_type() == TokenType.KEYWORD and self.keyword() in statement_dict:
            return statement_dict[self.keyword()]
        else:
            return StatementType.NOT_STATEMENT

    def keyword(self) -> KeywordType:
        return KeywordType[self.tokens[self.curr_token_index].upper()]

    def symbol(self) -> str:
        token = self.tokens[self.curr_token_index]
        return specific_symbols.get(token, token)

    def identifier(self) -> str:
        return self.tokens[self.curr_token_index]

    def int_val(self) -> int:
        return int(self.tokens[self.curr_token_index])

    def string_val(self) -> str:
        return self.tokens[self.curr_token_index][1:-1]

    def keyword_xml(self) -> str:
        return f"<keyword> {self.tokens[self.curr_token_index]} </keyword>"

    def symbol_xml(self) -> str:
        return f"<symbol> {self.symbol()} </symbol>"

    def identifier_xml(self) -> str:
        return f"<identifier> {self.identifier()} </identifier>"

    def string_xml(self) -> str:
        return f"<stringConstant> {self.string_val()} </stringConstant>"

    def int_xml(self) -> str:
        return f"<integerConstant> {self.int_val()} </integerConstant>"

    def is_open_parentheses(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() == "("
        )

    def is_close_parentheses(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() == ")"
        )

    def is_open_brackets(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() == "["
        )

    def is_next_token_open_brackets(self) -> bool:
        self.curr_token_index += 1
        res = (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() == "["
        )

        self.curr_token_index -= 1
        return res

    def is_next_token_dot_or_open_parentheses(self) -> bool:
        self.curr_token_index += 1
        res = (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() in ".("
        )

        self.curr_token_index -= 1
        return res

    def is_unary_operation(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() in "-~"
        )

    def is_binary_operation(self) -> bool:
        return (
            self.has_more_tokens() and self.tokens[self.curr_token_index] in "+-*/&|<>="
        )

    def is_semicolon(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() == ";"
        )

    def is_comma(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.SYMBOL
            and self.symbol() == ","
        )

    def is_else(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.KEYWORD
            and self.keyword() == KeywordType.ELSE
        )

    def is_variable(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.KEYWORD
            and self.keyword() == KeywordType.VAR
        )

    def is_class_variable(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.KEYWORD
            and self.keyword() in (KeywordType.STATIC, KeywordType.FIELD)
        )

    def is_void(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.KEYWORD
            and self.keyword() == KeywordType.VOID
        )

    def is_callable(self) -> bool:
        return (
            self.has_more_tokens()
            and self.token_type() == TokenType.KEYWORD
            and self.keyword()
            in (KeywordType.CONSTRUCTOR, KeywordType.FUNCTION, KeywordType.METHOD)
        )

    def get_current_token(self) -> str:
        return self.tokens[self.curr_token_index]

    def get_current_token_index(self) -> int:
        return self.curr_token_index

    def get_tokens(self) -> List[str]:
        return self.tokens
