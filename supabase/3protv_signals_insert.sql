-- 삼프로TV 시그널 데이터 INSERT 문
-- 생성일: 2026-02-27 14:36:27


-- 채널 데이터 삽입
INSERT INTO public.influencer_channels (id, channel_name, channel_url, platform, subscriber_count, description, created_at)
VALUES ('ac3b3ee5-6331-4953-acda-758bf412ea24', '삼프로TV', 'https://www.youtube.com/@3protv', 
        'youtube', 500000, '삼성증권 프로 투자 전문 채널', 
        '2026-02-27T07:36:27.195863+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('e21d66ba-d1b1-4edf-b074-43a45d8c1548', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_1', '이재규 투자 전략 분석', 
        '2026-02-27T07:36:27.195878+00:00', 600, True, 
        '2026-02-27T07:36:27.195882+00:00', '3protv_v7', '2026-02-27T07:36:27.195884+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('b21af275-502d-4d4c-b2c0-7ffce9b4e933', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_2', '박명성 투자 전략 분석', 
        '2026-02-27T07:36:27.195892+00:00', 600, True, 
        '2026-02-27T07:36:27.195895+00:00', '3protv_v7', '2026-02-27T07:36:27.195897+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('f5d909e2-797a-4cea-8530-e96ce3927bb9', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_3', '김동훈 투자 전략 분석', 
        '2026-02-27T07:36:27.195903+00:00', 600, True, 
        '2026-02-27T07:36:27.195906+00:00', '3protv_v7', '2026-02-27T07:36:27.195908+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('1025c530-b7fc-43fa-bf1a-5d86bd5e3016', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_4', '박명석 투자 전략 분석', 
        '2026-02-27T07:36:27.195913+00:00', 600, True, 
        '2026-02-27T07:36:27.195916+00:00', '3protv_v7', '2026-02-27T07:36:27.195918+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('9b94f69c-58ec-4049-82d7-c78e696b15e8', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_5', '김장열 투자 전략 분석', 
        '2026-02-27T07:36:27.195923+00:00', 600, True, 
        '2026-02-27T07:36:27.195926+00:00', '3protv_v7', '2026-02-27T07:36:27.195928+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('c952b654-8cf8-4ad7-aab8-a190dececefc', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_6', '배재원 투자 전략 분석', 
        '2026-02-27T07:36:27.195933+00:00', 600, True, 
        '2026-02-27T07:36:27.195936+00:00', '3protv_v7', '2026-02-27T07:36:27.195938+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('480abb0d-cf0c-46f6-97e6-72fa89c7271e', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_7', '차영주 투자 전략 분석', 
        '2026-02-27T07:36:27.195942+00:00', 600, True, 
        '2026-02-27T07:36:27.195945+00:00', '3protv_v7', '2026-02-27T07:36:27.195947+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('8d953a99-d91c-4a0a-b96e-a6d9ee222e23', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_8', '장우진 투자 전략 분석', 
        '2026-02-27T07:36:27.195953+00:00', 600, True, 
        '2026-02-27T07:36:27.195956+00:00', '3protv_v7', '2026-02-27T07:36:27.195958+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('1e2b361f-3620-46f4-aa2c-7a365ea21d4e', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_9', '박지훈 투자 전략 분석', 
        '2026-02-27T07:36:27.195963+00:00', 600, True, 
        '2026-02-27T07:36:27.195966+00:00', '3protv_v7', '2026-02-27T07:36:27.195968+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('e771da52-8ccd-4100-9421-8c7e971d87a1', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_10', '박병창 투자 전략 분석', 
        '2026-02-27T07:36:27.195974+00:00', 600, True, 
        '2026-02-27T07:36:27.195977+00:00', '3protv_v7', '2026-02-27T07:36:27.195979+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('8343a00b-8c52-4cd1-9507-abb62175fa08', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_11', '박현지 투자 전략 분석', 
        '2026-02-27T07:36:27.195984+00:00', 600, True, 
        '2026-02-27T07:36:27.195986+00:00', '3protv_v7', '2026-02-27T07:36:27.195988+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('1d0b8f7a-4089-4202-aa9a-2af819361e0c', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_12', '이권희 투자 전략 분석', 
        '2026-02-27T07:36:27.195993+00:00', 600, True, 
        '2026-02-27T07:36:27.195995+00:00', '3protv_v7', '2026-02-27T07:36:27.195998+00:00');


INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('2e05c4db-ffeb-4972-a261-966f290fa731', 'ac3b3ee5-6331-4953-acda-758bf412ea24', '3protv_mock_13', '고연수 투자 전략 분석', 
        '2026-02-27T07:36:27.196002+00:00', 600, True, 
        '2026-02-27T07:36:27.196005+00:00', '3protv_v7', '2026-02-27T07:36:27.196007+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('aa8afa3b-ba11-4d3e-87da-c8ca5e3c2ce0', '8e77f9cf-afb1-40a4-aeb2-d21bb379e8ac', '고연수', '증권주전체', 
        'NULL', 'SECTOR', 'investment', 'STRONG_BUY', 
        'high', '06:12', '"증권주는 거의 다 편하게 가져가도 된다. 무조건 지금보다는 수익률이 더 나을 수 있다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195374+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('292ae237-836b-44c8-8dda-5fafe0d3d07f', 'e80338aa-a277-4658-af91-b47be0694c02', '배재원', '삼성전자', 
        '005930', 'KR', 'investment', 'STRONG_BUY', 
        'high', '06:10', '"영업이익 추정치가 계속 상향되고 있는데 매도할 이유가 없다. 지금이라도 들어가야 된다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195402+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('5f873fa8-abc0-4f8d-89aa-fdb01c024caa', '694b2d3b-9fac-45ba-b8d1-395f587793af', '배재원', 'SK하이닉스', 
        '000660', 'KR', 'investment', 'STRONG_BUY', 
        'high', '07:13', '"목표주가가 계속 높아지고 있는 상황에서 매수하지 않을 이유가 뭔지 오히려 궁금하다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195416+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('12c6178d-2197-4983-8256-f07892fbacba', 'a8c34095-211f-4442-8aa8-ff97106947f1', '배재원', '코스피', 
        'KOSPI', 'UNKNOWN', 'investment', 'STRONG_BUY', 
        'high', '06:10', '"상반기에 정말 7,000포인트라는 더 역사적인 순간도 볼 수 있지 않을까"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195430+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('084fbc13-ecdc-44da-8821-e1c170665f54', '1113a1ce-4abe-464c-a8ac-b9070da0ad05', '박명성', '서클', 
        'CIRCLE', 'US', 'investment', 'STRONG_BUY', 
        'high', '38:08', '"서클 주가가 30% 넘게 급등했고 USDC 순환량이 전년 대비 72% 급증. 스테이블코인 인프라가 계속 구축되고 있어"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195441+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('cc53c80f-03fb-4fa6-b7a8-40fec583dca3', 'b858952f-e65f-4dd7-aa4a-5875524e9139', '박명성', '엔비디아', 
        'NVDA', 'US', 'investment', 'BUY', 
        'high', '[08:17]', '"5% 급락은 과도해. 실적 완벽했고 기술주가 필수소비재보다 저평가. 없는 분들에게 기회"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195453+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('3683110e-cb63-4ac3-a7f5-3067bf7a2631', '445f6c44-b162-4a43-9af9-4f99632e5931', '차영주', 'LG이노텍', 
        'NULL', 'UNKNOWN', 'investment', 'BUY', 
        'high', '01:02', '교보증권 목표주가 37만원 상향, 로봇산업 진출과 카메라모듈 기술 확장으로 매출 성장 기대', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195465+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('7c325a4d-3b2b-48af-839f-4d7c1b1cd346', '03f4ddc2-120d-4c16-a4cc-f9a3342a03e7', '김장열', '삼성전자', 
        '005930', 'KR', 'investment', 'BUY', 
        'high', '17:24', '메코리 목표주가 33만원, 향후 3-4개월간 업사이드 존재하며 배당 상향 기대감도 긍정적', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195475+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('b41da2bd-0231-4abd-abaa-14b42fbba358', 'ccb13fce-c69b-47ec-a674-e2e5a2f61283', '김장열', 'SK하이닉스', 
        '000660', 'KR', 'investment', 'BUY', 
        'high', '21:28', '270조 이익 전망에도 불구 밸류에이션 디스카운트, 중국 공장 업그레이드 제약이 리스크 요인', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195484+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('3b75f18b-2b59-4f52-a272-43eb2e8eb1b2', '69f63771-b378-4e26-815b-e09779156974', '박명석', '삼성전자', 
        '005930', 'KR', 'investment', 'BUY', 
        'high', '08:13', '"2027년 포워드 PER로 계산해도 3-4배밖에 안 되기 때문에 지금 삼성전자는 계속 가도 전혀 이상하지 않다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195496+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('9af8be4b-5867-4b3e-886e-4dc07a4d1574', '255a8cd0-ce5d-4829-8a56-63d68aa954bf', '이재규', 'SK하이닉스', 
        '000660', 'KR', 'investment', 'BUY', 
        'high', '14:27', '"대형주들의 장세가 좀 더 이어질 가능성이 높고, 7,000포인트까지 열려 있다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195505+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('4b914a87-aab9-49f8-9f08-9094b0c790e1', '8a85be91-d9fa-4c85-a70d-40dd36e0d5f0', '박병창', '삼성전자', 
        '005930', 'KR', 'investment', 'BUY', 
        'high', '13:19', '"결론은 삼성전자 SK하이닉스의 이익이 증가하는 걸 계산해 가지고 지수가 올라간다... 이번 상승에서 이 수익률을 쫓아가려면 삼성전자 SK하이닉스를 가지고 있어야 되는 거고"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195515+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('506cc863-c4b3-45ab-8011-efa546db7901', '4a56de82-eba6-44f2-b4f9-ed2cf29cc8c9', '김장열', '삼성전자', 
        '005930', 'KR', 'investment', 'BUY', 
        'high', '13:17', '"우선순위는... 메모리죠... 삼성전자나 SK하이닉스가 오늘 본장에서... 빠질 이유가 없죠... 대기하고 있는 사람이 너무 많아요"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195526+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('3f1ee5dc-d36c-4ac6-aff5-a2f76fc43de1', '093d97da-9cf4-4d11-ab12-c6a82994b96d', '차영주', '기아', 
        'NULL', 'UNKNOWN', 'investment', 'BUY', 
        'high', '16:30', '"목표주가 27만원으로 17% 상향. 미국에서 하이브리드 현지생산과 배당 4% 모멘텀"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195537+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('efc59332-3312-49ac-8ccf-2cc923193cce', 'e4ed243f-be9e-49fe-89e8-f3cf7bc3c135', '차영주', '한국전력', 
        'NULL', 'UNKNOWN', 'investment', 'BUY', 
        'high', '39:10', '"해외 원전사업 가치로 목표주가 8만원. 배당수익률 5.7% 기대"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195548+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('e467269c-bb78-4269-aa8e-d1670074b3be', '0abcc130-039e-46ba-b1d4-8c93b5bc3a52', '이재규', '현대차', 
        '005380', 'KR', 'investment', 'BUY', 
        'high', '18:30', '"로봇 밸류와 자율주행 모멘텀 부각. 테슬라 PER 280배 대비 현대차는 상승 밸류 남아있다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195557+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('6ad3e62e-f3eb-4286-9db8-8ccc14ae99ae', '6f8ee22e-91d9-4200-9fb7-c9ae00b76ef0', '장우진', '구글(알파벳)', 
        'NULL', 'UNKNOWN', 'investment', 'BUY', 
        'high', '26:45', '"노트북LM, 뮤직 등으로 오픈AI 추격하며 확실한 1등. 데이터 자산으로 앞서나가고 있다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195567+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('bb6ccddd-e9eb-46ef-adfa-d2a41df8c9a8', '9a803860-9939-4f57-80b4-15b50b05f3a5', '김동훈', '신세계', 
        'NULL', 'KR', 'investment', 'BUY', 
        'high', '08:15', '"신세계를 저는 좋게 보고 있거든요... 외국인은 지금 주가에서도 여전히 순매수 상태입니다... 추가 상승 여력이 있다라고 배팅을 한 거로 보여지거든요"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195578+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('3ebcc959-33a5-41cb-9d47-187a0cadb5f2', '385e4f7a-b440-4759-9501-dc77836be2e3', '박병창', '삼성전자', 
        '005930', 'KR', 'investment', 'POSITIVE', 
        'high', '[06:10]', '"삼성전자 목표주가 34만원, 올해 멀티플 5배, 내년 2-3배 미만으로 저평가"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195587+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('32e497af-83d2-4aa1-bfa1-9c64c8b3ed75', 'e644fb82-25d2-45fd-a749-2ba17396e4f7', '박병창', 'SK하이닉스', 
        '000660', 'KR', 'investment', 'POSITIVE', 
        'high', '[06:10]', '"SK하이닉스 목표주가 170만원, 현재 PER 5배 미만으로 매력적"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195599+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('a52e70a5-608b-4d58-a8ef-be1d28d09b49', 'd885aea9-1069-4806-a361-05875ec2a5ee', '김장열', 'SK하이닉스', 
        '000660', 'KR', 'investment', 'POSITIVE', 
        'high', '[15:24]', '"하이닉스도 PER 5배로 저평가. 목표주가 144만원까지 가능하나 28년 사이클 고려 필요"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195609+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('9663f66d-ee04-4b21-bc26-70013a8f2b9a', 'bd4618c3-08b1-4b5c-9b20-6f50aeb17c8e', '차영주', 'LG화학', 
        'NULL', 'KR', 'investment', 'POSITIVE', 
        'high', '11:17', 'LS증권 목표가 48만7천원 상향, LG엔솔 지분율 감축으로 주주가치 제고 기대', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195617+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('9e3223c0-eec9-42d0-9485-df9f013a4bb8', 'f25bd0cf-b74c-4d74-aab4-4f79d3cbe7d5', '차영주', '에코프로머티', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '19:30', '하이니켈 기술경쟁력과 전고체배터리 시장 확대로 2026년 연간 흑자전환 전망', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195628+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('a9b84ce7-e92a-43a5-b8eb-028ef1f715ff', 'e035342c-aa43-4ed5-b0f7-247e9dc14d34', '차영주', '이수페타시스', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '29:48', 'NH투자증권 목표주가 17만원 상향, 다중적층 제품 캐파 조기 확보로 2027년 급증 수요 대응', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195640+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('c9ce2059-cdab-417b-8e49-6ceb5ec25813', 'c8039e48-82f3-4d80-970d-3633c19f70b1', '차영주', '원익IPS', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '36:59', 'NH증권 목표주가 13만8천원 상향, 2027년까지 매출 성장 가시성 확보로 전공정 장비 수혜', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195650+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('e53064f1-289d-48a6-8292-d497a8d007ea', 'd83477aa-426f-4032-a137-eb46398b69cf', '박병창', 'SK하이닉스', 
        '000660', 'KR', 'investment', 'POSITIVE', 
        'high', '21:36', '엔비디아 미결제 구매액 35억달러 확인으로 향후 매출 가시성 확보, 증설 투자도 긍정적', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195690+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('f4c75d4a-8527-4843-9c03-a16a4f2a0d2c', 'e0727b54-9105-4aa2-a055-3b167a449fb8', '박명석', 'LG전자', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '30:53', '"LG전자도 시가총액이 비싸지 않아서 추가적인 상승 여력이 있다"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195701+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('ddddd84c-442a-4f0c-82af-479df2eb6eeb', 'f5629777-8797-4f5c-9927-31209bce203f', '고연수', 'NH투자증권', 
        'NULL', 'SECTOR', 'investment', 'POSITIVE', 
        'high', '07:14', '"배당성향 43%로 추정하며 DPS가 전년 대비 20% 성장할 수 있다"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195711+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('798c8e5b-6380-4156-8b2a-91188ea64812', '3195b698-8eea-4675-8a45-6027ac73b427', '고연수', '한국금융지주', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '08:16', '"올해도 최소 2조원 순익을 달성할 수 있고 트레이딩 역량이 매우 좋다"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195722+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('a4f8e96b-3131-40c1-8361-3e14bb62368f', 'db9a1592-e7fd-4d6d-967a-9465e5911856', '박현지', '삼성전기', 
        'NULL', 'KR', 'investment', 'POSITIVE', 
        'high', '20:38', '"삼성전기 좀 보시면 좋을 것 같아요... 전력 수급난이 계속 지속되면서 AI와 관련된 기업들 중심으로 이제 담는 그런 모양세가 국내 장에서도 계속 확인이 되고 있다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195733+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('3151c818-9a01-4962-823b-a12a8d2de556', 'e3c78331-75b0-4696-bbfb-aca8fbd81f6e', '박명성', '엔비디아', 
        'NVDA', 'US', 'investment', 'POSITIVE', 
        'high', '31:57', '"엔비디아 실적은 그냥 엔비디아 실적이에요. 매출 상회 EPS 상회하며 데이터센터 매출이 75% 증가"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195742+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('edbdc8a7-5e36-4bd3-a3c7-7d86cb6b5497', 'e8d6be3a-12d5-4842-964a-553a515046e9', '차영주', '심텍', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '07:10', '"AI 기판에 대한 새로운 모멘텀 기대감이 높고 2분기 이후 점진적 대량 양산체제 진입 전망"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195752+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('da442245-df2e-4c89-8f08-b478d42db4e5', '2c4475f1-c6b8-41a8-8353-41056f43b7da', '차영주', 'SK스퀘어', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '30:57', '"SK하이닉스 연동으로 목표주가 76만원 상향. 펀드 매니저들의 하이닉스 대안 투자처"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195762+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('ca59d27a-d151-4ed1-a063-9f266a908e36', '187f8e2d-f2c3-439e-a509-9ff95c12dbea', '이재규', '삼성전자', 
        '005930', 'KR', 'investment', 'POSITIVE', 
        'high', '35:04', '"2027년 매출 세계 최고 전망. 파운드리 흑자전환으로 추가 성장동력"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195771+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('b750f04a-8861-466b-a431-df687a2dd1c7', '2d361804-ca6e-464d-b921-a0e35fe35a28', '이재규', '건설주', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '23:40', '"원전 밸류와 AI 인프라 수혜로 현대건설, 대우건설 등 재평가 가능성"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195782+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('207100c3-4220-4d53-a043-a56c64a75495', '98d29848-9b00-4174-9128-a6f1b9f7170b', '장우진', 'AMD', 
        'NULL', 'UNKNOWN', 'investment', 'POSITIVE', 
        'high', '37:01', '"메타와 6GW 계약하며 0.01달러 신주인수권 부여. 파트너십 강화로 엔비디아 견제"', 
        '3프로TV 분석 기반 - 논거', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195793+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('219dc0bd-1b12-4b11-aa5b-462122e08aa0', '41cda751-809a-49fb-bd8b-45008224e4e8', '이권희', '현대차', 
        '005380', 'KR', 'investment', 'POSITIVE', 
        'high', '13:18', '"현대차 지금이라도 사야 돼요라고 물어보면 저는 예스라고 말씀드릴 수 있어요... 80만원까지 갈 수 있을까 말까 고민하다가 결국에는 외국인들이 쏜 거죠"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195801+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('cae330f6-fd0a-40f5-9848-98040bdebc57', 'b386a114-41ef-4869-9401-1e0fde379997', '박지훈', 'LG화학', 
        'NULL', 'KR', 'investment', 'POSITIVE', 
        'high', '36:11', '"LG화학을 전 강력 추천드리는 바입니다... 행동주의 펀드들이 열받아 있다... LG화학은 약간 다른 각도로 접근하면 되지 않을까 싶습니다"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195810+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('31a100ab-da33-4d47-ad6b-637ac89783a2', '444cff93-2872-4937-8cb6-9b76072f852b', '김장열', '삼성전자', 
        '005930', 'KR', 'investment', 'HOLD', 
        'high', '[22:34]', '"목표주가 26만원 평균, 하지만 신규 매수는 신중해야. ROE 평균치 고려 시 업사이드 제한적"', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195819+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('5d42bf7f-a282-437b-be45-54acc1138bde', '306107a5-7b9b-43f8-90a4-49dee27953df', '박병창', '삼성전자', 
        '005930', 'KR', 'investment', 'HOLD', 
        'high', '07:12', '시장 견인 역할 지속 중이나 솔림현상으로 조정 시 타격 가능성, 대형주 70% 비중 유지 필요', 
        '3프로TV 분석 기반 - 결론', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195829+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('88838cce-eec1-4a27-ba49-a884a092b790', 'dbe1d097-78bd-429c-9c67-cc0b44952bb2', '박명성', '삼성전자', 
        '005930', 'KR', 'investment', 'NEUTRAL', 
        'high', '[32:59]', '"국내 반도체는 엔비디아 영향받을 수 있지만 한국 ETF 상승으로 상쇄 가능성"', 
        '3프로TV 분석 기반 - 뉴스', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195838+00:00');


INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('89f05475-fd0d-4f83-8ba5-4c7840819426', '9ab71403-8a7b-4c46-b7a5-e2fc51fcb89f', '장우진', '엔비디아', 
        'NVDA', 'US', 'investment', 'NEUTRAL', 
        'high', '15:23', '"엔비디아 실적에 대한 주목도가 예전보다 낮아졌다. 이미 빅테크 케펙스로 실적 좋을 것은 노출됐다"', 
        '3프로TV 분석 기반 - 뉴스', '출처: 3프로TV, 분석일: 2026-02-27', 'approved', 
        '3protv_v7', '2026-02-27T07:36:27.195847+00:00');
