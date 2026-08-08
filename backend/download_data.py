
import os 
import re
import requests

POST_MORTEM_DIR = "data/post_mortems"
RAW_LOG_DIR = "data/raw_logs"

os.makedirs(POST_MORTEM_DIR, exist_ok=True)
os.makedirs(RAW_LOG_DIR, exist_ok=True)

# 1. Fetch & Extract Real Incident Post-Mortems from 'danluu/post-mortems'
print('Downloading real Markdown post-mortems from icco/postmortems repository...')

GITHUB_API_URL = "https://api.github.com/repos/icco/postmortems/contents/data"

headers = {
    "User-Agent": "Incident-Triage-App"
}

response = requests.get(GITHUB_API_URL, headers=headers)

if response.status_code == 200:
    files = response.json()
    # filter for markdown files
    md_files = [f for f in files if f['name'].endswith('.md')]
    print(f"Found {len(md_files)} post-mortems upstream. Downloading the top 20...")

    count = 0
    for file_info in md_files[:20]:
        raw_url = file_info['download_url']
        file_name = file_info['name']

        file_resp = requests.get(raw_url, headers=headers)
        if file_resp.status_code == 200:
            save_path = os.path.join(POST_MORTEM_DIR, file_name)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(file_resp.text)
            count += 1
            print(f"  ├─ Downloaded: {file_name}")
    print(f"Successfully saved {count} full post-mortem files to {POST_MORTEM_DIR}/\n")
else:
    print(f"GitHub API Error: {response.status_code}. Details: {response.text}")

# 2. Fetch real samples from 'logpai/loghub
print("\nDownloading production log samples from logpai/loghub...")

LOGHUB_SAMPLES = {
    "linux_system.log": "https://raw.githubusercontent.com/logpai/loghub/master/Linux/Linux_2k.log",
    "apache_web.log": "https://raw.githubusercontent.com/logpai/loghub/master/Apache/Apache_2k.log",
    "openstack_cloud.log": "https://raw.githubusercontent.com/logpai/loghub/master/OpenStack/OpenStack_2k.log",
    "zookeeper.log": "https://raw.githubusercontent.com/logpai/loghub/master/Zookeeper/Zookeeper_2k.log"
}

for local_name, url in LOGHUB_SAMPLES.items():
    print(f"Fetching {local_name}...")
    log_resp = requests.get(url)
    if log_resp.status_code == 200:
        filepath = os.path.join(RAW_LOG_DIR, local_name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(log_resp.text)
            print(f"  └─ Saved {local_name} ({len(log_resp.text.splitlines())} log lines)")
    else:
        print(f"  └─ Failed to download {local_name}")

print("\nData download complete!")

