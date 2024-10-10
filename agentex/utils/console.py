from typing import List, Optional

from rich import box
from rich.table import Table
from rich.console import Console

console = Console()


def print_section(name: str, contents: List[str], subtitle: Optional[str] = None):
    console.print()
    table = Table(box=box.SQUARE, caption=subtitle, show_header=False, expand=True)
    table.title = name
    table.add_column(name, style="dim", width=12)
    table.add_row(*contents)
    console.print(table)
