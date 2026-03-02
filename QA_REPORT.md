# QA 점검 리포트
**생성일시:** 2026-03-03 01:23 (Asia/Bangkok)
**프로젝트:** invest-sns
**총 시그널 수:** 142
**총 영상 수:** 163
**총 채널 수:** 7

---

## 1. key_quote 200자 초과 시그널
**심각도:** 🟡 Warning
**발견:** 2건

| ID | 종목 | 글자수 |
|---|---|---|
| 255c9bf9-198e-4448-86c5-5e6c89e17ae7 | 이더리움 (ETH) | 202 |
| dd12cfa5-94c3-46b8-8128-26663d0399a3 | 로켓랩 (RKLB) | 219 |

**제안:** key_quote를 200자 이내로 요약 또는 트리밍

## 2. ticker가 null인 시그널
**심각도:** 🔴 Critical
**발견:** 13건

| ID | 종목(stock) | signal |
|---|---|---|
| 78b3f927-0ecb-49a7-93df-2dea1ea4d630 | 테크 기업 | 매수 |
| bac042bc-8a78-4397-ab71-ba1755fc3d79 | 조선 | 긍정 |
| fee2af81-2e4b-4d1b-a31b-6c194e482b74 | 반도체 | 긍정 |
| 9aeda838-cd78-49c4-afe0-779fe6924305 | 바이오 AI 기업 | 긍정 |
| 0b1207d3-8144-4e27-b5b6-adad57709e27 | HM파마 | 중립 |
| 720aef52-2d6a-45f1-b8bd-b888a96813ae | 소프트웨어 섹터 | 경계 |
| f6d397de-1c5d-47f3-bf75-02abc2f3e8f4 | AI 인프라 섹터 | 긍정 |
| 9d79c0a4-7e2a-4852-b303-b24f05a980fd | 현대차그룹주 | 긍정 |
| 90524688-c8f2-4640-9614-61f79ec3ce58 | HCM파마 | 긍정 |
| 2d5d8a4b-a6e1-425a-98f5-8767a142193e | 로봇 섹터 | 경계 |
| 24b8baf3-82ea-4334-a98b-4eab6d0cdb70 | 마이크로스트라이즈 | 긍정 |
| 602d4f1a-7089-4b60-84a6-a905f355b1e4 | SpaceX | 중립 |
| e9aedc29-4f72-41dc-a12b-1cb6c7bdd687 | 금 | 긍정 |

**제안:** ticker 매핑 로직 점검. stock명으로 ticker 재매핑 필요

## 3. 같은 영상 내 유사 중복 시그널
**심각도:** 🟢 Info
**결과:** 없음 ✅

## 4. speaker_id별 시그널 수
**심각도:** 🟢 Info

| speaker_id | 시그널 수 |
|---|---|
| b9496a5f-06fa-47eb-bc2d-47060b095534 | 58 ⚠️ |
| b07d8758-493a-4a51-9bc5-7ef75f0be67c | 14 |
| 6b2696ff-f6a6-424b-a6de-0cd837f7bbb0 | 9 |
| 88892b60-9e6b-4390-ba3b-c6d1453b3cef | 8 |
| fcc56b05-159e-44a8-bc55-027a5904dadd | 7 |
| fcc6738d-49b6-48f0-9ec7-b20ec5594536 | 6 |
| e59ed6f5-7a8d-4111-af1c-502ad3344e79 | 6 |
| 8234cd75-1d0d-458c-b01c-62080c7d91e3 | 6 |
| d5ea4443-d1cb-4927-aabc-68061f59a3e0 | 5 |
| 3508abce-70e0-4eaa-a0d4-686b61071dd9 | 4 |
| d65055b9-1345-4baa-8104-b3d8c7f28d4c | 4 |
| 289de288-d587-4381-9f3d-b03ab63baf21 | 3 |
| 2720d0ee-b7e2-4006-80df-90bc9de07797 | 3 |
| a849fd03-6efa-4761-b176-175f1944bd5b | 2 |
| 5783838f-af5f-4e74-bcbf-bbc20141b199 | 2 |

**⚠️ 50건 초과 speaker:** 1명

## 5. stock 컬럼 이상값
**심각도:** 🟡 Warning
**발견:** 1건

| ID | stock | 사유 |
|---|---|---|
| e9aedc29-4f72-41dc-a12b-1cb6c7bdd687 | 금 | 의심 |

