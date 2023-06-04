import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import time
import sqlite3
import xml.etree.ElementTree as ET

# Color codes
SUCCESS_COLOR = '\033[92m'  # Green
INFO_COLOR = '\033[94m'  # Light Blue
ERROR_COLOR = '\033[91m'  # Red
RESET_COLOR = '\033[0m'  # Reset color


def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f'{ERROR_COLOR}Failed to fetch the website content{RESET_COLOR}')
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", {"class": "mirror-table table-mr table-responsive"})

    data = []
    rows = table.find_all("tr")  # Find all table rows
    for row in rows:
        columns = row.find_all("td")  # Find all table cells in each row
        row_data = [column.text.strip() for column in columns]  # Extract the text content from each cell
        data.append(row_data)

    return data


def save_to_csv(data, filename):
    headers = data[0]
    rows = data[1:]

    with open(filename, 'w') as file:
        file.write(','.join(headers) + '\n')
        for row in rows:
            file.write(','.join(row) + '\n')


def save_to_txt(data, filename):
    headers = data[0]
    rows = data[1:]

    with open(filename, 'w') as file:
        file.write('\t'.join(headers) + '\n')
        for row in rows:
            file.write('\t'.join(row) + '\n')


def save_to_xml(data, filename):
    root = ET.Element('data')
    headers = data[0]
    for row in data[1:]:
        if len(row) == len(headers):  # Check if the row has the correct number of values
            item = ET.SubElement(root, 'item')
            for i in range(len(headers)):
                header = headers[i]
                value = row[i]
                sub_element = ET.SubElement(item, header)
                sub_element.text = value

    tree = ET.ElementTree(root)
    tree.write(filename)


def save_to_sql(data, filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()

    # Create table
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS scraped_data (
        Date TEXT,
        Hacker TEXT,
        Team TEXT,
        M TEXT,
        R TEXT,
        H TEXT,
        G TEXT,
        B TEXT,
        Website TEXT,
        Mirror TEXT
    );
    '''
    c.execute(create_table_query)

    # Insert data
    headers = data[0]
    rows = data[1:]
    insert_query = f'''
    INSERT INTO scraped_data {tuple(headers)}
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    '''
    c.executemany(insert_query, rows)

    conn.commit()
    conn.close()


def main():
    banner = """
\033[91m   _____ __   _     ____ __ _ ____         _    _____
  / ___// /__(_)___/ / //_/(_) / /__  ____| |  / <  /
  \__ \/ //_/ / __  / ,<  / / / / _ \/ ___/ | / // / 
 ___/ / ,< / / /_/ / /| |/ / / /  __/ /   | |/ // /  
/____/_/|_/_/\__,_/_/ |_/_/_/_/\___/_/    |___//_/   
         Sicarios SkidKillerv1 | 2023                                            
\033[0m"""

    print(banner)

    num_pages = int(input("Enter the number of pages to scrape: "))

    base_url = "https://zone-xsec.com/country/AU/page="
    output_data = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}{page}"
        page_data = scrape_website(url)
        output_data.extend(page_data)

    if output_data:
        headers = ["Date", "Hacker", "Team", "M", "R", "H", "G", "B", "Website", "Mirror"]
        # Convert the scraped data to a list of lists
        data = [headers] + output_data

        # Print the data as a formatted table
        table = tabulate(data, headers="firstrow", tablefmt="pretty")
        print(f"{SUCCESS_COLOR}{table}{RESET_COLOR}")

        # Prompt user for rerun
        try:
            rerun = input("Would you like to rerun the script after a specified time? (y/n): ")
            if rerun.lower() == 'y':
                time_interval = int(input("Enter the time interval in seconds: "))
                print("Script will rerun after the specified time interval.")
                time.sleep(time_interval)
                main()
            else:
                print("Script has finished.")

            # Prompt user for output type
            output_type = input("Select the output type (CSV, TXT, XML, SQL): ").lower()
            if output_type == 'csv':
                csv_filename = input("Enter the CSV filename: ")
                save_to_csv(data, csv_filename)
                print(f"{SUCCESS_COLOR}Data saved to {csv_filename}{RESET_COLOR}")
            elif output_type == 'txt':
                txt_filename = input("Enter the TXT filename: ")
                save_to_txt(data, txt_filename)
                print(f"{SUCCESS_COLOR}Data saved to {txt_filename}{RESET_COLOR}")
            elif output_type == 'xml':
                xml_filename = input("Enter the XML filename: ")
                save_to_xml(data, xml_filename)
                print(f"{SUCCESS_COLOR}Data saved to {xml_filename}{RESET_COLOR}")
            elif output_type == 'sql':
                sql_filename = input("Enter the SQLite filename: ")
                save_to_sql(data, sql_filename)
                print(f"{SUCCESS_COLOR}Data saved to {sql_filename}{RESET_COLOR}")
            else:
                print(f"{ERROR_COLOR}Invalid output type.{RESET_COLOR}")
        except KeyboardInterrupt:
            print(f"\n{INFO_COLOR}Script interrupted by user. Exiting gracefully...{RESET_COLOR}")
            return

    else:
        print("No data found on the webpage.")


if __name__ == '__main__':
    main()
