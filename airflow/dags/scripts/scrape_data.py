import requests
from bs4 import BeautifulSoup
import csv
import os


def scrape_data(**kwargs):
    url = kwargs["url"]
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        all_data = []
        page_info = soup.find("p", text=lambda text: "Página" in text)
        if page_info:
            page_info_text = page_info.get_text()
            start_index = page_info_text.find("Página 1 de ") + len("Página 1 de ")
            end_index = page_info_text.find(",", start_index)
            total_pages = int(page_info_text[start_index:end_index])

            for current_page in range(1, total_pages + 1):
                page_url = f"{url}/index/page:{current_page}"
                response = requests.get(page_url)

                if response.status_code == 200:
                    html = response.text
                    soup = BeautifulSoup(html, "html.parser")
                    table = soup.find("table")

                    if table:
                        if current_page == 1:
                            header_row = table.find("tr")
                            if header_row:
                                column_names = [
                                    cell.get_text(strip=True)
                                    for cell in header_row.find_all("th")
                                ]
                                all_data.append(column_names)

                        data = []
                        for row in table.find_all("tr"):
                            cells = row.find_all("td")
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if any(row_data):
                                data.append(row_data)

                        all_data.extend(data)
                        print(f"Page {current_page} processed")
                    else:
                        print(f"No table found on page {current_page}")
                else:
                    print(f"Error in page {current_page}")
                    break

            # Save to a temporary CSV file
            temp_csv_path = "/tmp/inase_empresas.csv"
            with open(temp_csv_path, "w", newline="") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(all_data)

            # Push the file path to XCom
            kwargs["ti"].xcom_push(key="temp_csv_path", value=temp_csv_path)
        else:
            raise ValueError("Total pages not found.")
    else:
        raise ValueError("Error in the request")