**제안:** 유효 종목명으로 교체 또는 삭제

## 6. signal 컬럼 이상값

**signal 분포:**

| signal | 건수 |
|---|---|
| 긍정 | 84 |
| 매수 | 35 |
| 중립 | 20 |
| 경계 | 3 |

**심각도:** 🟢 Info
**결과:** 모두 정상 ✅

## 7. mention_type 분포

| mention_type | 건수 |
|---|---|
| 결론 | 87 |
| 논거 | 36 |
| 보유 | 8 |
| 컨센서스 | 4 |
| 리포트 | 3 |
| 뉴스 | 3 |
| 티저 | 1 |


## 8. 날짜 이상 (created_at)
**심각도:** 🟢 Info
**결과:** 없음 ✅

## 9. 종목 페이지 vs DB ticker 비교
**DB ticker 수:** 50
**종목 페이지 수:** 52

**시그널은 있는데 페이지 없는 ticker:** 1개

- ^KOSPI

**페이지는 있는데 DB에 시그널 없는 ticker:** 3개
- 009540
- 086520
- 399720

## 10. stockPrices.json 빈 prices
**심각도:** 🟢 Info
**결과:** 없음 ✅

## 11. stockPrices.json 키 vs DB ticker 비교
**stockPrices 키 수:** 54
**DB ticker 수:** 50
**DB에 있지만 stockPrices에 없는 ticker:** 1개

- ^KOSPI

## 12. 라이브 사이트 접근 확인

| 페이지 | URL | 상태 |
|---|---|---|
| 메인 | https://puing5555.github.io/invest-sns/ | ✅ 200 (5352B) |
| index.html | https://puing5555.github.io/invest-sns/index.html | ✅ 200 (5352B) |
| 종목:000660 | https://puing5555.github.io/invest-sns/stock/000660.html | ✅ 200 (6714B) |
| 종목:000720 | https://puing5555.github.io/invest-sns/stock/000720.html | ✅ 200 (6714B) |

## 13. signal_prices.json 구조 점검
**총 키 수:** 258
**UUID 키 발견:** 207개
- 42645e3c-79c2-4d42-9efe-50944e8a0cd2
- d8cd1b3e-7d71-4f96-b094-8441b3be64c1
- 98a8dfa2-ca7f-4199-a1e1-b4290d9b4a4e
- 66e79a97-3a96-449f-80cc-63e03c01ee7c
- 43700fd4-9b1d-41a7-b3a5-3a79a809d26e
- 9482809c-febc-4e93-b84b-2b057486bdb1
- be0669e3-c3b2-4f6e-bc18-c9bb63149997
- f39c6d56-72d3-4a5b-bdcd-6ad495a323a0
- 1ae017a5-c302-48ea-be69-ed769d2e82a5
- 4e036638-2081-4913-9aac-303c9770ae7f

## 14. video_id 고아 시그널 (influencer_videos에 없음)
**심각도:** 🔴 Critical
**발견:** 142건

