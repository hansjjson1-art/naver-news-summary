"""
네이버 뉴스(정치/경제) Gemini 요약 및 디스코드 전송 프로그램
"""

import sys
import logging
import requests
from datetime import datetime
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def summarize_with_gemini(news_content, category_name):
    """Gemini 모델로 특정 카테고리 뉴스 요약"""
    try:
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            logger.error("GOOGLE_GEMINI_API_KEY 환경변수가 설정되지 않았습니다")
            return None

        client = genai.Client(api_key=api_key)

        prompt = f"""다음은 네이버 뉴스의 {category_name} 섹션 헤드라인입니다.
이 뉴스들을 분석하고 주요 내용을 요약해주세요.

{news_content}

요약 형식:
1. 주요 {category_name} 뉴스 요약 (3-5개)
2. 종합적인 오늘의 {category_name} 트렌드 및 시사점 (3-5줄)"""

        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        logger.info(f"✅ Gemini {category_name} 요약 완료")
        return response.text

    except Exception as e:
        logger.error(f"Gemini 요약 중 오류: {e}")
        return None


def send_to_single_webhook(webhook_url, title, content):
    """단일 디스코드 웹훅에 전송"""
    if not webhook_url:
        logger.error("웹훅 URL이 설정되지 않았습니다")
        return False

    payload = {
        "embeds": [
            {
                "title": title,
                "description": content[:4000],
                "color": 0x3498db if "정치" in title else 0xe74c3c
            }
        ]
    }

    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        return r.status_code == 204
    except Exception as e:
        logger.error(f"디스코드 전송 중 오류: {e}")
        return False


def run_news_summary():
    """뉴스 요약 및 디스코드 전송 실행"""

    logger.info("=" * 80)
    logger.info("Gemini를 이용한 뉴스 요약 시작")
    logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    # 1. 네이버 뉴스 수집 (정치: 100, 경제: 101)
    logger.info("1단계: 네이버 뉴스 정치(100) 및 경제(101) 뉴스 수집 중...")

    from news_scraper import scrape_naver_news

    politics_news = scrape_naver_news('100')
    economy_news = scrape_naver_news('101')

    if not politics_news and not economy_news:
        logger.error("뉴스 수집 실패")
        return False

    # 2. Gemini로 각각 요약
    logger.info("2단계: 정치 및 경제 뉴스 각각 요약 중...")

    politics_content = "정치 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in politics_news[:10]])
    economy_content = "경제 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in economy_news[:10]])

    politics_summary = summarize_with_gemini(politics_content, "정치")
    economy_summary = summarize_with_gemini(economy_content, "경제")

    if not politics_summary and not economy_summary:
        logger.error("뉴스 요약에 모두 실패했습니다")
        return False

    # 3. 디스코드 전송
    logger.info("3단계: 디스코드 웹훅별 전송 중...")

    if politics_summary:
        ok = send_to_single_webhook(os.getenv('DISCORD_WEBHOOK_1'), "⚖️ 오늘의 정치 뉴스 요약", politics_summary)
        if ok:
            logger.info("✅ 정치 뉴스 전송 완료 (웹훅 1)")

    if economy_summary:
        ok = send_to_single_webhook(os.getenv('DISCORD_WEBHOOK_2'), "💰 오늘의 경제 뉴스 요약", economy_summary)
        if ok:
            logger.info("✅ 경제 뉴스 전송 완료 (웹훅 2)")

    logger.info("=" * 80)
    logger.info("모든 작업 완료!")
    logger.info("=" * 80)

    return True


if __name__ == "__main__":
    success = run_news_summary()
    sys.exit(0 if success else 1)
