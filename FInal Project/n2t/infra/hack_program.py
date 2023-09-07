from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from n2t.core import HackSimulator
from n2t.core.assembler import Assembler


@dataclass
class HackProgram:
    file_path: str
    cycles: int

    @classmethod
    def load_from(cls, file_or_directory_name: str, num_cycles: int) \
            -> HackProgram:
        return cls(file_or_directory_name, num_cycles)

    def load(self) -> Iterable[str]:
        with Path(self.file_path).open("r", newline="") as file:
            yield from (line.strip() for line in file if line)

    def simulate(self) -> None:
        instructions = (
            self.load()
            if self.file_path.endswith(".hack")
            else Assembler.load_from(self.file_path).assemble()
        )

        output = HackSimulator().simulate(instructions, self.cycles)

        json_path = (
            self.file_path[:-4]
            if self.file_path.endswith(".hack")
            else self.file_path[:-3]
        ) + "json"
        json_output = {"RAM": output}
        with open(json_path, "w") as json_file:
            json.dump(json_output, json_file, indent=2)
