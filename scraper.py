import requests
import random
import time
import os
import json
import colorama
import pyfiglet
from bs4 import BeautifulSoup
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from colorama import init, Fore

init(autoreset=True)
console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    ]
    return {"User-Agent": random.choice(user_agents)}

def get_google_results_API(query, max_pages, GOOGLE_API_KEY, GOOGLE_CX):
    urls = set()
    for page in range(max_pages):
        start = page * 10
        max_start = min(start, 90)
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&start={max_start}"
        try:
            response = requests.get(search_url, headers=get_random_headers(), timeout=5)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                urls.add(item["link"])

            if "nextPage" not in data.get("queries", {}):
                break  
        except requests.RequestException as e:
            print(Fore.RED + f"Error fetching Google results: {e}")
            break
        time.sleep(random.uniform(1, 3))
    return list(urls)

def get_google_results_noAPI(query, max_pages):
    urls = set()
    for page in range(max_pages):
        start = page * 10
        search_url = f"https://www.google.com/search?q={query}&start={start}"
        try:
            response = requests.get(search_url, headers=get_random_headers(), timeout=5)
            response.raise_for_status()
            
            if response.text.strip() == "":
                print(Fore.RED + "Google returned an empty response. Try again later.")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            
            for a in soup.select("div.tF2Cxc a"):
                urls.add(a["href"])
            
            if not urls:
                print(Fore.RED + "No results found. Google may have blocked the request.")
                break

        except requests.RequestException as e:
            print(Fore.RED + f"Error fetching Google results: {e}")
            break
        
        time.sleep(random.uniform(3, 7))
    return list(urls)


def get_bing_results(query, max_pages):
    urls = set()
    for page in range(max_pages):
        search_url = f"https://www.bing.com/search?q={query}&first={page * 10}"
        try:
            response = requests.get(search_url, headers=get_random_headers(), timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            links = [a['href'] for a in soup.select("a") if a.get('href', '').startswith("http")]

            if not links:
                print(Fore.RED + "No results found or Bing blocked the request.")
                break

            urls.update(links)
        except requests.RequestException as e:
            print(Fore.RED + f"Error fetching Bing results: {e}")
            break

        time.sleep(random.uniform(0.5, 2))  # Lebih cepat, tapi tetap aman

    return list(urls)


def main():
    clear_screen()
    scraper = pyfiglet.figlet_format("ScraperTools", font="slant")
    styled_text = Text(scraper, style="bold red")
    console.print(Panel(styled_text, subtitle="[bold cyan]V1.0[/bold cyan]", expand=False))
    
    print("\n1. Using API KEY")
    print("2. Not using API KEY")
    print("3. Close program\n")

    choice = input("Choose your option: ").strip()
    print("")
    print("────────────────────────────────────────────────────────────────────")
    print("")
    
    if choice == "1":
        GOOGLE_API_KEY = input("Enter your Google API KEY: ").strip()
        GOOGLE_CX = input("Enter your Custom Search Engine ID: ").strip()
        print("")
    elif choice == "2":
        GOOGLE_API_KEY = None
        GOOGLE_CX = None
    elif choice == "3":
        clear_screen()
        quit()
    else:
        print(Fore.RED + "Please enter the input correctly!")
        time.sleep(1)
        main()
        return

    query = input("Input dork: ").strip()
    try:
        max_pages = int(input("Max pages: ").strip())
    except ValueError:
        print(Fore.RED + "Invalid number! Defaulting to 1 page.")
        max_pages = 1

    filename = input("Enter the file name without a format: ").strip()
    
    print("\n────────────────────────────────────────────────────────────────────\n")
    
    results = []

    print(Fore.CYAN + "Scraping on Google...")
    if GOOGLE_API_KEY and GOOGLE_CX:
        google_results = get_google_results_API(query, max_pages, GOOGLE_API_KEY, GOOGLE_CX)
    else:
        google_results = get_google_results_noAPI(query, max_pages)

    google_lenght = len(google_results)
    if google_lenght == 0:
        print(Fore.RED + f"Found {len(google_results)} results from Google.")
    elif google_lenght > 0:
        print(Fore.YELLOW + f"Found {len(google_results)} results from Google.")

    print(Fore.CYAN + "Scraping on Bing...")
    bing_results = get_bing_results(query, max_pages)
    bing_lenght = len(bing_results)
    if bing_lenght == 0:
        print(Fore.RED + f"Found {len(bing_results)} results from Bing.")
    elif bing_lenght > 0:
        print(Fore.YELLOW + f"Found {len(bing_results)} results from Bing.")

    results.extend(google_results)
    results.extend(bing_results)
    results = list(set(results))  

    print("\n" + Fore.CYAN + "Results:")
    results_length = len(results)
    if results_length == 0:
        print(Fore.RED + f"No results found.")
    else:
        for result in results:
            print(Fore.WHITE + result)

    print(Fore.BLUE + f"\nTotal results: {len(results)}")

    output_folder = os.path.join(os.path.dirname(__file__), "result")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_path = os.path.join(output_folder, filename)
    with open(output_path + ".txt", "w") as f:
        f.write("\n".join(results))

    print(Fore.GREEN + f"Results have been saved in the file {filename}.txt")

    print("\n────────────────────────────────────────────────────────────────────")
    close = input("Do you want to continue this program? (y/N): ").strip().lower()
    if close == "y":
        main()
    else:
        print(Fore.RED + "Thanks for using ScraperTools!")
        time.sleep(1)
        clear_screen()
        quit()

if __name__ == "__main__":
    main()
