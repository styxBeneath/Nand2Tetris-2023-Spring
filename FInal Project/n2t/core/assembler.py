from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

COMMON_SYMBOLS = {
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24567,
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
}

COMP_TO_BINARY = {
    "0": "101010",
    "1": "111111",
    "-1": "111010",
    "D": "001100",
    "A": "110000",
    "M": "110000",
    "!D": "001101",
    "!A": "110001",
    "!M": "110001",
    "-D": "0011111",
    "-A": "110011",
    "-M": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "M+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "M-1": "110010",
    "D+A": "000010",
    "D+M": "000010",
    "D-A": "010011",
    "D-M": "010011",
    "A-D": "000111",
    "M-D": "000111",
    "D&A": "000000",
    "D&M": "000000",
    "D|A": "010101",
    "D|M": "010101",
}

DEST_TO_BINARY = {
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

JUMP_TO_BINARY = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

VAR_START_INDEX = 16


def clean_comments(assembly: Iterable[str]) -> Iterable[str]:
    return (line.split("//")[0].strip() for line in assembly)


def clean_whitespaces(assembly: Iterable[str]) -> Iterable[str]:
    return filter(lambda s: s.strip() != "",
                  (s.replace(" ", "") for s in assembly))


def clean_assembly(assembly: Iterable[str]) -> Iterable[str]:
    assembly = clean_comments(assembly)
    assembly = clean_whitespaces(assembly)
    return assembly


def process_labels(assembly: Iterable[str], symbols: Dict[str, Any]) \
        -> Iterable[str]:
    label_count = 0
    assembly_without_labels = []

    for idx, command in enumerate(assembly):
        if command[0] == "(" and command[-1] == ")":
            label = command[1:-1]
            symbols[label] = idx - label_count
            label_count += 1
        else:
            assembly_without_labels.append(command)

    return assembly_without_labels


def get_symbols(assembly: Iterable[str]) \
        -> Tuple[Iterable[str], Dict[str, Any]]:
    symbols = COMMON_SYMBOLS.copy()
    assembly = process_labels(assembly, symbols)
    return assembly, symbols


def process_a_instruction(
    command: str, var_index: int, symbols: Dict[str, str]
) -> Tuple[str, int]:
    val: Any
    if command in symbols:
        val = symbols[command]
    elif command.isdigit():
        val = int(command)
    else:
        val = var_index
        symbols[command] = val
        var_index += 1

    return "{0:016b}".format(val), var_index


def process_c_instruction(command: str) -> str:
    dest_comp, jump = command.split(";") if ";" in command else (command, "")
    dest, comp = dest_comp.split("=") if "=" in dest_comp else ("", dest_comp)

    dest_bits = DEST_TO_BINARY.get(dest, "000")
    comp_bits = COMP_TO_BINARY.get(comp, "000")
    jump_bits = JUMP_TO_BINARY.get(jump, "000")

    addr_bit = "1" if "M" in comp else "0"

    binary_instruction = "111" + addr_bit + comp_bits + dest_bits + jump_bits

    return binary_instruction


def command_to_binary(
    command: str, var_index: int, symbols: Dict[str, str]
) -> Tuple[str, int]:
    if command[0] == "@":
        return process_a_instruction(command[1:], var_index, symbols)
    else:
        return process_c_instruction(command), var_index


def convert_to_binary(
    assembly: Iterable[str], symbols: Dict[str, str]
) -> Iterable[str]:
    var_index = VAR_START_INDEX
    result = []
    for command in assembly:
        binary, var_index = command_to_binary(command, var_index, symbols)
        result.append(binary)
    return result


def file_to_iterable(file_path: str) -> Iterable[str]:
    with Path(file_path).open("r", newline="") as file:
        yield from (line.strip() for line in file if line)


@dataclass
class Assembler:
    file_or_directory_name: str

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> Assembler:
        return cls(file_or_directory_name)

    def assemble(self) -> Iterable[str]:
        assembly = file_to_iterable(self.file_or_directory_name)
        assembly = clean_assembly(assembly)
        assembly, symbols = get_symbols(assembly)
        result = convert_to_binary(assembly, symbols)
        return result
