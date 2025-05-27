import streamlit as st
import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime
from pymongo import MongoClient

# Header User-Agent
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
}

# Koneksi MongoDB
client = MongoClient('mongodb+srv://bolaaa:bolaaa@bolaaaa.mqbmlkh.mongodb.net/?retryWrites=true&w=majority&appName=bolaaaa')
db = client['artikelbola']
collection = db['bolaaaa']

# Fungsi Scraper
def scrape_detik(jumlah_halaman):
    a = 1
    scraped_articles = []
    for page in range(1, jumlah_halaman + 1):
        url = f'https://www.detik.com/search/searchall?query=latihan+sepak+bola&page={page}'
        res = req.get(url, headers=headers)
        soup = bs(res.text, 'html.parser')
        articles = soup.find_all('article', class_='list-content__item')

        if not articles:
            st.warning(f"Halaman {page} tidak ditemukan atau kosong.")
            continue

        for article in articles:
            try:
                a_tag = article.find('h3', class_='media__title').find('a')
                if not a_tag or 'href' not in a_tag.attrs:
                    continue
                link = a_tag['href']
                title = a_tag.get_text(strip=True)

                date_tag = article.find('div', class_='media__date').find('span') if article.find('div', class_='media__date') else None
                date = date_tag['title'] if date_tag else 'Tanggal tidak ditemukan'

                try:
                    datetime.strptime(date, "%A, %d %b %Y %H:%M WIB")
                except:
                    st.warning(f"Format tanggal tidak valid: {date}")

                detail_page = req.get(link, headers=headers)
                detail_soup = bs(detail_page.text, 'html.parser')
                body = detail_soup.find_all('div', class_='detail__body-text itp_bodycontent')

                if not body:
                    continue

                content = ''
                for section in body:
                    paragraphs = section.find_all('p')
                    content += ''.join(p.get_text(strip=True) for p in paragraphs)

                content = content.replace('ADVERTISEMENT', '').replace('SCROLL TO RESUME CONTENT', '').replace('\n', '')

                article_data = {
                    'title': title,
                    'date': date,
                    'link': link,
                    'content': content
                }

                collection.insert_one(article_data)
                scraped_articles.append(article_data)

                st.success(f'done[{a}] > {title[:40]}...')
                a += 1

            except Exception as e:
                st.error(f"[Error] {e}")
    return scraped_articles

# Streamlit UI
st.title("Scraper Detik: Latihan Sepak Bola")
st.markdown("Masukkan jumlah halaman yang ingin discarping dari Detik.com")

jumlah_halaman = st.number_input("Jumlah Halaman", min_value=1, max_value=20, value=3, step=1)

if st.button("Mulai Scraping"):
    with st.spinner("Sedang mengambil data..."):
        results = scrape_detik(jumlah_halaman)
    st.success(f"Berhasil mengambil {len(results)} artikel.")
    for art in results:
        with st.expander(art['title']):
            st.write(f"**Tanggal:** {art['date']}")
            st.write(f"[Baca Artikel]({art['link']})")
            st.write(art['content'][:500] + "...")

#syauqi
#titit