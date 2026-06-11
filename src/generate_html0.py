import re
from datetime import datetime


def parse_recipes(text: str) -> list[dict]:
    """
    Parst de markdown output van Claude naar een lijst van recepten.
    Elk recept is een dict met: title, time, ingredients, steps
    """
    recipes = []
    blocks = re.split(r'\*\*(?=\d|\w)', text)

    for block in text.split('**'):
        pass

    recipe_pattern = re.split(r'(?=\*\*[^\*]+\*\*\n)', text)

    current = None
    mode = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        title_match = re.match(r'\*\*(.+?)\*\*', line)
        if title_match:
            if current:
                recipes.append(current)
            current = {"title": title_match.group(1), "time": "", "ingredients": [], "steps": []}
            mode = None
            continue

        if current is None:
            continue

        if line.startswith('⏱'):
            current["time"] = line.replace('⏱', '').strip()
            continue

        if line.lower().startswith('ingredient') or line.lower().startswith('ingrediënt'):
            mode = 'ingredients'
            continue
        if line.lower().startswith('instruction') or line.lower().startswith('bereiding') or line.lower().startswith(
                'instructie'):
            mode = 'steps'
            continue

        if mode == 'ingredients' and line.startswith('-'):
            current["ingredients"].append(line[1:].strip())
        elif mode == 'steps' and re.match(r'^\d+\.', line):
            current["steps"].append(re.sub(r'^\d+\.\s*', '', line))

    if current:
        recipes.append(current)

    return recipes


def render_ingredients(ingredients: list[str]) -> str:
    html = ""
    for ing in ingredients:
        if '—' in ing:
            parts = ing.split('—', 1)
            name = parts[0].replace('←', '').strip()
            deal = parts[1].replace('←', '').strip()
            html += f'''
        <div class="ingredient">
          <span class="ing-name">{name}</span>
          <span class="deal">{deal}</span>
        </div>'''
        else:
            name = ing.replace('←', '').replace('←', '').strip()
            html += f'''
        <div class="ingredient">
          <span class="ing-name">{name}</span>
          <span class="deal staple">eigen voorraad</span>
        </div>'''
    return html


def render_steps(steps: list[str]) -> str:
    html = ""
    for i, step in enumerate(steps, 1):
        html += f'''
        <div class="step">
          <span class="step-num">{i:02d}</span>
          <span class="step-text">{step}</span>
        </div>'''
    return html


def render_recipe(recipe: dict, index: int) -> str:
    total = 5
    ingredients_html = render_ingredients(recipe["ingredients"])
    steps_html = render_steps(recipe["steps"])

    return f'''
    <div class="recipe">
      <div class="recipe-meta">
        <span class="recipe-num">{index:02d} / {total:02d}</span>
        <span class="recipe-time">{recipe["time"]}</span>
      </div>
      <h2 class="recipe-title">{recipe["title"]}</h2>

      <div class="section-label">ingrediënten</div>
      <div class="ingredients">{ingredients_html}
      </div>

      <div class="section-label">bereiding</div>
      <div class="steps">{steps_html}
      </div>
    </div>'''


