import json
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class VOSParser:
    def __init__(self):
        self.base_url = "https://vos.olimpiada.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    def get_page(self, url: str) -> BeautifulSoup | None:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return None

    def parse_subjects(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        subjects = []
        subjects_div = soup.find('div', class_='subjects')

        if subjects_div:
            for link in subjects_div.find_all('a'):
                subject = {
                    'name': link.get_text(strip=True),
                    'url': self.base_url + link.get('href', ''),
                    'code': link.get('href', '').split('/')[-1]
                }

                note = link.find('span', class_='s-note')
                if note:
                    subject['note'] = note.get_text(strip=True)
                    subject['name'] = subject['name'].replace(subject['note'], '').strip()

                subjects.append(subject)

        return subjects

    def parse_year_page_content(self, year: str, stage: str, subject: Optional[str] = None) -> dict | None:
        api_url = f"{self.base_url}/api/yearPage"

        payload = {
            'year': year,
            'psevdo': stage,
            'textField': 'ds2'
        }

        if subject:
            payload['sub'] = subject

        try:
            response = self.session.post(api_url, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при загрузке данных из API: {e}")
            return None

    def parse_school_stage(self, year: str = "2026") -> Dict:
        url = f"{self.base_url}/{year}/school"
        soup = self.get_page(url)

        if not soup:
            return {}

        result = {
            'url': url,
            'year': year,
            'stage': 'school',
            'title': '',
            'subjects': [],
            'menu_items': [],
            'partners': []
        }

        title = soup.find('title')
        if title:
            result['title'] = title.get_text(strip=True)

        result['subjects'] = self.parse_subjects(soup)

        school_menu = soup.find('div', class_='multilevel school-a')
        if school_menu:
            submenu = school_menu.find('div', class_='submenu')
            if submenu:
                for link in submenu.find_all('a'):
                    result['menu_items'].append({
                        'name': link.get_text(strip=True),
                        'url': self.base_url + link.get('href', '')
                    })

        partners_div = soup.find('div', class_='partners')
        if partners_div:
            for link in partners_div.find_all('a'):
                partner_url = link.get('href', '')
                img = link.find('img')
                if img:
                    result['partners'].append({
                        'url': partner_url,
                        'logo': self.base_url + img.get('src', '')
                    })

        return result

    def get_dynamic_content(self, year: str = "2026", stage: str = "school") -> Optional[Dict]:
        return self.parse_year_page_content(year, stage)


def main():
    parser = VOSParser()
    static_data = parser.parse_school_stage("2026")
    dynamic_data = parser.get_dynamic_content("2026", "school")


    print(f"\nTitle: {static_data['title']}")
    print(f"\nSubjects: {len(static_data['subjects'])}")

    print("\n")
    for subject in static_data['subjects'][:5]:
        print(f"  - {subject['name']} ({subject['code']})")
        if 'note' in subject:
            print(f"    {subject['note']}")

    output_file = "vos_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'static': static_data,
            'dynamic': dynamic_data
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
