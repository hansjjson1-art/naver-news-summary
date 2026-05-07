import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_discord_webhook(webhook_url, message, title="📰 오늘의 뉴스 요약"):
    """디스코드 웹훅을 통해 메시지 전송"""
    try:
        # 디스코드 Embed 형식
        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": message[:4000],  # Discord 제한
                    "color": 0x3498db
                }
            ]
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 204:
            logger.info("디스코드 웹훅 전송 성공")
            return True
        else:
            logger.error(f"디스코드 웹훅 전송 실패: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"디스코드 웹훅 전송 중 오류: {e}")
        return False


def send_to_discord_channels(news_items, summary):
    """두 개의 디스코드 채널에 뉴스 전송"""
    webhook_1 = os.getenv('DISCORD_WEBHOOK_1')
    webhook_2 = os.getenv('DISCORD_WEBHOOK_2')

    if not webhook_1 or not webhook_2:
        logger.error("DISCORD_WEBHOOK_1 또는 DISCORD_WEBHOOK_2 환경변수가 설정되지 않았습니다")
        return False

    # 디스코드 전송용 메시지 포맷
    message = _format_discord_message(news_items, summary)

    # 첫 번째 채널 전송
    result1 = send_discord_webhook(webhook_1, message, "📰 오늘의 뉴스 요약 - 채널 1")
    # 두 번째 채널 전송
    result2 = send_discord_webhook(webhook_2, message, "📰 오늘의 뉴스 요약 - 채널 2")

    return result1 and result2


def _format_discord_message(news_items, summary):
    """디스코드 메시지 포맷"""
    message = f"**[뉴스 요약]**\n{summary}\n\n"
    message += "**[주요 뉴스]**\n"

    for i, item in enumerate(news_items[:10], 1):
        title = item['title'][:60]  # 제목 길이 제한
        link = item['link']
        message += f"{i}. [{title}]({link})\n"

    return message


if __name__ == "__main__":
    from news_scraper import scrape_top_news
    from news_summarizer import summarize_news

    news_list = scrape_top_news()
    summary = summarize_news(news_list)

    if summary:
        result = send_to_discord_channels(news_list, summary)
        if result:
            print("✅ 디스코드 전송 완료")
        else:
            print("❌ 디스코드 전송 실패")
