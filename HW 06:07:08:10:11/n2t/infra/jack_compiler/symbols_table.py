from collections import defaultdict
from typing import Dict, Tuple


class SymbolsTable:
    def __init__(self) -> None:
        self.if_label_idx = 0
        self.while_label_idx = 0
        self.class_table: Dict[str, Tuple[str, str, int]] = {}
        self.subroutine_table: Dict[str, Tuple[str, str, int]] = {}
        self.scope_index: Dict[str, int] = defaultdict(int)

    def start_subroutine(self) -> None:
        self.scope_index = defaultdict(int)
        self.subroutine_table = {}

    def define_symbol(self, name: str, symbol_type: str, kind: str) -> None:
        value = (symbol_type, kind, self.scope_index[kind])
        self.scope_index[kind] += 1

        if kind in {"static", "field"}:
            self.class_table[name] = value
        else:
            self.subroutine_table[name] = value

    def next_if_index(self) -> int:
        self.if_label_idx += 1
        return self.if_label_idx - 1

    def next_while_index(self) -> int:
        self.while_label_idx += 1
        return self.while_label_idx - 1

    def contains_name(self, name: str) -> bool:
        return name in self.class_table or name in self.subroutine_table

    def get_num_fields(self) -> int:
        return sum(1 for _, (_, kind, _) in self.class_table.items() if kind == "field")

    def get_type(self, name: str) -> str:
        if name in self.class_table:
            return self.class_table[name][0]
        else:
            return self.subroutine_table[name][0]

    def get_kind(self, name: str) -> str:
        if name in self.class_table:
            return self.class_table[name][1]
        else:
            return self.subroutine_table.get(name, ("", "", ""))[1]

    def get_index(self, name: str) -> int:
        if name in self.class_table:
            return self.class_table[name][2]
        else:
            return self.subroutine_table[name][2]
