### 🏠 Immoweb Property Data Scraper🏠




</center>

### 📜🔍 Project Overview 🔍📜

This project entails developing a web scraper to collect property data from Immoweb, a premier real estate website in Belgium.

The scraper gathers comprehensive details about properties listed for sale, including their location, type, price, number of rooms, and additional features like gardens, terraces, swimming pools, and more.

The collected data is then compiled into a CSV file for further analysis or utilization.

![Loading GIF](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fc.tenor.com%2FBPluFhmEcYQAAAAC%2Fletterkenny-scrap.gif&f=1&nofb=1&ipt=dad347232bc278f33a1e0f906f42496b4ab239dd7da00320c577bcf7be1dec79&ipo=images)

## 💻⌛ Installation ⌛💻

To run this project, ensure you have Python installed on your machine. Additionally, you will need to install the following Python libraries:

  ✅ `requests`
  ✅ `BeautifulSoup`
  ✅ `re`
  ✅ `json`
  ✅ `csv`
  ✅ `time`
  ✅ from `typing import Any, Dict, List, Optional, Set, Union`
  ✅ from `concurrent.futures import ThreadPoolExecutor`

## 🛠️⚙️ Usage ⚙️🛠️

To use the ImmoWebScraper, follow these steps:

1. Clone the repository and navigate to the project directory:

`git clone https://github.com/yourusername/immoweb-scraper.git
cd immoweb-scraper`

2. Install the required Python libraries:

`pip install requests beautifulsoup4`

keep on for the others

3. Run the scraper:

`python scraper.py`

4. The collected property data will be saved to a CSV file:

By default, the data will be saved to a file named properties.csv in the project directory. You can change the filename by modifying the filename parameter in the save_to_csv method call within the __main__ block of scraper.py

`if __name__ == "__main__":
    scraper = ImmoWebScraper()
    scraper.save_to_csv(filename='your_custom_filename.csv')`



## 🎯 Project Components: Functions and Descriptions 🎯

A web scraper for extracting property data from the Immoweb website.
Methods:

- `__init__(self, max_workers: int = 10) -> None`
Initializes the scraper with optional parameters, including the number of concurrent threads for scraping.

- `scrape_all_pages(self) -> None`
Scrapes all pages of property listings for both sale and rent until no more properties are found.

- `scrape_page(self, url: str, sale_type: str) -> Optional[List[str]]`
Scrapes a single page of property listings, returning a list of property links found on the page.

- `get_soup(self, url: str) -> Optional[BeautifulSoup]`
Sends a GET request to the URL and returns a BeautifulSoup object of the parsed HTML.

- `get_links(self, soup: BeautifulSoup) -> List[str]`
Extracts property links from the parsed HTML of the page.

- `scrape_property(self, link: str, sale_type: str) -> Optional[Dict[str, Union[str, int, Optional[int]]]]`
Scrapes a single property page, returning the extracted property data.

- `extract_property_data(self, soup: BeautifulSoup, sale_type: str) -> Optional[Dict[str, Union[str, int, Optional[int]]]]`
Extracts property data from the parsed HTML of the property page, including:


  * Locality: The location of the property.
  * Type of property: Indicates whether the property is a house or apartment.
  * Subtype of property: Specifies the subtype, such as bungalow, chalet, or mansion.
  * Price: The price of the property.
  * Type of sale: Specifies the type of sale, excluding life sales.
  * Number of rooms: The total number of rooms in the property.
  * Living Area: The living area in square meters.
  * Fully equipped kitchen: Indicates if the kitchen is fully equipped (Yes/No).
  * Furnished: Indicates if the property is furnished (Yes/No).
  * Open fire: Indicates if there is an open fire (Yes/No).
  * Terrace: Indicates if there is a terrace (Yes/No), and if so, its area in square meters.
  * Garden: Indicates if there is a garden (Yes/No), and if so, its area in square meters.
  * Surface of the plot: The surface area of the plot in square meters.
  * Number of facades: The number of facades the property has.
  * Swimming pool: Indicates if there is a swimming pool (Yes/No).
  * State of the building: Describes the condition of the building (e.g., new, to be renovated).
  

- `safe_get(self, dictionary: Dict[str, Any], keys: List[str]) -> Any`
Safely gets a value from a nested dictionary using a list of keys.

- `add_property(self, property_data: Dict[str, Union[str, int, Optional[int]]]) -> None`
Adds property data to the data list if it is not a duplicate.

- `save_to_csv(self, filename: str = 'properties.csv') -> None`
Saves the collected property data to a CSV file with the specified filename.

## 👥 Contributors 👥
⭐ kyllian Culot
⭐ Mehmet Batar
⭐ Adrien Piette

## 📅 Timeline 📅

Day 1: Project setup, library installation, and initial testing.
Days 2-3: Development and refinement of the web scraper.
Day 4: Data extraction, DataFrame creation, and CSV file handling.
Day 5: Documentation and final testing.