| signal ID | video_id | stock |
|---|---|---|
| 8e42adce-5630-4b8a-9e38-1137df6b4173 | 98a76d69-6bb2-4d93-8168-4b063da57812 | 아모레퍼시픽 (090430) |
| f5a73453-15dc-4cb5-bd0e-1da5eea7fb23 | 98a76d69-6bb2-4d93-8168-4b063da57812 | 현대차 (005380) |
| 9c83cb42-6d31-4a9a-9b1c-5a85c125b84d | cef2c937-db77-4bf6-9173-2e3fd8533334 | SK하이닉스 (000660) |
| 0f3c3f27-ddb4-4dec-a16d-7f28163db5f1 | 1a47ae36-c840-4831-9ece-ec88ba5fc7ec | 삼성전자 (005930) |
| 7ba0f471-6950-4436-8e8f-2ee5989748ce | d68ab7a3-4772-49fe-86f2-eead4f4d1887 | 삼성전자 (005930) |
| c5ddfab8-d29f-428c-aaab-568aff7db603 | 9286ef9e-12ac-44d0-8e85-2e32b44e7fc1 | SK하이닉스 (000660) |
| dc359487-49ef-42ce-ba2c-297b1587e743 | b27de8b4-9bf8-451e-a281-6064e61ce46e | CGV (079160) |
| b97347cb-f51c-4180-9717-e11ebc8cccef | 93c60878-e2d3-4bc2-bcd2-4d32d0a3bd2c | 현대건설 (000720) |
| c9d04f21-5570-4d15-b01f-0d8d06412b7b | ffc64461-4859-4f38-898e-519b6ecaf2b2 | 삼성전자 (005930) |
| 414a3173-afac-46b8-af46-48615d2293e6 | ffc64461-4859-4f38-898e-519b6ecaf2b2 | SK하이닉스 (000660) |
| 78b3f927-0ecb-49a7-93df-2dea1ea4d630 | fa9707b6-1383-4ce3-ab15-45314d23a135 | 테크 기업 |
| bac042bc-8a78-4397-ab71-ba1755fc3d79 | cfc9e60f-5bae-45c5-8e57-8f624f79298c | 조선 |
| fee2af81-2e4b-4d1b-a31b-6c194e482b74 | 94ff3a67-01d6-49da-89ff-d461a810774c | 반도체 |
| fc445820-5853-4152-bca2-db6eacb10003 | 94ff3a67-01d6-49da-89ff-d461a810774c | SK하이닉스 (000660) |
| 85e74359-3b1f-4694-b9f5-09b8d303659d | ffc64461-4859-4f38-898e-519b6ecaf2b2 | 원익IPS (240810) |
| 11e95a7f-a408-4a9a-9072-f1b238db28e5 | ffc64461-4859-4f38-898e-519b6ecaf2b2 | 주성엔지니어링 (036930) |
| 2bb7d896-a03c-4413-ac3e-9717c59b9090 | ffc64461-4859-4f38-898e-519b6ecaf2b2 | 한미반도체 (042700) |
| 4ed7b3c7-e152-4011-85f9-88d7eb331dd6 | ffc64461-4859-4f38-898e-519b6ecaf2b2 | HPSP (403870) |
| 2244a98d-2de6-40a7-bd0a-8f0104126e5e | cfc9e60f-5bae-45c5-8e57-8f624f79298c | 효성중공업 (298040) |
| e1d58ec7-3ca7-4db9-9a77-d63cf1c06e89 | ffc64461-4859-4f38-898e-519b6ecaf2b2 | SOXX (SOXX) |
| ... | 외 122건 | |

**제안:** 누락된 video 레코드 추가 또는 고아 시그널 정리

## 15. speaker_id 고아 시그널
**심각도:** 🟢 Info
**결과:** 없음 ✅

## 16. review_status 분포

| review_status | 건수 | 비율 |
|---|---|---|
| pending | 142 | 100.0% |


## 17. 같은 stock, 다른 ticker
**심각도:** 🟢 Info
**결과:** 없음 ✅

---

## 📊 종합 요약

| 심각도 | 항목 수 |
|---|---|
| 🔴 Critical | 2 |
| 🟡 Warning | 6 |
| 🟢 정상 | 9 |

### 항목별 결과

| 항목 | 문제 수 | 심각도 |
|---|---|---|
| 1. key_quote 초과 | 2 | 🟡 Warning |
| 2. ticker null | 13 | 🔴 Critical |
| 3. 중복 시그널 | 0 | 🟢 Info |
| 4. speaker 비정상 | 1 | 🟡 Warning |
| 5. stock 이상값 | 1 | 🟡 Warning |
| 6. signal 이상값 | 0 | 🟢 Info |
| 7. mention_type | 0 | 🟢 Info |
| 8. 날짜 이상 | 0 | 🟢 Info |
| 9. 페이지 누락 | 1 | 🟡 Warning |
| 10. 빈 prices | 0 | 🟢 Info |
| 11. stockPrices 누락 | 1 | 🟡 Warning |
| 12. 라이브 사이트 | 0 | 🟢 Info |
| 13. UUID 키 | 207 | 🟡 Warning |
| 14. 고아 video_id | 142 | 🔴 Critical |
| 15. 고아 speaker_id | 0 | 🟢 Info |
| 16. review_status | 0 | 🟢 Info |
| 17. stock-ticker 불일치 | 0 | 🟢 Info |

⚠️ **Critical 이슈가 2건 있습니다. 우선 수정이 필요합니다.**
📋 **Warning 6건은 데이터 품질 향상을 위해 검토가 권장됩니다.**