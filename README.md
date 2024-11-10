# Dark Web Scraper for Dread Forum with Tor and Privoxy

This project is a Python-based scraper designed to access and scrape posts from the Dread dark web forum. The script leverages `Selenium`, `Requests`, `MongoDB`, and proxies configured through `Tor` and `Privoxy` to safely navigate and access `.onion` sites.

## Table of Contents
- [Requirements](#requirements)
- [Project Setup](#project-setup)
- [Installing Dependencies](#installing-dependencies)
- [Tor and Privoxy Configuration](#tor-and-privoxy-configuration)
  - [Tor Installation and Configuration](#tor-installation-and-configuration)
  - [Privoxy Installation and Configuration](#privoxy-installation-and-configuration)
- [Running the Scraper](#running-the-scraper)
- [Project Features and Design](#project-features-and-design)
  - [Session Cookies](#session-cookies)
  - [Access Queue and Dread Navigation](#access-queue-and-dread-navigation)
  - [Data Extraction](#data-extraction)

---

## Requirements

Ensure your environment meets the following requirements:
- **Python** 
- **Selenium** for browser automation
- **Requests** for HTTP requests
- **MongoDB** for data storage
- **BeautifulSoup** for HTML parsing
- **Tor** and **Privoxy** to manage proxy connections

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AdilKhan000/Darkweb_Scraper.git
cd Darkweb_Scraper
```

### 2. Create a Virtual Environment
To isolate dependencies, we recommend using a Python virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installing Dependencies
Install the project’s dependencies from requirements.txt.

```bash
pip install -r requirements.txt
```

### 4. Tor and Privoxy Configuration
Tor Installation and Configuration
Install Tor on your machine:

```bash
sudo apt update
sudo apt install tor
``` 

Edit Tor Configuration to enable the necessary ports. Open the Tor configuration file and configure the following:

```text
SocksPort 9050
ControlPort 9051
```

Restart Tor to apply the changes:
```bash
sudo service tor restart
```

Privoxy Installation and Configuration
Install Privoxy:
```bash
sudo apt install privoxy
```
Configure Privoxy to forward HTTP traffic to the Tor SOCKS proxy. Edit the Privoxy configuration file:

```text
forward-socks5t / 127.0.0.1:9050 .
```

Restart Privoxy:

```bash
sudo service privoxy restart
``` 

Running the Scraper

Execute the scraper script:

```bash
python scraper.py
```

The scraper will connect to the specified .onion URL (Dread) and use Selenium to manage session cookies required for Dread’s access queue. The script will manage pagination and retries to handle intermittent connection issues.

# Dread Scraper

This Python script automates the scraping of data from the dark web marketplace Dread. 


### Project Features and Design

* **Session Cookies:**
    Dread utilizes session-based authentication with an access queue. This script leverages Selenium with a configured Tor proxy to automatically obtain and store session cookies, guaranteeing continuity when resuming the scraper after interruptions.

* **Respectful Access:**
    To avoid overwhelming Dread's servers and potentially triggering anti-bot measures, the scraper adheres to the existing access queue mechanism. It waits for 60 seconds after establishing a new session and leverages the acquired cookies from Selenium for subsequent requests via the `requests` library.

* **Targeted Data Extraction:**
    The script focuses on extracting valuable information from each post:
        - Title: Extracted from the post's designated title element.
        - Author: Extracted from the author metadata (if available).
        - Upvotes: Collected to gauge post popularity.
        - Post Content: The main body text from each post.

* **Comprehensive Pagination:**
    The script efficiently navigates through multiple Dread pages and follows all pagination links to ensure complete data capture.

* **Data Persistence:**
    It maintains a MongoDB collection for storing scraped post details (Title, Author, Upvotes, Content, URL), preventing duplicate entries by checking URLs before insertion.

* **Robust Checkpointing:**
    The scraper automatically saves progress in a file named `scraping_checkpoint.pkl`. This allows the script to resume from the last scrape point in case of unexpected termination, ensuring data consistency.

* **Adaptive Error Handling:**
    The script incorporates retry mechanisms and random delays to gracefully handle potential errors and avoid being flagged as a bot. 

* **Enhanced Security:**
    Network traffic is routed through a combination of Tor and Privoxy for enhanced anonymity and protection.

**Disclaimer:**

Please be aware that scraping data from Dread might violate their terms of service. Use this script responsibly and ethically, understanding that Dread might change its structure or employ anti-scraping measures that could affect the script's functionality.

