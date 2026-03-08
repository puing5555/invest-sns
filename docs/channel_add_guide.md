# 파이프라인 신규 채널 추가 가이드

이 문서는 `influencer_channels` 테이블에 새 YouTube 채널을 추가할 때 따라야 할 규칙과 절차를 정리합니다.

---

## 채널명 규칙

- **channel_name**: YouTube 실제 채널명 사용 (핸들 @xxx 사용 금지)
- **확인 방법**: `yt-dlp --print channel URL` 또는 YouTube About 페이지
- **channel_handle**: @xxx 형식 유지 (변경 없음)

### 예시

```
# 올바른 예
channel_name = "Godofit"
channel_handle = "@GODofIT"

# 잘못된 예
channel_name = "@GODofIT"  ← 핸들을 채널명으로 쓰면 안 됨
```

### yt-dlp로 채널명 확인하기

```bash
python -m yt_dlp --print "%(channel)s" --no-download "https://www.youtube.com/@GODofIT"
```

---

## DB 등록 절차

1. YouTube 채널 URL 확보
2. yt-dlp로 `channel` (실제 채널명) 및 `channel_id` 확인
3. `influencer_channels` 테이블에 INSERT
4. 비디오 크롤링 실행 (`video_id`, `published_at` 수집)
5. 비디오 제목은 YouTube ID가 아닌 실제 제목으로 저장 (yt-dlp `%(title)s` 사용)

---

## 비디오 제목 저장 규칙

- `title` 컬럼: 반드시 실제 YouTube 영상 제목 저장
- YouTube ID(예: `Ceuu9plkhUY`)를 title로 저장하지 말 것
- 수집 시 yt-dlp 명령어:

```bash
python -m yt_dlp --print "%(title)s" --no-download "https://www.youtube.com/watch?v={video_id}"
```

---

## 주의사항

- service role key를 사용해야 PATCH/INSERT 가능 (anon key는 읽기만)
- yt-dlp 요청 간 2초 딜레이 필수 (YouTube 차단 방지)
- 20개마다 5초 추가 대기
- 실패한 video_id는 `failed_title_updates.txt`에 별도 기록
