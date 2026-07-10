import requests, difflib
from datetime import datetime

# carrega templates
with open("targets.txt") as f:
    TEMPLATES = [l.strip() for l in f if l.strip() and not l.startswith("#")]

my_id = "wiener"

with open("ids.txt", encoding="utf-8-sig") as f:
    test_ids = [l.lstrip("\ufeff").strip() for l in f if l.strip()]

log_file = open("idor_log.jsonl", "a", encoding="utf-8")
def gravar(msg): log_file.write(msg + "\n")

for URL_TEMPLATE in TEMPLATES:
    print(f"\n== Testando {URL_TEMPLATE}")
    base_html = requests.get(URL_TEMPLATE.format(ID=my_id)).text

    for target_id in test_ids:
        html  = requests.get(URL_TEMPLATE.format(ID=target_id)).text
        ratio = difflib.SequenceMatcher(None, base_html, html).ratio()

        if ratio < 0.95:
            print(f"⚠️  Suspeita com {target_id} (similaridade {ratio:.2f})")

            gravar(f"{datetime.now().isoformat()} | {URL_TEMPLATE} | {target_id} | {ratio:.2f}")

            for line in difflib.unified_diff(base_html.splitlines(),
                                             html.splitlines(), n=2, lineterm=""):
                if line.startswith(("+", "-")) and line.strip():
                    print(line[:150])
        else:
            print(f"{target_id}: nada de diferente ✅")