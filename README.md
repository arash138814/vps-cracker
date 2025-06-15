# vps-cracker


NL Brute : https://mega.nz/file/uLpzHRyC#v9Lzo6LJAxkfaVnt1OvxF-bN-Niu0pVkTsCodlMFBuM `newamooz.com`

DUBrute : https://s9.picofile.com/d/8301380568/265b1619-589b-46a7-bb35-0697db1a6f90/DuBrute_8_2.zip password : `no password`

DUBrute : https://s2.picofile.com/file/8262294542/DUBrute_2_2_breach_team_org_dj_hack_.rar.html password : `breach-team.org_dj-hack`

ClearLock : https://www.snapfiles.com/downloads/clearlock/dlclearlock.html password : `no password`

from bs4 import BeautifulSoup
from re import search, IGNORECASE
from requests import get, post, RequestException
from time import sleep

# تصحیح توکن با نسخه اصلی که از @BotFather دریافت کردید
BOT_TOKEN = "8117450822:AAGyqDDtS7_Jvq2hEc3VLHQetIxtq0K7o"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def extract_dorks(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tbody = soup.find('tbody')
    if not tbody:
        print("No tbody found")
        return []
    rows = tbody.find_all('tr')
    if not rows:
        print("No rows found")
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
            dork_match = search(r'Dork:\s*(.+)', text_content, IGNORECASE)
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
    """دریافت پیام‌ها و استخراج chat_id"""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    try:
        response = get(url, params=params)
        response.raise_for_status()
        updates = response.json()
        if updates.get("ok") and updates.get("result"):
            return updates["result"][-1]  # آخرین آپدیت
        return None
    except RequestException as e:
        print(f"Error in get_updates: {e}")
        return None

def send_message(chat_id, text):
    """ارسال پیام به کاربر"""
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    try:
        response = post(url, params=params)
        response.raise_for_status()
        print(f"Message sent: {text}")
        return response.json()
    except RequestException as e:
        print(f"Error in send_message: {e}")
        return {"ok": False}

def main():
    last_dork = ""
    chat_id = None

    # دریافت اولیه chat_id
    print("Waiting for first message to get chat_id...")
    while chat_id is None:
        update = get_updates()
        if update and "message" in update:
            chat_id = update["message"]["chat"]["id"]
            print(f"Found chat_id: {chat_id}")
        sleep(5)  # منتظر بمانید تا پیام دریافت شود

    print("Bot started...")
    while True:
        try:
            url = "https://cxsecurity.com/dorks/"
            response = get(url).text
            dorks = extract_dorks(response)
            if dorks and dorks[0] != last_dork:
                new_dork = dorks[0]
                print(f"New dork detected: {new_dork}")
                last_dork = new_dork
                send_message(chat_id, f"New dork found: {new_dork}")
            else:
                print("No new dorks or same as last time")
        except Exception as e:
            print(f"Error in main loop: {e}")
        sleep(300)  # 5 دقیقه صبر کنید (300 ثانیه)

if __name__ == "__main__":
    main()
