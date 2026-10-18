#!/usr/bin/env python3
"""
Парсер для сайта vos.olimpiada.ru
Извлекает информацию о школьном этапе олимпиады
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional


class VOSParser:
    """Парсер для vos.olimpiada.ru"""

    def __init__(self):
        self.base_url = "https://vos.olimpiada.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Получить и распарсить страницу"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return None

    def parse_subjects(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Извлечь список предметов"""
        subjects = []
        subjects_div = soup.find('div', class_='subjects')

        if subjects_div:
            for link in subjects_div.find_all('a'):
                subject = {
                    'name': link.get_text(strip=True),
                    'url': self.base_url + link.get('href', ''),
                    'code': link.get('href', '').split('/')[-1]
                }

                # Обработка подзаголовков (например, "в рамках предмета «Информатика»")
                note = link.find('span', class_='s-note')
                if note:
                    subject['note'] = note.get_text(strip=True)
                    subject['name'] = subject['name'].replace(subject['note'], '').strip()

                subjects.append(subject)

        return subjects

    def parse_year_page_content(self, year: str, stage: str, subject: Optional[str] = None) -> Optional[Dict]:
        """
        Получить динамический контент через API

        Args:
            year: Год олимпиады (например, "2026")
            stage: Этап (например, "school", "okrug", "region")
            subject: Код предмета (опционально)
        """
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
        """Парсинг страницы школьного этапа"""
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

        # Заголовок
        title = soup.find('title')
        if title:
            result['title'] = title.get_text(strip=True)

        # Предметы
        result['subjects'] = self.parse_subjects(soup)

        # Пункты меню "Школам"
        school_menu = soup.find('div', class_='multilevel school-a')
        if school_menu:
            submenu = school_menu.find('div', class_='submenu')
            if submenu:
                for link in submenu.find_all('a'):
                    result['menu_items'].append({
                        'name': link.get_text(strip=True),
                        'url': self.base_url + link.get('href', '')
                    })

        # Партнеры
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
        """Получить динамический контент страницы"""
        return self.parse_year_page_content(year, stage)


def main():
    """Основная функция"""
    parser = VOSParser()

    print("=== Парсинг страницы школьного этапа ВОШ ===\n")

    # Парсинг статического контента
    print("Загрузка статического контента...")
    static_data = parser.parse_school_stage("2026")

    print(f"\nЗаголовок: {static_data['title']}")
    print(f"\nНайдено предметов: {len(static_data['subjects'])}")

    print("\nПредметы:")
    for subject in static_data['subjects'][:5]:  # Первые 5 для примера
        print(f"  - {subject['name']} ({subject['code']})")
        if 'note' in subject:
            print(f"    {subject['note']}")

    print(f"\n... и еще {len(static_data['subjects']) - 5} предметов")

    print("\nПункты меню:")
    for item in static_data['menu_items']:
        print(f"  - {item['name']}: {item['url']}")

    # Попытка получить динамический контент
    print("\n\nЗагрузка динамического контента через API...")
    dynamic_data = parser.get_dynamic_content("2026", "school")

    if dynamic_data and 'data' in dynamic_data:
        data = dynamic_data['data']
        print(f"\nНазвание: {data.get('name', 'N/A')}")

        if 'text' in data and data['text']:
            print(f"Контент загружен ({len(data['text'])} символов)")
            # Парсинг HTML контента
            content_soup = BeautifulSoup(data['text'], 'html.parser')
            text_preview = content_soup.get_text(strip=True)[:200]
            print(f"Начало текста: {text_preview}...")

        if 'years' in data:
            print(f"\nДоступные годы: {', '.join([y['name'] for y in data['years']])}")

    # Сохранение результатов
    output_file = "vos_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'static': static_data,
            'dynamic': dynamic_data
        }, f, ensure_ascii=False, indent=2)

    print(f"\n\nДанные сохранены в {output_file}")


if __name__ == "__main__":
    main()
