# ui.py
# وحدة المسؤولة فقط عن عرض النتائج والتنقل البصري
from rich.console import Console
from rich.panel import Panel

console = Console()

def display_results(results):
    """
    عرض نتائج البحث كبطاقات عمودية منفصلة باللغة الإنجليزية فقط.
    """
    console.clear()
    
    if not results:
        console.print("[bold red]No matches found.[/bold red]")
        input("\nPress Enter to continue...")
        return

    console.print("[bold blue]=== SEARCH RESULTS ===[/bold blue]")
    console.print("[dim]" + "─" * (console.width - 4) + "[/dim]\n")

    for idx, group in enumerate(results, 1):
        primary = group.get("primary_name", "Unknown Group")
        models = group.get("models", [])
        total = len(models)

        # بناء محتوى البطاقة العمودي
        card_text = f"[bold cyan]GROUP {idx} | {primary.upper()}[/bold cyan]\n"
        card_text += f"[dim]Total Compatible Models: {total}[/dim]\n"
        card_text += "[yellow]Models:[/yellow]\n"
        
        for model in models:
            card_text += f"  • {model}\n"

        # عرض البطاقة في إطار مستطيل بعرض الشاشة
        console.print(Panel(card_text.strip(), border_style="blue", expand=True))
        console.print()  # مسافة فاصلة بين البطاقات

    console.print("[dim]" + "─" * (console.width - 4) + "[/dim]")
    console.print("[bold]Enter group number to manage, or 0 to go back.[/bold]")

def print_header(title):
    """طباعة عنوان رئيسي نظيف"""
    console.clear()
    console.print(Panel(f"[bold white]{title}[/bold white]", border_style="green", expand=True))
    console.print()