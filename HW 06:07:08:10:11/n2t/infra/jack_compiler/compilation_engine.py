from n2t.infra.jack_compiler.constants import (
    ELSE_LABEL_BEGIN,
    IF_ELSE_LABEL_END,
    IF_LABEL_BEGIN,
    WHILE_LABEL_BEGIN,
    WHILE_LABEL_END,
    XML_LINE_TAB,
)
from n2t.infra.jack_compiler.symbols_table import SymbolsTable
from n2t.infra.jack_compiler.tokenizer import StatementType, Tokenizer, TokenType
from n2t.infra.jack_compiler.vm_code_generator import VMCodeGenerator


class CompilationEngine:
    def __init__(self, tokenizer: Tokenizer, xml_file_name: str, vm_file_name: str):
        self.class_name = ""
        self.return_type = ""
        self.tokenizer = tokenizer
        self.out_file_name = xml_file_name
        self.symbols_table = SymbolsTable()
        self.vm_generator = VMCodeGenerator(vm_file_name)
        self.xml_file = open(xml_file_name, "w")

    def write_line(self, line: str, tab_count: int) -> None:
        self.xml_file.write(f"{XML_LINE_TAB * tab_count}{line}\n")

    def write_in_file(self) -> None:
        self.compile_class()
        self.vm_generator.close_file()
        self.xml_file.close()

    def write_and_move_next(self, line: str, tab_count: int) -> None:
        self.write_line(line, tab_count)
        self.tokenizer.advance()

    def compile_class(self) -> None:
        self.write_line("<class>", 0)

        self.write_and_move_next(self.tokenizer.keyword_xml(), 1)
        self.class_name = self.tokenizer.get_current_token()
        self.write_and_move_next(self.tokenizer.identifier_xml(), 1)
        self.write_and_move_next(self.tokenizer.symbol_xml(), 1)

        while self.tokenizer.is_class_variable():
            self.compile_class_var_declaration(1)

        while self.tokenizer.is_callable():
            self.compile_subroutine_dec(1)

        self.write_and_move_next(self.tokenizer.symbol_xml(), 1)
        self.write_line("</class>", 0)

    def compile_class_var_declaration(self, tab_count: int) -> None:
        self.write_line("<classVarDec>", tab_count)

        kind = self.tokenizer.get_current_token()

        self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        self.compile_variable(kind, tab_count + 1)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_line("</classVarDec>", tab_count)

    def compile_variable(self, kind: str, tab_count: int) -> int:
        var_type = self.tokenizer.get_current_token()
        self.compile_type(tab_count)

        self.symbols_table.define_symbol(
            self.tokenizer.get_current_token(), var_type, kind
        )
        self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count)

        num_vars = 1
        while self.tokenizer.is_comma():
            num_vars += 1
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
            self.symbols_table.define_symbol(
                self.tokenizer.get_current_token(), var_type, kind
            )
            self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count)

        return num_vars

    def compile_type(self, tab_count: int) -> str:
        symbol_type = self.tokenizer.get_current_token()
        if self.tokenizer.token_type() == TokenType.KEYWORD:
            self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count)
        else:
            self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count)
        return symbol_type

    def compile_subroutine_dec(self, tab_count: int) -> None:
        self.write_line("<subroutineDec>", tab_count)

        self.symbols_table.start_subroutine()

        function_type = self.tokenizer.get_current_token()
        if function_type == "method":
            self.symbols_table.define_symbol("this", self.class_name, "argument")

        self.write_and_move_next(
            self.tokenizer.keyword_xml(), tab_count + 1
        )  # constructor, function, method
        self.return_type = self.tokenizer.get_current_token()

        if self.tokenizer.is_void():
            self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        else:
            self.compile_type(tab_count + 1)

        function_name = self.tokenizer.get_current_token()

        self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)  # name
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.compile_parameter_list(tab_count + 1)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.compile_subroutine_body(function_name, function_type, tab_count + 1)
        self.write_line("</subroutineDec>", tab_count)

    def compile_parameter_list(self, tab_count: int) -> None:
        self.write_line("<parameterList>", tab_count)

        while not self.tokenizer.is_close_parentheses():
            symbol_type = self.compile_type(tab_count + 1)
            name = self.tokenizer.get_current_token()
            self.symbols_table.define_symbol(name, symbol_type, "argument")
            self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)
            if self.tokenizer.is_comma():
                self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_line("</parameterList>", tab_count)

    def compile_subroutine_body(
        self, function_name: str, function_type: str, tab_count: int
    ) -> None:
        self.write_line("<subroutineBody>", tab_count)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        num_vars = 0
        while self.tokenizer.is_variable():
            num_vars += self.compile_var_dec(tab_count + 1)

        self.vm_generator.generate_function(self.class_name, function_name, num_vars)

        if function_type == "constructor":
            self.vm_generator.generate_constructor_header(
                self.symbols_table.get_num_fields()
            )
        elif function_type == "method":
            self.vm_generator.generate_method_header()

        self.compile_statements(tab_count + 1)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.write_line("</subroutineBody>", tab_count)

    def compile_var_dec(self, tab_count: int) -> int:
        self.write_line("<varDec>", tab_count)

        self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        num_vars = self.compile_variable("local", tab_count + 1)

        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.write_line("</varDec>", tab_count)

        return num_vars

    def compile_statements(self, tab_count: int) -> None:
        self.write_line("<statements>", tab_count)

        compilers = {
            StatementType.LET: self.compile_let,
            StatementType.IF: self.compile_if,
            StatementType.WHILE: self.compile_while,
            StatementType.DO: self.compile_do,
            StatementType.RETURN: self.compile_return,
        }

        while self.tokenizer.statement() != StatementType.NOT_STATEMENT:
            compilers[self.tokenizer.statement()](tab_count + 1)

        self.write_line("</statements>", tab_count)

    def compile_let(self, tab_count: int) -> None:
        self.write_line("<letStatement>", tab_count)

        self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)

        index = self.symbols_table.get_index(self.tokenizer.get_current_token())
        kind = self.symbols_table.get_kind(self.tokenizer.get_current_token())

        self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)

        is_open_brackets = self.tokenizer.is_open_brackets()
        if is_open_brackets:
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_expression(tab_count + 1)

            self.vm_generator.generate_push(kind, index)
            self.vm_generator.generate_alu("+")

            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.compile_expression(tab_count + 1)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        if is_open_brackets:
            self.vm_generator.generate_pop("temp", 0)
            self.vm_generator.generate_pop("pointer", 1)
            self.vm_generator.generate_push("temp", 0)
            self.vm_generator.generate_pop("that", 0)
        else:
            self.vm_generator.generate_pop("this" if kind == "field" else kind, index)

        self.write_line("</letStatement>", tab_count)

    def compile_expression(self, tab_count: int) -> None:
        self.write_line("<expression>", tab_count)
        self.compile_term(tab_count + 1)

        while self.tokenizer.is_binary_operation():
            op = self.tokenizer.get_current_token()
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_term(tab_count + 1)
            self.vm_generator.generate_alu(op)
        self.write_line("</expression>", tab_count)

    def compile_array_term(self, current_token: str, tab_count: int) -> None:
        kind = self.symbols_table.get_kind(current_token)
        index = self.symbols_table.get_index(current_token)
        self.vm_generator.generate_push(kind, index)

        self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_expression(tab_count)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_generator.generate_alu("+")
        self.vm_generator.generate_pop("pointer", 1)
        self.vm_generator.generate_push("that", 0)

    def compile_term(self, tab_count: int) -> None:
        self.write_line("<term>", tab_count)

        token_type = self.tokenizer.token_type()
        current_token = self.tokenizer.get_current_token()

        if token_type == TokenType.INT_CONST:
            self.vm_generator.generate_push("constant", self.tokenizer.int_val())
            self.write_and_move_next(self.tokenizer.int_xml(), tab_count + 1)
        elif token_type == TokenType.STRING_CONST:
            self.vm_generator.generate_string(self.tokenizer.string_val())
            self.write_and_move_next(self.tokenizer.string_xml(), tab_count + 1)
        elif token_type == TokenType.KEYWORD:
            self.vm_generator.generate_keyword(current_token)
            self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        elif self.tokenizer.is_open_parentheses():
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_expression(tab_count + 1)
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        elif self.tokenizer.is_unary_operation():
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_term(tab_count + 1)
            self.vm_generator.generate_alu("neg" if current_token == "-" else "not")
        elif self.tokenizer.is_next_token_open_brackets():
            self.compile_array_term(current_token, tab_count + 1)
        elif self.tokenizer.is_next_token_dot_or_open_parentheses():
            self.compile_subroutine_call(tab_count + 1)
        else:
            kind = self.symbols_table.get_kind(current_token)
            index = self.symbols_table.get_index(current_token)
            self.vm_generator.generate_push(kind, index)

            self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count + 1)

        self.write_line("</term>", tab_count)

    def compile_subroutine_call(self, tab_count: int) -> None:
        count_args = 0
        object_name = self.tokenizer.get_current_token()

        self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count)

        if not self.tokenizer.is_open_parentheses():
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
            if self.symbols_table.contains_name(object_name):
                kind = self.symbols_table.get_kind(object_name)
                index = self.symbols_table.get_index(object_name)
                object_name = self.symbols_table.get_type(object_name)
                count_args = 1
                self.vm_generator.generate_push(kind, index)

            name = f"{object_name}.{self.tokenizer.get_current_token()}"

            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
            self.write_and_move_next(self.tokenizer.identifier_xml(), tab_count)

            count_args += self.compile_expression_list(tab_count)
        else:
            name = f"{self.class_name}.{object_name}"
            self.vm_generator.generate_push("pointer", 0)
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
            count_args += self.compile_expression_list(tab_count) + 1

        self.vm_generator.generate_call(name, count_args)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)

    def compile_if(self, tab_count: int) -> None:
        self.write_line("<ifStatement>", tab_count)

        label_index = self.symbols_table.next_if_index()

        self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count)

        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_expression(tab_count)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_generator.generate_if_goto(IF_LABEL_BEGIN, label_index)
        self.vm_generator.generate_goto(ELSE_LABEL_BEGIN, label_index)
        self.vm_generator.generate_label(IF_LABEL_BEGIN, label_index)

        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_statements(tab_count)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_generator.generate_goto(IF_ELSE_LABEL_END, label_index)
        self.vm_generator.generate_label(ELSE_LABEL_BEGIN, label_index)

        if self.tokenizer.is_else():
            self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
            self.compile_statements(tab_count + 1)
            self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.vm_generator.generate_label(IF_ELSE_LABEL_END, label_index)
        self.write_line("</ifStatement>", tab_count)

    def compile_while(self, tab_count: int) -> None:
        self.write_line("<whileStatement>", tab_count)

        label_index = self.symbols_table.next_while_index()
        self.vm_generator.generate_label(WHILE_LABEL_BEGIN, label_index)

        self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count)

        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_expression(tab_count)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_generator.generate_alu("not")
        self.vm_generator.generate_if_goto(WHILE_LABEL_END, label_index)

        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)
        self.compile_statements(tab_count)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count)

        self.vm_generator.generate_goto(WHILE_LABEL_BEGIN, label_index)
        self.vm_generator.generate_label(WHILE_LABEL_END, label_index)

        self.write_line("</whileStatement>", tab_count)

    def compile_do(self, tab_count: int) -> None:
        self.write_line("<doStatement>", tab_count)

        self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)
        self.compile_subroutine_call(tab_count + 1)
        self.vm_generator.generate_pop("temp", 0)
        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)

        self.write_line("</doStatement>", tab_count)

    def compile_return(self, tab_count: int) -> None:
        self.write_line("<returnStatement>", tab_count)
        self.write_and_move_next(self.tokenizer.keyword_xml(), tab_count + 1)

        if not self.tokenizer.is_semicolon():
            self.compile_expression(tab_count + 1)

        if self.return_type == "void":
            self.vm_generator.generate_push("constant", 0)
        self.vm_generator.generate_return()

        self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
        self.write_line("</returnStatement>", tab_count)

    def compile_expression_list(self, tab_count: int) -> int:
        self.write_line("<expressionList>", tab_count)
        count = 0

        if not self.tokenizer.is_close_parentheses():
            self.compile_expression(tab_count + 1)
            count += 1
            while self.tokenizer.is_comma():
                self.write_and_move_next(self.tokenizer.symbol_xml(), tab_count + 1)
                self.compile_expression(tab_count + 1)
                count += 1

        self.write_line("</expressionList>", tab_count)

        return count
