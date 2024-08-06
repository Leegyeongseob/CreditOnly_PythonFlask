import requests
from bs4 import BeautifulSoup

def get_hm_sale_items():
    urls = {
        'manPantsClothes': 'https://www2.hm.com/ko_kr/sale/shopbyproductmen/trousers.html',
        'manShoes': 'https://www2.hm.com/ko_kr/sale/shopbyproductmen/shoes.html',
        'manTopClothes': 'https://www2.hm.com/ko_kr/sale/shopbyproductmen/shirts.html',
        'womanButtomClothes': 'https://www2.hm.com/ko_kr/sale/shopbyproductladies/skirts.html',
        'womanOnepiece': 'https://www2.hm.com/ko_kr/sale/shopbyproductladies/dresses.html',
        'womanShoes': 'https://www2.hm.com/ko_kr/sale/shopbyproductladies/shoes.html',
        'womanTopClothes': 'https://www2.hm.com/ko_kr/sale/shopbyproductladies/shirtsblouses.html'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    all_products = {}

    for category, url in urls.items():
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"{category} 페이지 로드 성공")
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select(".section > ul > li")

            product_info_list = []

            for item in items:
                a_tag = item.select_one("article .image-container a")
                img_tag = item.select_one("article .image-container img")

                if a_tag and img_tag:
                    link = a_tag.get("href")
                    img_src = img_tag.get("data-src")

                    product_info = {
                        "link": link,
                        "img_src": img_src
                    }

                    product_info_list.append(product_info)

            all_products[category] = product_info_list
        else:
            print(f"{category} 페이지 로드 실패")

    return all_products

# 함수 호출 예시
sale_items = get_hm_sale_items()
print(sale_items)
