import requests
from bs4 import BeautifulSoup
import random
import time
import mysql.connector

def scrape_google_search(query, num_results=10):
    base_url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing Google search results: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    search_results = []

    for result in soup.find_all("div", class_="tF2Cxc"):
        link = result.find("a")
        title = result.find("h3")
        snippet = result.find("span", class_="aCOpRe")

        if link and title:
            search_result = {
                "title": title.get_text(),
                "url": link["href"],
                "snippet": snippet.get_text() if snippet else ""
            }
            search_results.append(search_result)

    return search_results

def save_to_mysql(search_results):
    db_connection = None  # Initialize db_connection variable
    try:
        # Connect to MySQL database
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Enter your MySQL password here
            database="google_search_data",
            port=3306  # Default MySQL port
        )

        # Create cursor object to execute SQL queries
        cursor = db_connection.cursor()

        # Insert each search result into the MySQL database
        for result in search_results:
            sql = "INSERT INTO search_results (title, url, snippet) VALUES (%s, %s, %s)"
            values = (result["title"], result["url"], result["snippet"])
            cursor.execute(sql, values)

        # Commit changes and close cursor
        db_connection.commit()
        cursor.close()

        print("Data saved successfully to MySQL database.")

    except mysql.connector.Error as e:
        print(f"Error saving data to MySQL database: {e}")

    finally:
        # Close database connection
        if db_connection.is_connected():
            db_connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    query = "beauty products"
    num_results = 1000

    beauty_search_results = scrape_google_search(query, num_results)
    if beauty_search_results:
        save_to_mysql(beauty_search_results)
    else:
        print("No search results found.")
