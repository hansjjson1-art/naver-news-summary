import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_naver_news(category=None):
    """네이버 뉴스 수집"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        if category:
            url = f'https://news.naver.com/section/{category}'
        else:
            url = 'https://news.naver.com/'

        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        news_items = []
        # 다양한 뉴스 제목 셀렉터 시도 (메인 페이지 및 섹션 페이지 대응)
        headlines = soup.select('a.news_tit, a.cjs_t, .sa_text_title, .sa_text_title strong, .sh_text_headline, .lnk_hdline_article, .cluster_text_headline, .sa_text_strong, .cnf_news_area strong, .cnf_news')

        for headline in headlines[:15]:
            title = headline.get_text(strip=True)
            link = headline.get('href', '')
            
            # 절대 경로가 아닌 경우 처리
            if link and not link.startswith('http'):
                if link.startswith('/'):
                    link = f"https://news.naver.com{link}"
                else:
                    link = f"https://news.naver.com/{link}"

            if title and link:
                news_items.append({
                    'title': title,
                    'link': link,
                    'collected_at': datetime.now().isoformat()
                })

        logger.info(f"수집된 뉴스: {len(news_items)}개")
        return news_items

    except Exception as e:
        logger.error(f"뉴스 수집 중 오류: {e}")
        return []


def get_top_categories():
    """가장 많이 나오는 기사 카테고리 2개 찾기"""
    categories = ['100', '101', '102', '103', '104', '105', '106']  # 정치, 경제, 사회, 스포츠, 연예, IT, 과학
    category_counts = {}

    for cat in categories:
        news = scrape_naver_news(cat)
        category_counts[cat] = len(news)
        logger.info(f"카테고리 {cat}: {len(news)}개")

    top_2 = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:2]
    return [cat[0] for cat in top_2]


def scrape_top_news(num_articles=10):
    """상위 2개 카테고리에서 뉴스 수집"""
    top_categories = get_top_categories()
    all_news = []

    for category in top_categories:
        news = scrape_naver_news(category)
        all_news.extend(news[:num_articles])

    return all_news


if __name__ == "__main__":
    news_list = scrape_top_news()
    for item in news_list:
        print(f"제목: {item['title']}")
        print(f"링크: {item['link']}")
        print("-" * 80)
