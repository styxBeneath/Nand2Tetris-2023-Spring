from typing import Dict

from n2t.infra.asm_formatter.constants import (
    ADD,
    AND,
    EQ,
    GT,
    INSTRUCTION_INDEX_KEY,
    INSTRUCTION_KEY,
    LT,
    NEG,
    NOT,
    OR,
    SUB,
)


class AluFormatter:
    def __init__(self, args: Dict[str, str]) -> None:
        self.instruction: str = args[INSTRUCTION_KEY]
        self.label_idx = args[INSTRUCTION_INDEX_KEY]

    def translate_to_asm(self) -> str:
        asm_formatter_per_alu_type = {
            "add": self.__format_add,
            "sub": self.__format_sub,
            "neg": self.__format_neg,
            "eq": self.__format_eq,
            "lt": self.__format_lt,
            "gt": self.__format_gt,
            "and": self.__format_and,
            "or": self.__format_or,
            "not": self.__format_not,
        }

        return asm_formatter_per_alu_type[self.instruction]()

    def __format_add(self) -> str:
        return self.BINARY_OPERATION_TO_ASM.format(binary_op=ADD)

    def __format_sub(self) -> str:
        return self.BINARY_OPERATION_TO_ASM.format(binary_op=SUB)

    def __format_and(self) -> str:
        return self.BINARY_OPERATION_TO_ASM.format(binary_op=AND)

    def __format_or(self) -> str:
        return self.BINARY_OPERATION_TO_ASM.format(binary_op=OR)

    def __format_neg(self) -> str:
        return self.UNARY_OPERATION_TO_ASM.format(unary_op=NEG)

    def __format_not(self) -> str:
        return self.UNARY_OPERATION_TO_ASM.format(unary_op=NOT)

    def __format_eq(self) -> str:
        return self.COMPARISON_TO_ASM.format(branch=EQ, index=self.label_idx)

    def __format_lt(self) -> str:
        return self.COMPARISON_TO_ASM.format(branch=LT, index=self.label_idx)

    def __format_gt(self) -> str:
        return self.COMPARISON_TO_ASM.format(branch=GT, index=self.label_idx)

    BINARY_OPERATION_TO_ASM = "@SP\n" "AM=M-1\n" "D=M\n" "A=A-1\n" "M=M{binary_op}D\n"

    UNARY_OPERATION_TO_ASM = "@SP\n" "A=M-1\n" "M={unary_op}M\n"

    COMPARISON_TO_ASM = (
        "@SP\n"
        "AM=M-1\n"
        "D=M\n"
        "A=A-1\n"
        "D=M-D\n"
        "M=-1\n"
        "@LABEL{index}\n"
        "D;{branch}\n"
        "@SP\n"
        "A=M-1\n"
        "M=0\n"
        "(LABEL{index})\n"
    )
