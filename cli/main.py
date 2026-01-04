"""
Velo CLI - FastAPI Module Generator
"""

import typer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

app = typer.Typer()
console = Console()


def get_template_env() -> Environment:
    """Get Jinja2 environment for templates"""
    template_dir = Path(__file__).parent / "templates"
    return Environment(loader=FileSystemLoader(template_dir))


def render_template(template_name: str, context: dict) -> str:
    """Render a template with given context"""
    env = get_template_env()
    template = env.get_template(template_name)
    return template.render(**context)


def create_file_from_template(
    template_name: str, output_path: Path, context: dict, overwrite: bool = False
) -> None:
    """Create a file from template"""
    if output_path.exists() and not overwrite:
        console.print(
            f"[yellow]⚠️  File {output_path} already exists. Use --overwrite to replace.[/yellow]"
        )
        return

    content = render_template(template_name, context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    console.print(f"[green]✓[/green] Created {output_path}")


@app.command()
def generate(
    name: str = typer.Argument(
        ..., help="Name of the module to generate (e.g., 'product', 'user', 'category')"
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files"
    ),
):
    """
    Generate a new FastAPI module with CRUD operations.

    This command creates a complete module structure including:
    - Beanie document model
    - Pydantic schemas (Create, Update, Response)
    - Use case with business logic
    - FastAPI router with REST endpoints

    Example: velo product
    """
    # Convert name to snake_case and PascalCase
    snake_case = name.lower().replace("-", "_")
    pascal_case = "".join(word.capitalize() for word in snake_case.split("_"))

    context = {
        "feature_name": snake_case,
        "pascal_case": pascal_case,
        "module_name": snake_case,
    }

    # Base module directory
    module_dir = Path("apiapp/modules") / snake_case
    module_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_file = module_dir / "__init__.py"
    init_file.write_text("")
    console.print(f"[green]✓[/green] Created {init_file}")

    # Create model.py
    create_file_from_template(
        "model.py.j2", module_dir / "model.py", context, overwrite
    )

    # Create schemas.py
    create_file_from_template(
        "schemas.py.j2", module_dir / "schemas.py", context, overwrite
    )

    # Create use_case.py
    create_file_from_template(
        "use_case.py.j2", module_dir / "use_case.py", context, overwrite
    )

    # Create router.py
    create_file_from_template(
        "router.py.j2", module_dir / "router.py", context, overwrite
    )

    # Success message
    success_text = Text(
        f"Module '{snake_case}' generated successfully!", style="bold green"
    )
    console.print(Panel(success_text, title="✅ Success", border_style="green"))

    console.print(f"[blue]📁[/blue] Location: {module_dir}")

    console.print("\n[bold cyan]Next steps:[/bold cyan]")
    console.print(
        f"1. Add the router to your main app: [code]from apiapp.modules.{snake_case}.router import router[/code]"
    )
    console.print(
        "2. Include it in your FastAPI app: [code]app.include_router(router)[/code]"
    )


if __name__ == "__main__":
    app()
