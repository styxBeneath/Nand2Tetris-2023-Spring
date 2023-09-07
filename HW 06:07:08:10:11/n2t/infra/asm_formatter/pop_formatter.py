from typing import Dict

from n2t.infra.asm_formatter.constants import (
    A_REG,
    ARGUMENT_REG,
    FILENAME_KEY,
    INSTRUCTION_KEY,
    LOCAL_REG,
    M_REG,
    POINTER_REG,
    TEMP_REG,
    THAT_REG,
    THIS_REG,
)


class PopFormatter:
    def __init__(self, args: Dict[str, str]) -> None:
        instruction_parts = args[INSTRUCTION_KEY].split(" ")
        self.register_type = instruction_parts[1]
        self.address = instruction_parts[2]
        self.filename = args[FILENAME_KEY]

    def translate_to_asm(self) -> str:
        asm_formatter_per_segment = {
            "local": self.__format_local,
            "argument": self.__format_argument,
            "this": self.__format_this,
            "that": self.__format_that,
            "static": self.__format_static,
            "pointer": self.__format_pointer,
            "temp": self.__format_temp,
        }

        return asm_formatter_per_segment[self.register_type]()

    def __format_local(self) -> str:
        return self.POP_OTHERS_TO_ASM.format(
            addr=self.address, register=LOCAL_REG, a_or_m_register=M_REG
        )

    def __format_argument(self) -> str:
        return self.POP_OTHERS_TO_ASM.format(
            addr=self.address, register=ARGUMENT_REG, a_or_m_register=M_REG
        )

    def __format_this(self) -> str:
        return self.POP_OTHERS_TO_ASM.format(
            addr=self.address, register=THIS_REG, a_or_m_register=M_REG
        )

    def __format_that(self) -> str:
        return self.POP_OTHERS_TO_ASM.format(
            addr=self.address, register=THAT_REG, a_or_m_register=M_REG
        )

    def __format_temp(self) -> str:
        return self.POP_OTHERS_TO_ASM.format(
            addr=self.address, register=TEMP_REG, a_or_m_register=A_REG
        )

    def __format_pointer(self) -> str:
        return self.POP_OTHERS_TO_ASM.format(
            addr=self.address, register=POINTER_REG, a_or_m_register=A_REG
        )

    def __format_static(self) -> str:
        return self.POP_STATIC_TO_ASM.format(addr=self.filename + "." + self.address)

    POP_OTHERS_TO_ASM = (
        "@{addr}\n"
        "D=A\n"
        "@{register}\n"
        "D=D+{a_or_m_register}\n"
        "@R13\n"
        "M=D\n"
        "@SP\n"
        "AM=M-1\n"
        "D=M\n"
        "@R13\n"
        "A=M\n"
        "M=D\n"
    )

    POP_STATIC_TO_ASM = "@SP\n" "AM=M-1\n" "D=M\n" "@{addr}\n" "M=D\n"
