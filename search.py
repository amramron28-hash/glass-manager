import json, os, re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# تحديد مسار ملف البيانات في نفس المجلد
DB_FILE = "models_db.json"

def load_data():
    if not os.path.exists(DB_FILE):
        console.print("[bold red]❌ خطأ: ملف models_db.json غير موجود في المجلد![/bold red]")
        return None
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red]❌ خطأ في قراءة الملف: {e}[/bold red]")
        return None

def normalize_text(text):
    """تنظيف النص وتوحيد الاختصارات للبحث الدقيق"""
    text = text.lower().strip()
    # قاموس اختصارات شائعة
    replacements = {
        "rm ": "redmi ", "redmi ": "redmi ",
        "op ": "oppo ", "oppo ": "oppo ",
        "sam ": "samsung galaxy ", "samsung ": "samsung galaxy ",
        "vi ": "vivo ", "vivo ": "vivo ",
        "poco ": "poco ", "xiomi ": "xiaomi ", "xiaomi ": "xiaomi ",
        "hw ": "huawei ", "huawei ": "huawei ",
        "hon ": "honor ", "honor ": "honor ",
        "1+": "oneplus ", "oneplus ": "oneplus ",
        "moto ": "motorola moto ", "motorola ": "motorola moto ",
        "inf ": "infinix ", "infinix ": "infinix ",
        "tec ": "tecno ", "tecno ": "tecno ",
        "itel ": "itel ",
        "iqoo ": "iqoo ",
        "nothing ": "nothing phone ",
        "black shark ": "black shark "
    }
    for key, val in replacements.items():
        text = text.replace(key, val)
    return text

def search_models(data, query):
    if not query:
        return []
        norm_query = normalize_text(query)
    results = []
    
    for group in data.get("groups", []):
        found = False
        for model in group.get("models", []):
            norm_model = normalize_text(model)
            # بحث ذكي: يتطابق إذا كان الاسم جزءاً من الموديل أو العكس
            if norm_query in norm_model or norm_model in norm_query:
                found = True
                break
        
        if found:
            results.append(group)
            
    return results

def display_results(results):
    if not results:
        console.print(Panel("[yellow]⚠️ لم يتم العثور على نتائج مطابقة. جرب اسماً مختلفاً أو اختصاراً.[/yellow]", border_style="yellow"))
        return

    console.print(Panel(f"[bold green]✅ تم العثور على {len(results)} مجموعة متوافقة[/bold green]", border_style="green"))
    
    for i, group in enumerate(results, 1):
        table = Table(title=f"[cyan]المجموعة #{i}: {group.get('name', 'بدون اسم')}[/cyan]", show_header=False, box=None)
        table.add_column("📱 الموديلات المتوافقة", style="white")
        
        # عرض أول 15 موديلاً فقط لتجنب الازدحام، مع إمكانية عرض الكل
        models = group.get("models", [])
        for model in models[:15]:
            table.add_row(model)
            
        if len(models) > 15:
            table.add_row(f"[dim]... و {len(models) - 15} موديلات أخرى[/dim]")
            
        console.print(table)
        console.print("-" * 50)

def main():
    console.clear()
    console.print(Panel("[bold blue]AMMAR TELECOM PRO - Glass Search[/bold blue]\nاكتب اسم الهاتف للبحث عن التوافقات", border_style="blue"))
    
    data = load_data()
    if not data:
        return

    while True:
        query = console.input("\n[bold cyan]🔍 ابحث عن هاتف (أو 'exit' للخروج): [/bold cyan]")
        if query.lower() == 'exit':            break
        
        results = search_models(data, query)
        display_results(results)

if __name__ == "__main__":
    main()