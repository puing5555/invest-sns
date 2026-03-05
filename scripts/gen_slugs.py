# -*- coding: utf-8 -*-
"""Generate slug mappings for missing speakers"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Romanization mapping for Korean names
MAPPING = {
    '강동진': 'kang-dongjin',
    '강정수': 'kang-jungsu',
    '강하나': 'kang-hana',
    '거스 쿤': 'gus-kuhn',
    '권영화': 'kwon-younghwa',
    '김단테': 'kim-dante',
    '김대식': 'kim-daesik',
    '김도형': 'kim-dohyung',
    '김동환': 'kim-donghwan',
    '김민석': 'kim-minseok',
    '김수헌': 'kim-suheon',
    '김장년': 'kim-jangnyeon',
    '김탁': 'kim-tak',
    '김현지': 'kim-hyunji',
    '김효식': 'kim-hyosik',
    '맹성준': 'maeng-sungjun',
    '박성진': 'park-sungjin',
    '박세익': 'park-seik',
    '박형근': 'park-hyunggeun',
    '배경율': 'bae-kyungyul',
    '배상수': 'bae-sangsu',
    '백수전': 'baek-sujeon',
    '변우철': 'byun-woochul',
    '송종호': 'song-jongho',
    '슈카': 'syuka',
    '슈카월드': 'syuka-world',
    '신형관': 'shin-hyunggwan',
    '안유화': 'ahn-yuhwa',
    '안희철': 'ahn-heechul',
    '양희창': 'yang-heechang',
    '엄민용': 'um-minyong',
    '오종태': 'oh-jongtae',
    '오태민': 'oh-taemin',
    '올랜도 킴': 'orlando-kim',
    '윤수목': 'yoon-sumok',
    '이선엽': 'lee-sunyup',
    '이승우': 'lee-seungwoo',
    '이용재': 'lee-yongjae',
    '이장우': 'lee-jangwoo',
    '이형수': 'lee-hyungsu',
    '장민환': 'jang-minhwan',
    '정주용': 'jung-jooyong',
    '정지훈': 'jung-jihoon',
    '조봉수': 'cho-bongsu',
    '주기영': 'joo-kiyoung',
    '최도연': 'choi-doyeon',
    '최준': 'choi-jun',
    '한정수': 'han-jungsu',
    '홍선애': 'hong-sunae',
    '홍성철': 'hong-sungchul',
    '홍진채': 'hong-jinchae',
}

# Generate TypeScript entries
for name, slug in sorted(MAPPING.items()):
    print(f"  '{name}': '{slug}',")
