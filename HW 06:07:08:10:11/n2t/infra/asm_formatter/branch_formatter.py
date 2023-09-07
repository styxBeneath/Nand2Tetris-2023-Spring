from typing import Dict

from n2t.infra.asm_formatter.constants import (
    FILENAME_KEY,
    FUNCTION_NAME_KEY,
    INSTRUCTION_KEY,
)


class BranchFormatter:
    def __init__(self, args: Dict[str, str]) -> None:
        self.command_args = args[INSTRUCTION_KEY].split(" ")
        self.filename = args[FILENAME_KEY]
        self.function_name = args[FUNCTION_NAME_KEY]

    def translate_to_asm(self) -> str:
        asm_formatter_per_branch = {
            "goto": self.__format_goto,
            "if-goto": self.__format_if_goto,
            "label": self.__format_label,
        }

        return asm_formatter_per_branch[self.command_args[0]]()

    def __format_goto(self) -> str:
        return self.GOTO_TO_ASM.format(
            function=self.function_name, label=self.command_args[1]
        )

    def __format_if_goto(self) -> str:
        return self.IF_GOTO_TO_ASM.format(
            function=self.function_name, label=self.command_args[1]
        )

    def __format_label(self) -> str:
        return self.LABEL_TO_ASM.format(
            function=self.function_name, label=self.command_args[1]
        )

    GOTO_TO_ASM = "@{function}${label}\n" "0;JMP\n"

    IF_GOTO_TO_ASM = "@SP\n" "AM=M-1\n" "D=M\n" "@{function}${label}\n" "D;JNE\n"

    LABEL_TO_ASM = "({function}${label})\n"
