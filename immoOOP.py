import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import time
from typing import Any, Dict, List, Optional, Set, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

class ImmoWebScraper:
    """
    A web scraper for extracting property data from the Immoweb website.
    
    Attributes:
        headers (dict): HTTP headers for the requests.
        base_url_sale (str): The base URL for properties for sale.
        base_url_rent (str): The base URL for properties for rent.
        data (list): List to store extracted property data.
        seen_links (set): Set to keep track of processed property links.
        max_workers (int): Number of concurrent threads for scraping.
    """
    headers: Dict[str, str]
    base_url_sale: str
    base_url_rent: str
    data: List[Dict[str, Union[str, int, Optional[int]]]]
    seen_links: Set[str]
    max_workers: int

    def __init__(self, max_workers: int = 10) -> None:
        """
        Initializes the ImmoWebScraper with optional parameters.
        
        Args:
            max_workers (int): Number of concurrent threads for scraping.
        """
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.base_url_sale = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page="
        self.base_url_rent = "https://www.immoweb.be/en/search/house-and-apartment/for-rent?countries=BE&priceType=MONTHLY_RENTAL_PRICE&page="
        self.data = []
        self.seen_links = set()
        self.max_workers = max_workers
        self.scrape_all_pages()

    def scrape_all_pages(self) -> None:
        """
        Scrapes all pages of property listings until no more properties are found.
        """
        for sale_type, base_url in [('For Sale', self.base_url_sale), ('For Rent', self.base_url_rent)]:
            page = 1
            while True:
                print(f"Scraping page {page} for {sale_type}")
                url = base_url + str(page)
                property_links = self.scrape_page(url, sale_type)
                if not property_links:
                    break
                page += 1
                time.sleep(0.1)  # Small delay to avoid overwhelming the server

    def scrape_page(self, url: str, sale_type: str) -> Optional[List[str]]:
        """
        Scrapes a single page of property listings.
        
        Args:
            url (str): The URL of the page to scrape.
            sale_type (str): Type of the property listing ('For Sale' or 'For Rent').
        
        Returns:
            Optional[List[str]]: List of property links found on the page.
        """
        soup = self.get_soup(url)
        if not soup:
            return None
        property_links = self.get_links(soup)
        if not property_links:
            return None
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.scrape_property, link, sale_type) for link in property_links]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.add_property(result)
        return property_links

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Sends a GET request to the URL and returns a BeautifulSoup object.
        
        Args:
            url (str): The URL to request.
        
        Returns:
            Optional[BeautifulSoup]: Parsed HTML of the page.
        """
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        return None

    def get_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts property links from the soup object.
        
        Args:
            soup (BeautifulSoup): The parsed HTML of the page.
        
        Returns:
            List[str]: List of property links found.
        """
        return [link["href"] for link in soup.find_all('a', class_="card__title-link")]

    def scrape_property(self, link: str, sale_type: str) -> Optional[Dict[str, Union[str, int, Optional[int]]]]:
        """
        Scrapes a single property page.
        
        Args:
            link (str): The URL of the property page.
            sale_type (str): Type of the property listing ('For Sale' or 'For Rent').
        
        Returns:
            Optional[Dict[str, Union[str, int, Optional[int]]]]: Extracted property data.
        """
        if link in self.seen_links:
            return None
        self.seen_links.add(link)
        soup = self.get_soup(link)
        return self.extract_property_data(soup, sale_type) if soup else None

    def extract_property_data(self, soup: BeautifulSoup, sale_type: str) -> Optional[Dict[str, Union[str, int, Optional[int]]]]:
        """
        Extracts property data from the soup object.
        
        Args:
            soup (BeautifulSoup): The parsed HTML of the property page.
            sale_type (str): Type of the property listing ('For Sale' or 'For Rent').
        
        Returns:
            Optional[Dict[str, Union[str, int, Optional[int]]]]: Extracted property data.
        """
        try:
            script_tag = next((tag.string for tag in soup.find_all('script', type='text/javascript') if 'window.classified' in str(tag.string)), None)
            if not script_tag:
                return None
            json_data = re.search(r'window.classified = ({.*});', script_tag).group(1)
            property_dict = json.loads(json_data)

            property_data = {
                'Locality': self.safe_get(property_dict, ['property', 'location', 'locality']),
                'Price': self.safe_get(property_dict, ['transaction', 'sale', 'price']) if sale_type == 'For Sale' else self.safe_get(property_dict, ['transaction', 'rental', 'price']),
                'Type': self.safe_get(property_dict, ['property', 'type']),
                'Subtype': self.safe_get(property_dict, ['property', 'subtype']),
                'Rooms': self.safe_get(property_dict, ['property', 'bedroomCount']),
                'Living Area': self.safe_get(property_dict, ['property', 'netHabitableSurface']),
                'Fully equipped kitchen': 1 if self.safe_get(property_dict, ['property', 'kitchen', 'type']) == 'HYPER_EQUIPPED' else 0,
                'Furnished': 1 if self.safe_get(property_dict, ['property', 'furniture', 'isFurnished']) else 0,
                'Open fire': 1 if self.safe_get(property_dict, ['property', 'fireplaceExists']) else 0,
                'Terrace': 1 if self.safe_get(property_dict, ['property', 'hasTerrace']) else 0,
                'Terrace Area': self.safe_get(property_dict, ['property', 'terraceSurface']),
                'Garden': 1 if self.safe_get(property_dict, ['property', 'hasGarden']) else 0,
                'Garden Area': self.safe_get(property_dict, ['property', 'gardenSurface']),
                'Surface of the plot': self.safe_get(property_dict, ['property', 'land', 'surface']),
                'Number of facades': self.safe_get(property_dict, ['property', 'building', 'facadeCount']),
                'Swimming pool': 1 if self.safe_get(property_dict, ['property', 'hasSwimmingPool']) else 0,
                'State of the building': self.safe_get(property_dict, ['property', 'building', 'condition']),
                'Sale Type': sale_type
            }

            for key, value in property_data.items():
                if value is None:
                    property_data[key] = "None"


            return property_data
        except Exception as e:
            print(f"Error extracting data: {e}")
            return None

    def safe_get(self, dictionary: Dict[str, Any], keys: List[str]) -> Any:
        """
        Safely gets a value from a nested dictionary.
        
        Args:
            dictionary (dict): The dictionary to extract the value from.
            keys (list): List of keys to navigate through the dictionary.
        
        Returns:
            Any: The extracted value or None if not found.
        """
        for key in keys:
            dictionary = dictionary.get(key)
            if dictionary is None:
                return None
        return dictionary

    def add_property(self, property_data: Dict[str, Union[str, int, Optional[int]]]) -> None:
        """
        Adds property data to the data list if it is not a duplicate.
        
        Args:
            property_data (dict): The property data to add.
        """
        if property_data not in self.data:
            self.data.append(property_data)

    def save_to_csv(self, filename: str = 'properties.csv') -> None:
        """
        Saves the collected property data to a CSV file.
        
        Args:
            filename (str): The name of the CSV file.
        """
        if not self.data:
            print("No data to save.")
            return
        keys = self.data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.data)

if __name__ == "__main__":
    scraper = ImmoWebScraper()
    scraper.save_to_csv()
