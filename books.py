# This app do webscrap data from html site

from bs4 import BeautifulSoup
import requests
import csv

url ="http://books.toscrape.com"
headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    # print(response.status_code)
    html_content = response.text
    
else:
    print("fetching error", response.status_code)

# Dictionary to convert rating words to numbers
rating_map = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

# Step 1: Get all category links
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

category_section = soup.find('div', class_='side_categories')
category_links = category_section.find_all('a')

# Prepare CSV file
with open("books_all_categories.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([ "Title", "Category", "Price (£)", "Availability", "Rating (1-5)"])

    # Step 2: Loop through each category
    for link in category_links[1:]:  # Skip the "Books" main link
        category_name = link.text.strip()
        category_url = requests.compat.urljoin(url, link.get('href'))

        while category_url:
            res = requests.get(category_url)
            page_soup = BeautifulSoup(res.text, 'lxml')

            # Step 3: Find all books on the current category page
            books = page_soup.find_all('article', class_='product_pod')

            for book in books:
                # Title
                title = book.h3.a['title'].strip()

                # Price
                price = book.find("p", class_="price_color").text.replace("Â", "").replace("£", "").strip()

                # Availability
                availability = book.find("p", class_="instock availability").text.strip()

                # Rating in words → convert to number
                rating_tag = book.find('p', class_='star-rating')
                rating_word = [cls for cls in rating_tag['class'] if cls != 'star-rating'][0]
                rating_number = rating_map.get(rating_word, 0)

                # Write to CSV
                writer.writerow([ title, category_name, price, availability, rating_number])

            # Step 4: Handle pagination
            next_button = page_soup.find('li', class_='next')
            if next_button:
                next_page = next_button.a['href']
                category_url = requests.compat.urljoin(category_url, next_page)
            else:
                break


print(" Book data successfully exported to 'books_travel_category.csv'")