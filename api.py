import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def get_search_results(search_query, num_pages):
    # Set up Chrome options to run headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to chromedriver.exe
    exe_path = os.path.join(current_dir, "chromedriver.exe")

    service = Service(exe_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get('https://www.google.com')

    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    titles = []
    urls = []
    pages = []

    for page in range(num_pages):
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')  # Use 'html.parser' instead of 'lxml'
        search_results = soup.find_all('div', {'class': 'g'})
        for result in search_results:
            title_tag = result.find('h3')
            if title_tag:
                titles.append(title_tag.get_text(strip=True))
            else:
                titles.append('N/A')

            link_tag = result.find('a')
            if link_tag and 'href' in link_tag.attrs:
                urls.append(link_tag['href'])
            else:
                urls.append('N/A')

            pages.append(page + 1)

        try:
            next_button = driver.find_element(By.ID, 'pnnext')
            next_button.click()
        except Exception as e:
            st.write(f"Error navigating to next page: {e}")
            break

    driver.quit()

    df = pd.DataFrame({
        'Title': titles,
        'URL': urls,
        'Page': pages
    })

    return df

def main():
    st.title('Google Search Results Scraper')

    search_query = st.text_input("Enter the newsletter you want to search for:")
    num_pages = st.number_input("Enter the number of pages to scrape:", min_value=1, value=1)

    if st.button('Search'):
        if search_query:
            with st.spinner('Searching...'):
                df = get_search_results(search_query, num_pages)
                
            st.write("Search Results:")
            st.dataframe(df)
            
            # Create a downloadable CSV file
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='google_search_results.csv',
                mime='text/csv'
            )
        else:
            st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()
