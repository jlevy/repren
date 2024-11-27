import subprocess
from rich import print as rprint


def _run(cmd: list[str]) -> int:
    rprint(f"[bold green]❯ {' '.join(cmd)}[/bold green]")
    errcount = 0
    try:
        subprocess.run(cmd, text=True, check=True)
    except subprocess.CalledProcessError as e:
        rprint(f"[bold red]Error: {e}[/bold red]")
        errcount = 1
    rprint()

    return errcount


PATHS = ["repren"]


def main():
    rprint()

    errcount = 0
    paths = PATHS
    doc_paths = ["README.md"]
    errcount += _run(["codespell", "--write-changes", *paths, *doc_paths])
    errcount += _run(["usort", "format", *paths])
    errcount += _run(["ruff", "check", "--fix", *paths])
    errcount += _run(["black", *paths])
    errcount += _run(["mypy", *paths])  # TODO: Enable.

    rprint()

    if errcount != 0:
        rprint(f"[bold red]✗ Lint failed with {errcount} errors.[/bold red]")
    else:
        rprint("[bold green]✔️ Lint passed![/bold green]")
    rprint()

    return errcount


if __name__ == "__main__":
    exit(main())
