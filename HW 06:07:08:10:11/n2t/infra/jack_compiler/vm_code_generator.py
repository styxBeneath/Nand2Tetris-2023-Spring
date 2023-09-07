var_types_to_segments = {"field": "this"}

symbol_to_alu_command = {
    "+": "add",
    "-": "sub",
    "~": "not",
    "|": "or",
    "&": "and",
    "&gt": "gt",
    "@lt": "lt",
    ">": "gt",
    "<": "lt",
    "=": "eq",
    "*": "call Math.multiply 2",
    "/": "call Math.divide 2",
    "@amp": "amp",
}


class VMCodeGenerator:
    def __init__(self, out_file_name: str):
        self.file = open(out_file_name, "w")

    def close_file(self) -> None:
        self.file.close()

    def generate_push(self, segment: str, index: int) -> None:
        self.file.write(f"push {var_types_to_segments.get(segment, segment)} {index}\n")

    def generate_pop(self, segment: str, index: int) -> None:
        self.file.write(f"pop {var_types_to_segments.get(segment, segment)} {index}\n")

    def generate_label(self, label: str, index: int) -> None:
        self.file.write(f"label {label}{index}\n")

    def generate_goto(self, label: str, index: int) -> None:
        self.file.write(f"goto {label}{index}\n")

    def generate_if_goto(self, label: str, index: int) -> None:
        self.file.write(f"if-goto {label}{index}\n")

    def generate_string(self, value: str) -> None:
        self.generate_push("constant", len(value))
        self.generate_call("String.new", 1)

        for ch in value:
            self.generate_push("constant", ord(ch))
            self.generate_call("String.appendChar", 2)

    def generate_keyword(self, keyword: str) -> None:
        if keyword == "true":
            self.generate_push("constant", 0)
            self.generate_alu("not")
        elif keyword in ("false", "null"):
            self.generate_push("constant", 0)
        elif keyword == "this":
            self.generate_push("pointer", 0)

    def generate_alu(self, symbol: str) -> None:
        self.file.write(f"{symbol_to_alu_command.get(symbol, symbol)}\n")

    def generate_function(
        self, class_name: str, function_name: str, nargs: int
    ) -> None:
        self.file.write(f"function {class_name}.{function_name} {nargs}\n")

    def generate_call(self, name: str, nargs: int) -> None:
        self.file.write(f"call {name} {nargs}\n")

    def generate_return(self) -> None:
        self.file.write("return\n")

    def generate_method_header(self) -> None:
        self.generate_push("argument", 0)
        self.generate_pop("pointer", 0)

    def generate_constructor_header(self, size: int) -> None:
        self.generate_push("constant", size)
        self.generate_call("Memory.alloc", 1)
        self.generate_pop("pointer", 0)
