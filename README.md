# 📰 네이버 뉴스 자동 요약 및 전송 시스템 (Main)

이 프로그램은 네이버 뉴스의 **정치(100)** 및 **경제(101)** 섹션을 자동으로 수집하여 Google Gemini로 요약하고, 카카오톡과 디스코드에 전송합니다.

## 🚀 주요 기능
- **섹션별 수집**: 정치(100), 경제(101) 뉴스 각각 10개씩 수집
- **Gemini 요약**: 각 섹션의 핵심 내용을 독립적으로 요약 분석
- **디스코드 전송**: 
  - 웹훅 1번: 정치 뉴스 요약 전송
  - 웹훅 2번: 경제 뉴스 요약 전송
- **카카오톡 전송**: Claude Code Play MCP(`KakaotalkChat-MemoChat`)를 통해 나에게 보내기
  - Python 스크립트는 전송할 메시지를 `kakao_pending.json`에 저장
  - Claude가 해당 파일을 읽어 MCP로 실제 전송 (200자 초과 시 자동 분할)

## 🛠️ 설정 및 실행

### 1. 환경 변수 (.env)
루트 디렉토리의 `.env` 파일에 다음 정보를 설정하세요.
```env
GOOGLE_GEMINI_API_KEY=your_key
DISCORD_WEBHOOK_1=politics_url
DISCORD_WEBHOOK_2=economy_url
```

### 2. 실행 방법

```bash
python main.py                    # 디스코드 + 카카오톡 전송
python main.py --discord-only     # 디스코드만 전송
python main.py --kakao-only       # 카카오톡 메시지 준비 (kakao_pending.json 저장)
python main.py --preview          # 미리보기 (전송 안함)
```

> ⚠️ **카카오톡 전송은 Claude Code에서 실행해야 합니다.**  
> `--kakao-only` 실행 후 생성된 `kakao_pending.json`을 Claude가 읽어 Play MCP로 전송합니다.  
> Claude에게 "뉴스 카카오로 보내줘"라고 하면 두 단계를 자동으로 처리합니다.

## 📁 파일 구성
- `main.py`: 전체 프로세스 제어
- `news_scraper.py`: 네이버 뉴스 수집 로직
- `news_summarizer.py`: Gemini 요약 로직
- `kakao_sender.py`: 메시지 분할 및 `kakao_pending.json` 저장
- `discord_sender.py`: 디스코드 전송 모듈
- `kakao_pending.json`: 카카오톡 전송 대기 메시지 (Claude MCP가 소비)