def generate_html(recipes_text: str) -> str:
    now = datetime.now()
    week = now.isocalendar().week
    year = now.year
    date_str = now.strftime("%d %B %Y").lstrip("0").lower()

    recipes = parse_recipes(recipes_text)
    recipes_html = ""
    for i, recipe in enumerate(recipes, 1):
        recipes_html += render_recipe(recipe, i)

    return f'''<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AH recepten — week {week}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #f9f8f6;
      --surface: #ffffff;
      --text: #1a1a18;
      --muted: #888780;
      --faint: #d3d1c7;
      --accent: #1a1a18;
    }}

    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #111110;
        --surface: #1a1a18;
        --text: #f1efe8;
        --muted: #888780;
        --faint: #444441;
        --accent: #f1efe8;
      }}
    }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      line-height: 1.6;
      padding: 3rem 1.25rem 6rem;
    }}

    .page {{
      max-width: 480px;
      margin: 0 auto;
    }}

    header {{
      margin-bottom: 3rem;
    }}

    .header-label {{
      font-size: 10px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 0.25rem;
    }}

    .header-week {{
      font-size: 22px;
      font-weight: 500;
      color: var(--text);
      margin-bottom: 0.15rem;
    }}

    .header-date {{
      font-size: 11px;
      color: var(--muted);
    }}

    .recipe {{
      border-top: 0.5px solid var(--faint);
      padding: 2rem 0;
    }}

    .recipe:last-child {{
      border-bottom: 0.5px solid var(--faint);
    }}

    .recipe-meta {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 0.35rem;
    }}

    .recipe-num {{
      font-size: 10px;
      color: var(--muted);
      letter-spacing: 0.08em;
    }}

    .recipe-time {{
      font-size: 10px;
      color: var(--muted);
    }}

    .recipe-title {{
      font-size: 16px;
      font-weight: 500;
      color: var(--text);
      margin-bottom: 1.5rem;
      line-height: 1.3;
    }}

    .section-label {{
      font-size: 9px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 0.6rem;
      margin-top: 1.25rem;
    }}

    .ingredient {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 1rem;
      padding: 4px 0;
      border-bottom: 0.5px solid var(--faint);
    }}

    .ingredient:last-child {{
      border-bottom: none;
    }}

    .ing-name {{
      color: var(--text);
      font-size: 12px;
    }}

    .deal {{
      font-size: 11px;
      color: var(--muted);
      white-space: nowrap;
      font-style: italic;
    }}

    .deal.staple {{
      opacity: 0.45;
    }}

    .step {{
      display: flex;
      gap: 1rem;
      padding: 5px 0;
    }}

    .step-num {{
      color: var(--muted);
      min-width: 20px;
      font-size: 11px;
      padding-top: 1px;
    }}

    .step-text {{
      color: var(--text);
      font-size: 12px;
      line-height: 1.65;
    }}

    footer {{
      margin-top: 4rem;
      font-size: 10px;
      color: var(--muted);
      text-align: center;
      letter-spacing: 0.08em;
    }}
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="header-label">Albert Heijn bonus</div>
      <div class="header-week">week {week} — {year}</div>
      <div class="header-date">{date_str}</div>
    </header>

    {recipes_html}

    <footer>gegenereerd op {date_str}</footer>
  </div>
</body>
</html>'''


def save_html(recipes_text: str) -> str:
    now = datetime.now()
    week = now.isocalendar().week
    year = now.year
    filename = f"recepten_week{week}_{year}.html"

    html = generate_html(recipes_text)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return filename


if __name__ == "__main__":
    test_text = """
**Spinazie pasta met tonijn**
⏱ 22 minutes

Ingredients:
- Grand' Italia Rigatoni 500g — voor €0.99 ← discount
- AH Spinazie 450g — 55% korting ← discount
- Rio Mare Tonijn in olijfolie — 2e gratis ← discount
- knoflook, ui, citroen ← staple

Instructions:
1. Kook de pasta gaar en bewaar een kopje kookwater.
2. Fruit knoflook en ui in olijfolie, voeg spinazie toe.
3. Meng tonijn erdoor, pasta erbij, breng op smaak.

**BBQ worst met stamppot**
⏱ 25 minutes

Ingredients:
- AH BBQ worst naturel 350g — 1+1 gratis ← discount
- aardappelen, mosterd, ui ← staple

Instructions:
1. Kook aardappelen 15 minuten en stamp ze grofweg.
2. Bak worst in plakken goudbruin, ongeveer 8 minuten.
3. Serveer met mosterd en gebakken ui ernaast.
"""
    filename = save_html(test_text)
    print(f"Opgeslagen als: {filename}")
