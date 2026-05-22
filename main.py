import sys, os

# --- حل مشكلة المسارات في Pydroid 3 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from models_db import load_data, save_data, normalize_name, find_by_specs, add_new_model
    from ui import display_results, print_header
except ImportError as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    print("تأكد من وجود ملفات ui.py و models_db.py في نفس مجلد main.py")
    sys.exit(1)

from rich.prompt import Prompt
from rich.console import Console

console = Console()

def add_model_to_group(group, model_name):
    normalized = normalize_name(model_name)
    existing_models = [normalize_name(m) for m in group.get("models", [])]
    existing_aliases = [normalize_name(a) for a in group.get("aliases", [])]
    
    if normalized not in existing_models and normalized not in existing_aliases:
        group["models"].append(model_name.title())
        if normalized not in existing_aliases:
            group["aliases"].append(normalized)
        return True
    return False

def smart_search_flow():
    query = Prompt.ask("\n🔍 Enter model name to search (e.g., Redmi 9)")
    normalized_query = normalize_name(query)
    
    data = load_data()
    
    found_group = None
    for group in data["groups"]:
        aliases = [normalize_name(a) for a in group.get("aliases", [])]
        models = [normalize_name(m) for m in group.get("models", [])]
        if normalized_query in aliases or normalized_query in models:
            found_group = group
            break
            
    if found_group:
        console.print(f"[green]✅ Found '{query}' in group: {found_group['primary_name']}[/green]")
        display_results([found_group])
        return
    console.print(f"[yellow]⚠️ Model '{query}' not found in database.[/yellow]")
    use_specs = Prompt.ask("Do you want to search by physical specs (Size, Cutout, Curve)?", choices=["y", "n"], default="y")
    
    if use_specs == "y":
        try:
            size = float(Prompt.ask("📏 Enter screen size (e.g., 6.53)"))
            cutout = Prompt.ask("🕳️ Enter cutout type (notch/hole/full)", choices=["notch", "hole", "full", "drop"], default="notch")
            curve = Prompt.ask("〰️ Enter curve type (flat/curved)", choices=["flat", "curved"], default="flat")
            
            console.print("[dim]Searching database for compatible models...[/dim]")
            matches = find_by_specs(size, cutout, curve)
            
            if matches:
                console.print(f"[green]✨ Found {len(matches)} compatible group(s) with same specs![/green]")
                display_results(matches)
                
                add_it = Prompt.ask(f"Add '{query}' to one of these groups?", choices=["y", "n"], default="y")
                if add_it == "y":
                    target_group = matches[0]
                    if add_model_to_group(target_group, query):
                        save_data(data)
                        console.print(f"[bold green]✅ Successfully added '{query}' to group '{target_group['primary_name']}'![/bold green]")
                    else:
                        console.print("[yellow]⚠️ Model already exists in this group.[/yellow]")
            else:
                console.print("[red]❌ No compatible models found with these exact specs.[/red]")
                create_new = Prompt.ask("Create a NEW group for this model?", choices=["y", "n"], default="y")
                if create_new == "y":
                    new_group = add_new_model(query, size, cutout, curve)
                    console.print(f"[bold green]✅ Created new group '{new_group['primary_name']}' successfully![/bold green]")
                    
        except ValueError:
            console.print("[red]❌ Invalid input. Please enter numbers for size.[/red]")

def main():
    while True:
        print_header("AMMAR TELECOM PRO - SMART SEARCH")
        console.print("[1] Smart Search (Auto-Detect & Add)")
        console.print("[0] Exit")
        
        choice = Prompt.ask("Select an option", choices=["0", "1"], default="1")
        
        if choice == "1":
            smart_search_flow()
            Prompt.ask("\nPress Enter to continue...")
        elif choice == "0":
            console.print("[bold blue]Goodbye! 👋[/bold blue]")
            break
if __name__ == "__main__":
    main()