from typing import Dict

from n2t.infra.asm_formatter.constants import (
    ARGUMENT_REG,
    FILENAME_KEY,
    FUNCTION_NAME_KEY,
    INSTRUCTION_INDEX_KEY,
    INSTRUCTION_KEY,
    LOCAL_REG,
    THAT_REG,
    THIS_REG,
)


class FunctionFormatter:
    def __init__(self, args: Dict[str, str]) -> None:
        self.command_args = args[INSTRUCTION_KEY].split(" ")
        self.filename = args[FILENAME_KEY]
        self.command_index = args[INSTRUCTION_INDEX_KEY]

        if len(self.command_args) > 1:
            args[FUNCTION_NAME_KEY] = self.command_args[1]

    def translate_to_asm(self) -> str:
        branch_type_to_asm_handler = {
            "function": self.__format_function,
            "call": self.__format_call,
            "return": self.__format_return,
        }

        return branch_type_to_asm_handler[self.command_args[0]]()

    def __format_function(self) -> str:
        return self.LABEL_TO_ASM.format(
            function=self.command_args[1]
        ) + self.PUSH_SPACE_FOR_VARIABLE * int(self.command_args[2])

    def __format_call(self) -> str:
        return (
            self.PUSH_SPACE_FOR_RETURN.format(
                function=self.command_args[1], label=self.command_index
            )
            + self.PUSH_SPACE_FOR_SEGMENT.format(arg=LOCAL_REG)
            + self.PUSH_SPACE_FOR_SEGMENT.format(arg=ARGUMENT_REG)
            + self.PUSH_SPACE_FOR_SEGMENT.format(arg=THIS_REG)
            + self.PUSH_SPACE_FOR_SEGMENT.format(arg=THAT_REG)
            + self.MOVE_SP_TO_LCL.format(args_count=self.command_args[2])
            + self.GO_TO_FUNCTION.format(function=self.command_args[1])
            + self.RETURN_VALUE_TO_ASM.format(
                function=self.command_args[1], label=self.command_index
            )
        )

    def __format_return(self) -> str:
        return (
            self.RESOLVE_RETURN_ADDRESS
            + self.POP_SPACE_FOR_ARGUMENT
            + self.RESOLVE_SPACE_FOR_SEGMENT.format(register=THAT_REG)
            + self.RESOLVE_SPACE_FOR_SEGMENT.format(register=THIS_REG)
            + self.RESOLVE_SPACE_FOR_SEGMENT.format(register=ARGUMENT_REG)
            + self.RESOLVE_SPACE_FOR_SEGMENT.format(register=LOCAL_REG)
            + self.GO_TO_RETURN_ADDRESS
        )

    LABEL_TO_ASM = "({function})\n"

    RETURN_VALUE_TO_ASM = "({function}$ret.{label})\n"

    PUSH_SPACE_FOR_VARIABLE = "@SP\n" "M=M+1\n" "A=M-1\n" "M=0\n"

    PUSH_SPACE_FOR_RETURN = (
        "@{function}$ret.{label}\n" "D=A\n" "@SP\n" "AM=M+1\n" "A=A-1\n" "M=D\n"
    )

    PUSH_SPACE_FOR_SEGMENT = "@{arg}\n" "D=M\n" "@SP\n" "AM=M+1\n" "A=A-1\n" "M=D\n"

    MOVE_SP_TO_LCL = (
        "@{args_count}\n"
        "D=A\n"
        "@5\n"
        "D=D+A\n"
        "@SP\n"
        "D=M-D\n"
        "@ARG\n"
        "M=D\n"
        "@SP\n"
        "D=M\n"
        "@LCL\n"
        "M=D\n"
    )

    GO_TO_FUNCTION = "@{function}\n" "0;JMP\n"

    RESOLVE_RETURN_ADDRESS = (
        "@LCL\n"
        "D=M\n"
        "@R13\n"
        "M=D\n"
        "@5\n"
        "D=A\n"
        "@R13\n"
        "A=M-D\n"
        "D=M\n"
        "@R14\n"
        "M=D\n"
    )

    RESOLVE_SPACE_FOR_SEGMENT = "@R13\n" "AM=M-1\n" "D=M\n" "@{register}\n" "M=D\n"

    POP_SPACE_FOR_ARGUMENT = (
        "@SP\n"
        "A=M-1\n"
        "D=M\n"
        "@ARG\n"
        "A=M\n"
        "M=D\n"
        "@ARG\n"
        "D=M+1\n"
        "@SP\n"
        "M=D\n"
    )

    GO_TO_RETURN_ADDRESS = "@R14\n" "A=M\n" "0;JMP\n"
