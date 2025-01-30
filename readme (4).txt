# 📌 Updated README for the Project

## 🔹 Project Description
This project automates the retrieval of services from an API, updates prices, and manages the main service file. The scripts run on a schedule (cron) and include logging and Telegram notifications.

## 📁 Project Structure
- `update_token.py` – Retrieves and updates the access token for the API.
- `fetch_and_update.py` – Fetches all services in a single request, analyzes changes, and updates the main file.
- `start_all.py` – Manages the execution of all processes and sends results to Telegram.

## 🔧 Installation & Execution
1. Clone the repository.
2. Install required dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Run `start_all.py` manually or set up execution via `cron`.

## 📊 Logging
All events are recorded in:
- `/home/public_html/wp-content/uploads/scripts/fetch_update_log.txt`

## 📩 Telegram Notifications
After service updates, a summary report is sent to Telegram, including:
- 🔄 Number of updated prices
- ➕ Newly added services
- ❌ Removed services
- 📝 General change summary

This mechanism allows for quick reporting without manually checking logs.

## 🕒 Automation via Cron
A `crontab` entry ensures daily execution of `start_all.py`:
```bash
40 7 * * * cd /home/public_html/wp-content/uploads/scripts && /usr/bin/python3 start_all.py > start_all_log.txt 2>&1
```
This guarantees regular data updates without manual intervention.

## 📌 Contact
For integration, automation, or customization for specific websites, feel free to contact me: 
[@dubrovski82](https://t.me/dubrovski82).

