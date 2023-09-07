from typer import Typer, echo

from n2t.infra import HackProgram

cli = Typer(name="Nand 2 Tetris Software", no_args_is_help=True, add_completion=False)


@cli.command("execute", no_args_is_help=True)
def run_simulator(hack_file: str, cycles: int = 10000) -> None:
    HackProgram.load_from(hack_file, cycles).simulate()
    echo("Done!")


@cli.command("run", no_args_is_help=True)
def run() -> None:
    pass
