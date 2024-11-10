import random
import time
import pickle
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pymongo import MongoClient
from bs4 import BeautifulSoup
from termcolor import colored
import urllib.parse
import re

# Proxy and MongoDB setup
proxy_host = "127.0.0.1"
proxy_port = 8118
client = MongoClient("mongodb://localhost:27017/")
db = client["scraped_data"]
collection = db["posts"]

# File to track last URL scraped
checkpoint_file = "scraping_checkpoint.pkl"

# Initialize Firefox Options
options = Options()
options.set_preference("network.proxy.type", 1)
options.set_preference("network.proxy.http", proxy_host)
options.set_preference("network.proxy.http_port", proxy_port)
options.set_preference("network.proxy.ssl", proxy_host)
options.set_preference("network.proxy.ssl_port", proxy_port)
options.set_preference("network.proxy.socks", proxy_host)
options.set_preference("network.proxy.socks_port", proxy_port)
options.set_preference("network.proxy.socks_version", 5)
options.set_preference("network.proxy.no_proxies_on", "")
driver = webdriver.Firefox(options=options)

# Target URL
start_url = "http://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion"

# Load checkpoint if it exists
def load_checkpoint():
    try:
        with open(checkpoint_file, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return [start_url]

# Save the current scraping state to resume later
def save_checkpoint(url_queue):
    with open(checkpoint_file, 'wb') as f:
        pickle.dump(url_queue, f)

# Function to clean text by removing unwanted characters
def clean_text(text):
    text = re.sub(r'[\n\r]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

# Function to extract cookies and close the browser
def extract_cookies(driver):
    cookies = driver.get_cookies()
    driver.quit()
    return {cookie['name']: cookie['value'] for cookie in cookies}

# Set up session with cookies
def setup_requests_session(cookies):
    session = requests.Session()
    session.proxies = {'http': f'http://{proxy_host}:{proxy_port}', 'https': f'http://{proxy_host}:{proxy_port}'}
    session.cookies.update(cookies)
    return session

# Scrape post content
def scrape_post_content(session, post_url, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            response = session.get(post_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                content = soup.find('div', class_='postContent').get_text(separator="\n")
                return clean_text(content)
            else:
                print(colored(f"Warning: Failed to retrieve content from {post_url}", "yellow"))
        except requests.exceptions.RequestException as e:
            attempt += 1
            print(colored(f"Connection error on {post_url}, retry {attempt}/{retries}: {e}", "red"))
            time.sleep(5)  # Wait before retrying
    return ""

# Scrape a page and retrieve post data
def scrape_page(session, url, scraped_posts, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                posts = [
                    post for post in soup.find_all('div', class_='item')
                    if post.find('a', class_='title') and post.find('div', class_='voteCount')
                ]

                for post in posts:
                    try:
                        title = post.find('a', class_='title').get_text(strip=True)
                        post_link = post.find('a', class_='title')['href']
                        full_post_link = urllib.parse.urljoin(url, post_link)

                        # Skip post if already processed
                        if full_post_link in scraped_posts:
                            print(colored(f"Skipping duplicate post: {title}", "yellow"))
                            continue

                        upvotes = int(post.find('div', class_='voteCount').get_text(strip=True))

                        # Process the author name and area, removing /u/
                        author_tag = post.find('div', class_='author').find('a')
                        author = author_tag.get_text(strip=True).replace('/u/', '')
                        area = post.find('div', class_='author').find_all('a')[1].get_text(strip=True)

                        print(colored(f"Scraping post: {title} | URL: {full_post_link}", "cyan"))
                        
                        # Scrape post content and clean it
                        post_content = scrape_post_content(session, full_post_link)

                        # Document to insert into MongoDB
                        post_document = {
                            "Title": title,
                            "Author": author,
                            "Area": area,
                            "Upvotes": upvotes,
                            "Content": post_content,
                            "URL": full_post_link
                        }

                        # Check if post already exists in MongoDB
                        if collection.count_documents({"URL": full_post_link}, limit=1) == 0:
                            collection.insert_one(post_document)
                            print(colored(f"Post saved: {title}", "green"))
                        else:
                            print(colored(f"Post already exists in database: {title}", "yellow"))

                        # Mark post as processed
                        scraped_posts[full_post_link] = True

                    except Exception as e:
                        print(colored(f"Error parsing post: {e}", "red"))

                pagination_links = soup.select('div.pagination a')
                next_pages = [urllib.parse.urljoin(url, link['href']) for link in pagination_links if link.get('href')]
                print(colored(f"Found pagination links: {next_pages}", "blue"))

                return next_pages
            else:
                print(colored(f"Failed to scrape {url}, status code: {response.status_code}", "red"))
        except requests.exceptions.RequestException as e:
            attempt += 1
            print(colored(f"Connection error on {url}, retry {attempt}/{retries}: {e}", "red"))
            time.sleep(5)
    return []

# Main function
def main():
    try:
        print(colored(f"Opening URL: {start_url}", "blue"))
        driver.get(start_url)
        print(colored("Waiting 60 seconds to ensure the session is established...", "yellow"))
        time.sleep(60)

        cookies = extract_cookies(driver)
        session = setup_requests_session(cookies)

        to_scrape = load_checkpoint()
        scraped = set()
        scraped_posts = {}

        while to_scrape:
            url = to_scrape.pop(0)
            if url not in scraped:
                print(colored(f"Scraping page: {url}", "magenta"))
                new_links = scrape_page(session, url, scraped_posts)

                # Avoid duplicates in to_scrape
                to_scrape.extend(link for link in new_links if link not in scraped and link not in to_scrape)
                scraped.add(url)

                save_checkpoint(to_scrape)
                time.sleep(random.uniform(5, 15))

    except Exception as e:
        print(colored(f"Error in main scraping function: {e}", "red"))

if __name__ == "__main__":
    main()
