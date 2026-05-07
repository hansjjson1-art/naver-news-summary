from google import genai
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def summarize_news(news_items):
    """Google Gemini를 사용하여 뉴스 요약"""
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    if not api_key:
        logger.error("GOOGLE_GEMINI_API_KEY 환경변수가 설정되지 않았습니다")
        return None

    client = genai.Client(api_key=api_key)
    
    news_text = "\n\n".join([f"제목: {item['title']}\n링크: {item['link']}" for item in news_items])

    prompt = f"""다음은 오늘의 뉴스 헤드라인들입니다.
각 뉴스를 한 문장으로 요약하고, 전체 뉴스의 주요 내용을 3-5줄로 요약해주세요.

뉴스:
{news_text}

형식:
[개별 뉴스 요약]
1. 제목1 - 요약문
2. 제목2 - 요약문
...

[전체 요약]
오늘의 주요 뉴스 내용을 3-5줄로 정리
"""

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        summary = response.text
        logger.info("뉴스 요약 완료")
        return summary
    except Exception as e:
        logger.error(f"뉴스 요약 중 오류: {e}")
        return None


def format_summary_with_links(news_items, summary):
    """뉴스 링크를 포함한 형식으로 요약 정리"""
    formatted = f"📰 오늘의 뉴스 요약\n{'='*50}\n\n"
    formatted += summary
    formatted += f"\n\n{'='*50}\n📌 뉴스 링크:\n"

    for i, item in enumerate(news_items, 1):
        formatted += f"{i}. {item['title']}\n   🔗 {item['link']}\n"

    return formatted


if __name__ == "__main__":
    from news_scraper import scrape_top_news

    news_list = scrape_top_news()
    summary = summarize_news(news_list)
    if summary:
        formatted = format_summary_with_links(news_list, summary)
        print(formatted)
