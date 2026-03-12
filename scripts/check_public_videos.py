#!/usr/bin/env python3
"""Gate1 통과 영상 중 공개/멤버십 비율 샘플 체크"""
import yt_dlp, json, sys

with open('data/tmp/anyuhuatv_metadata.json', encoding='utf-8') as f:
    videos = json.load(f)

sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 20
sample = videos[:sample_size]
public_count = 0
member_count = 0
error_count = 0

ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}

print(f"샘플 {sample_size}개 체크 중...")
for i, v in enumerate(sample):
    vid_id = v['video_id']
    title = v['title'][:40]
    url = f"https://www.youtube.com/watch?v={vid_id}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        print(f"  [{i+1:02d}] PUBLIC:  {vid_id} - {title}")
        public_count += 1
    except Exception as e:
        err = str(e)
        if 'members' in err.lower() or 'member' in err.lower() or 'Join this channel' in err:
            print(f"  [{i+1:02d}] MEMBER:  {vid_id} - {title}")
            member_count += 1
        else:
            print(f"  [{i+1:02d}] ERROR:   {vid_id} - {err[:80]}")
            error_count += 1

total = len(videos)
print(f"\n=== 결과 ===")
print(f"샘플 {sample_size}개: 공개 {public_count}개 / 멤버십 {member_count}개 / 에러 {error_count}개")
member_ratio = member_count / sample_size
public_ratio = public_count / sample_size
print(f"멤버십 비율: {member_ratio:.0%} / 공개 비율: {public_ratio:.0%}")
print(f"전체 {total}개 기준 예상: 공개 ~{int(total * public_ratio)}개 / 멤버십 ~{int(total * member_ratio)}개")
