from __future__ import annotations

import os
from dataclasses import dataclass
from os.path import isdir, isfile
from typing import List

from n2t.infra.jack_compiler.compilation_engine import CompilationEngine
from n2t.infra.jack_compiler.constants import (
    JACK_FILE_EXT,
    PARSER_FILE_EXT,
    TOKENIZER_FILE_EXT,
    VM_FILE_EXT,
)
from n2t.infra.jack_compiler.tokenizer import Tokenizer


def analyze_file(file_name: str) -> None:
    tokenizer_file_name = file_name.rstrip(JACK_FILE_EXT) + TOKENIZER_FILE_EXT
    parser_file_name = file_name.rstrip(JACK_FILE_EXT) + PARSER_FILE_EXT
    compiler_file_name = file_name.rstrip(JACK_FILE_EXT) + VM_FILE_EXT
    tokenizer = Tokenizer(file_name, tokenizer_file_name)
    tokenizer.write_in_file()

    tokenizer.reset()
    parser = CompilationEngine(tokenizer, parser_file_name, compiler_file_name)
    parser.write_in_file()


def get_all_files(directory_name: str) -> List[str]:
    return [
        os.path.join(directory_name, file_name)
        for file_name in os.listdir(directory_name)
        if file_name.endswith(JACK_FILE_EXT)
    ]


@dataclass
class JackProgram:
    file_or_directory_name: str

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> JackProgram:
        cls.file_or_directory_name = file_or_directory_name
        return cls(cls.file_or_directory_name)

    def compile(self) -> None:
        if isfile(self.file_or_directory_name):
            files = [self.file_or_directory_name]
        elif isdir(self.file_or_directory_name):
            files = get_all_files(self.file_or_directory_name)
        else:
            raise FileNotFoundError()
        for file in files:
            analyze_file(file)
