from __future__ import annotations

from ctypes import c_short
from dataclasses import dataclass
from typing import Any, Dict, Iterable

SIZE = 32768


@dataclass
class HackSimulator:
    address_reg: int = 0
    data_reg: int = 0
    ram = [0] * SIZE
    used = [False] * SIZE

    @classmethod
    def create(cls) -> HackSimulator:
        return cls()

    def simulate(self, instructions: Iterable[str], cycles: int) \
            -> dict[int, int]:
        instr = list(iter(instructions))
        index = 0
        while cycles > 0:
            cycles = cycles - 1
            if index >= len(instr):
                break
            index = self.perform_instruction(instr[index], index)
        return self.ram_state_payroll()

    def perform_instruction(self, instruction: str, index: int) -> Any:
        if instruction.startswith("0"):
            self.perform_a_instruction(instruction[1:])
            return index + 1
        return self.perform_c_instruction(instruction[3:], index)

    def perform_a_instruction(self, value: str) -> None:
        self.address_reg = int(value, 2)
        return

    def perform_c_instruction(self, instruction: str, index: int) -> Any:
        comp: int = c_short(self.get_computation(instruction[:7])).value
        jump = instruction[10:]
        destination = instruction[7:10]
        if destination != "000":
            self.save_value(destination, comp)
        if jump == "000":
            return index + 1
        return self.perform_jump(jump, comp, index)

    def get_computation(self, comp: str) -> Any:
        a = comp[0]
        comp = comp[1:]

        cases = {
            "101010": 0,
            "111111": 1,
            "111010": -1,
            "001100": self.data_reg,
            "110000":
                self.address_reg if a == "0" else self.ram[self.address_reg],
            "001101": ~self.data_reg,
            "110001": ~self.address_reg if a == "0" else
                ~(self.ram[self.address_reg]),
            "001111": -self.data_reg,
            "110011": -self.address_reg if a == "0" else
                -self.ram[self.address_reg],
            "011111": self.data_reg + 1,
            "110111": self.address_reg + 1
            if a == "0"
            else self.ram[self.address_reg] + 1,
            "001110": self.data_reg - 1,
            "110010": self.address_reg - 1
            if a == "0"
            else self.ram[self.address_reg] - 1,
            "000010": self.data_reg
            + (self.address_reg if a == "0" else self.ram[self.address_reg]),
            "010011": self.data_reg
            - (self.address_reg if a == "0" else self.ram[self.address_reg]),
            "000111": (self.address_reg - self.data_reg)
            if a == "0"
            else (self.ram[self.address_reg] - self.data_reg),
            "000000": (self.address_reg & self.data_reg)
            if a == "0"
            else (self.ram[self.address_reg] & self.data_reg),
        }

        default_case = (
            self.address_reg | self.data_reg
            if a == "0"
            else self.ram[self.address_reg] | self.data_reg
        )
        return cases.get(comp, default_case)

    def save_value(self, destination: str, value: Any) -> None:
        if destination == "001":
            self.ram[self.address_reg] = value
            self.used[self.address_reg] = True
        elif destination == "010":
            self.data_reg = value
        elif destination == "011":
            self.ram[self.address_reg] = value
            self.used[self.address_reg] = True
            self.data_reg = value
        elif destination == "100":
            self.address_reg = value
        elif destination == "101":
            self.ram[self.address_reg] = value
            self.used[self.address_reg] = True
            self.address_reg = value
        elif destination == "110":
            self.address_reg = value
            self.data_reg = value
        else:
            self.data_reg = value
            self.ram[self.address_reg] = value
            self.used[self.address_reg] = True
            self.address_reg = value

    def perform_jump(self, jump_type: str, comp: Any, current_index: int) \
            -> Any:
        ans: Any = self.address_reg
        jump_conditions = {
            "001": comp > 0,
            "010": comp == 0,
            "011": comp >= 0,
            "100": comp < 0,
            "101": comp != 0,
            "110": comp <= 0,
        }

        if jump_type in jump_conditions:
            if jump_conditions[jump_type]:
                return self.address_reg
            else:
                return current_index + 1

        return ans

    def ram_state_payroll(self) -> Dict[int, int]:
        output: Dict[int, int] = {}
        for i in range(SIZE):
            if self.used[i]:
                output[i] = self.ram[i]
        return output
