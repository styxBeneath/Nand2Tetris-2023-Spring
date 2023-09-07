from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, TextIO

from n2t.infra.asm_formatter.alu_formatter import AluFormatter
from n2t.infra.asm_formatter.branch_formatter import BranchFormatter
from n2t.infra.asm_formatter.constants import (
    ASM_EXTENSION,
    FILENAME_KEY,
    FUNCTION_NAME_KEY,
    INSTRUCTION_INDEX_KEY,
    INSTRUCTION_KEY,
    MAIN_FILENAME,
    VM_EXTENSION,
)
from n2t.infra.asm_formatter.function_formatter import FunctionFormatter
from n2t.infra.asm_formatter.pop_formatter import PopFormatter
from n2t.infra.asm_formatter.push_formatter import PushFormatter

BOOTSTRAP_SP = "@256\n" "D=A\n" "@SP\n" "M=D\n"

BOOTSTRAP_SYS_INIT = "call Sys.init 0"


def get_asm_filename(file_or_directory_name: str) -> str:
    path = os.path.splitext(file_or_directory_name.rstrip("/"))[0]

    if os.path.isfile(path + VM_EXTENSION):
        without_ext = os.path.splitext(path)[0]
    else:
        without_ext = os.path.join(path, os.path.basename(path))

    return without_ext + ASM_EXTENSION


def contain_sys(filenames: List[str]) -> bool:
    for i, filename in enumerate(filenames):
        if MAIN_FILENAME in filename:
            return True
    return False


def clean_vm_code(instructions: List[str]) -> List[str]:
    cleaned_lines = []
    for line in instructions:
        if "//" in line:
            line = line.split("//", 1)[0]
        cleaned_line = line.strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    return cleaned_lines


def parse_folder(folder_name: str, asm_file: TextIO) -> List[str]:
    filenames = [
        os.path.join(folder_name, filename)
        for filename in os.listdir(folder_name)
        if filename.endswith(VM_EXTENSION)
    ]

    if contain_sys(filenames):
        asm_file.write(BOOTSTRAP_SP)
        parse_vm_file([BOOTSTRAP_SYS_INIT], asm_file, "")

    return filenames


def vm_instr_to_asm(args: Dict[str, Any]) -> str:
    command_type: str = args[INSTRUCTION_KEY].split(" ")[0]
    if command_type == "push":
        return PushFormatter(args).translate_to_asm()
    elif command_type == "pop":
        return PopFormatter(args).translate_to_asm()
    elif command_type in ("label", "goto", "if-goto"):
        return BranchFormatter(args).translate_to_asm()
    elif command_type in ("function", "call", "return"):
        return FunctionFormatter(args).translate_to_asm()
    else:
        return AluFormatter(args).translate_to_asm()


def parse_vm_file(vm_instructions: List[str], file: TextIO, filename: str) -> None:
    current_function: str = ""
    for i, vm_instruction in enumerate(vm_instructions):
        args = {
            INSTRUCTION_KEY: vm_instruction,
            FILENAME_KEY: filename,
            FUNCTION_NAME_KEY: current_function,
            INSTRUCTION_INDEX_KEY: i,
        }
        asm_command: str = vm_instr_to_asm(args)
        file.write(asm_command)


def parse_vm_files(file_or_directory_name: str, asm_filename: str) -> None:
    asm_file = open(asm_filename, "w")
    filenames = [file_or_directory_name]

    if not os.path.isfile(file_or_directory_name):
        filenames = parse_folder(file_or_directory_name, asm_file)

    for filename in filenames:
        with open(filename, "r") as file:
            instructions = clean_vm_code(file.read().split("\n"))
            parse_vm_file(
                instructions, asm_file, os.path.basename(filename).split(".")[0]
            )

    asm_file.close()


@dataclass
class VmProgram:
    file_or_directory_name: str

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> VmProgram:
        return cls(file_or_directory_name)

    def translate(self) -> None:
        asm_filename = get_asm_filename(self.file_or_directory_name)
        parse_vm_files(self.file_or_directory_name, asm_filename)
