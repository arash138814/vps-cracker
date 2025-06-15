from bs4 import BeautifulSoup
import re
import requests
import time
from datetime import datetime
BOT_TOKEN = "86078049:GNDALW69mrTsaWNnU5L2dCsKmsAaTTHNXWLDSLCe"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
chat_ids = set()
def extract_dorks(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tbody = soup.find('tbody')
    if not tbody:
        print("No tbody found in HTML")
        return []
    rows = tbody.find_all('tr')
    if not rows:
        print("No rows found in tbody")
        return []
    dorks = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
        dork_cell = cells[1]
        dork_text = dork_cell.find('font')
        if dork_text:
            text_content = dork_text.get_text(strip=True)
            dork_match = re.search(r'Dork:\s*(.+)', text_content, re.IGNORECASE)
            if dork_match:
                dork = dork_match.group(1).strip()
                dorks.append(dork)
                print(f"Extracted dork: {dork}")
            else:
                print(f"No dork match in: {text_content}")
        else:
            print(f"No font tag in row: {dork_cell}")
    return dorks
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        updates = response.json()
        if updates.get("ok") and updates.get("result"):
            return updates["result"][-1]
        return None
    except requests.RequestException as e:
        print(f"Error in get_updates: {e}")
        return None
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        print(f"Message sent to {chat_id}: {text}")
        return response.json()
    except requests.RequestException as e:
        print(f"Error in send_message: {e}")
        return {"ok": False}
def main():
    last_dork = ""
    chat_id = None
    print("Waiting for first message to get chat_id...")
    while chat_id is None:
        update = get_updates()
        if update and "message" in update:
            chat_id = update["message"]["chat"]["id"]
            chat_ids.add(chat_id)
            print(f"Found chat_id: {chat_id}")
        time.sleep(5)
    print("Bot started...")
    while True:
        try:
            url = "https://cxsecurity.com/dorks/"
            response = requests.get(url).text
            dorks = extract_dorks(response)
            if dorks and dorks[0] != last_dork:
                new_dork = dorks[0]
                print(f"New dork detected: {new_dork}")
                last_dork = new_dork
                for cid in chat_ids:
                    send_message(cid, f"New dork found at {datetime.now()}: {new_dork}")
            else:
                print("No new dorks or same as last time")
        except Exception as e:
            print(f"Error in main loop: {e}")
        time.sleep(1 * 24 * 60 * 60)
if __name__ == "__main__":
    main()
