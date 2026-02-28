export interface FeedPost {
  id: string;
  type: 'signal' | 'news' | 'analysis';
  author: {
    id: string;
    name: string;
    avatar: string;
    verified: boolean;
    followers: string;
  };
  timestamp: string;
  content: {
    text: string;
    signal?: {
      stock: string;
      direction: '매수' | '매도' | '중립';
      confidence: 'high' | 'medium' | 'low';
      targetPrice?: number;
      currentPrice?: number;
    };
  };
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    bookmarks: number;
  };
  tags: string[];
}

// Real feed data from signals
export const feedPosts: FeedPost[] = [
  {
    "id": "signal-1",
    "type": "signal",
    "author": {
      "id": "고연수",
      "name": "고연수",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-28T02:42:31.696Z",
    "content": {
      "text": "증권주는 거의 다 편하게 가져가도 된다. 무조건 지금보다는 수익률이 더 나을 수 있다",
      "signal": {
        "stock": "증권주전체",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 63538.82689249316
      }
    },
    "engagement": {
      "likes": 15,
      "comments": 14,
      "shares": 2,
      "bookmarks": 10
    },
    "tags": [
      "증권주전체",
      "STRONG_BUY",
      "결론"
    ]
  },
  {
    "id": "signal-2",
    "type": "signal",
    "author": {
      "id": "배재원",
      "name": "배재원",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-28T01:42:31.697Z",
    "content": {
      "text": "영업이익 추정치가 계속 상향되고 있는데 매도할 이유가 없다. 지금이라도 들어가야 된다",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 136696.84805801464
      }
    },
    "engagement": {
      "likes": 73,
      "comments": 6,
      "shares": 8,
      "bookmarks": 7
    },
    "tags": [
      "삼성전자",
      "STRONG_BUY",
      "결론"
    ]
  },
  {
    "id": "signal-3",
    "type": "signal",
    "author": {
      "id": "배재원",
      "name": "배재원",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-28T00:42:31.697Z",
    "content": {
      "text": "목표주가가 계속 높아지고 있는 상황에서 매수하지 않을 이유가 뭔지 오히려 궁금하다",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 102819.15781051667
      }
    },
    "engagement": {
      "likes": 86,
      "comments": 11,
      "shares": 2,
      "bookmarks": 7
    },
    "tags": [
      "SK하이닉스",
      "STRONG_BUY",
      "결론"
    ]
  },
  {
    "id": "signal-4",
    "type": "signal",
    "author": {
      "id": "배재원",
      "name": "배재원",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T23:42:31.697Z",
    "content": {
      "text": "상반기에 정말 7,000포인트라는 더 역사적인 순간도 볼 수 있지 않을까",
      "signal": {
        "stock": "코스피",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 117451.60425971702
      }
    },
    "engagement": {
      "likes": 50,
      "comments": 9,
      "shares": 2,
      "bookmarks": 16
    },
    "tags": [
      "코스피",
      "STRONG_BUY",
      "결론"
    ]
  },
  {
    "id": "signal-5",
    "type": "signal",
    "author": {
      "id": "박명성",
      "name": "박명성",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T22:42:31.697Z",
    "content": {
      "text": "서클 주가가 30% 넘게 급등했고 USDC 순환량이 전년 대비 72% 급증. 스테이블코인 인프라가 계속 구축되고 있어",
      "signal": {
        "stock": "서클",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 139738.19255755813
      }
    },
    "engagement": {
      "likes": 66,
      "comments": 2,
      "shares": 8,
      "bookmarks": 8
    },
    "tags": [
      "서클",
      "STRONG_BUY",
      "결론"
    ]
  },
  {
    "id": "signal-6",
    "type": "signal",
    "author": {
      "id": "박명성",
      "name": "박명성",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T21:42:31.697Z",
    "content": {
      "text": "5% 급락은 과도해. 실적 완벽했고 기술주가 필수소비재보다 저평가. 없는 분들에게 기회",
      "signal": {
        "stock": "엔비디아",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 102995.91022903449
      }
    },
    "engagement": {
      "likes": 78,
      "comments": 14,
      "shares": 0,
      "bookmarks": 7
    },
    "tags": [
      "엔비디아",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-7",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T20:42:31.697Z",
    "content": {
      "text": "교보증권 목표주가 37만원 상향, 로봇산업 진출과 카메라모듈 기술 확장으로 매출 성장 기대",
      "signal": {
        "stock": "LG이노텍",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 98531.10600634501
      }
    },
    "engagement": {
      "likes": 44,
      "comments": 19,
      "shares": 9,
      "bookmarks": 1
    },
    "tags": [
      "LG이노텍",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-8",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T19:42:31.697Z",
    "content": {
      "text": "메코리 목표주가 33만원, 향후 3-4개월간 업사이드 존재하며 배당 상향 기대감도 긍정적",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 136631.41922511155
      }
    },
    "engagement": {
      "likes": 30,
      "comments": 5,
      "shares": 9,
      "bookmarks": 4
    },
    "tags": [
      "삼성전자",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-9",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T18:42:31.697Z",
    "content": {
      "text": "270조 이익 전망에도 불구 밸류에이션 디스카운트, 중국 공장 업그레이드 제약이 리스크 요인",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 61598.691617724464
      }
    },
    "engagement": {
      "likes": 79,
      "comments": 10,
      "shares": 9,
      "bookmarks": 15
    },
    "tags": [
      "SK하이닉스",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-10",
    "type": "signal",
    "author": {
      "id": "박명석",
      "name": "박명석",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T17:42:31.697Z",
    "content": {
      "text": "2027년 포워드 PER로 계산해도 3-4배밖에 안 되기 때문에 지금 삼성전자는 계속 가도 전혀 이상하지 않다",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 70715.53876094842
      }
    },
    "engagement": {
      "likes": 45,
      "comments": 12,
      "shares": 8,
      "bookmarks": 25
    },
    "tags": [
      "삼성전자",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-11",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T16:42:31.697Z",
    "content": {
      "text": "대형주들의 장세가 좀 더 이어질 가능성이 높고, 7,000포인트까지 열려 있다",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 90403.84740591072
      }
    },
    "engagement": {
      "likes": 4,
      "comments": 16,
      "shares": 5,
      "bookmarks": 14
    },
    "tags": [
      "SK하이닉스",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-12",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T15:42:31.697Z",
    "content": {
      "text": "결론은 삼성전자 SK하이닉스의 이익이 증가하는 걸 계산해 가지고 지수가 올라간다... 이번 상승에서 이 수익률을 쫓아가려면 삼성전자 SK하이닉스를 가지고 있어야 되는 거고",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 55363.54708017653
      }
    },
    "engagement": {
      "likes": 53,
      "comments": 1,
      "shares": 9,
      "bookmarks": 7
    },
    "tags": [
      "삼성전자",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-13",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T14:42:31.697Z",
    "content": {
      "text": "우선순위는... 메모리죠... 삼성전자나 SK하이닉스가 오늘 본장에서... 빠질 이유가 없죠... 대기하고 있는 사람이 너무 많아요",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 55855.43837333614
      }
    },
    "engagement": {
      "likes": 28,
      "comments": 1,
      "shares": 9,
      "bookmarks": 20
    },
    "tags": [
      "삼성전자",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-14",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T13:42:31.697Z",
    "content": {
      "text": "목표주가 27만원으로 17% 상향. 미국에서 하이브리드 현지생산과 배당 4% 모멘텀",
      "signal": {
        "stock": "기아",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 107203.29035858215
      }
    },
    "engagement": {
      "likes": 70,
      "comments": 19,
      "shares": 1,
      "bookmarks": 10
    },
    "tags": [
      "기아",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-15",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T12:42:31.697Z",
    "content": {
      "text": "해외 원전사업 가치로 목표주가 8만원. 배당수익률 5.7% 기대",
      "signal": {
        "stock": "한국전력",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 59157.447529387224
      }
    },
    "engagement": {
      "likes": 11,
      "comments": 16,
      "shares": 7,
      "bookmarks": 21
    },
    "tags": [
      "한국전력",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-16",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T11:42:31.697Z",
    "content": {
      "text": "로봇 밸류와 자율주행 모멘텀 부각. 테슬라 PER 280배 대비 현대차는 상승 밸류 남아있다",
      "signal": {
        "stock": "현대차",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 78964.95205651807
      }
    },
    "engagement": {
      "likes": 13,
      "comments": 7,
      "shares": 9,
      "bookmarks": 15
    },
    "tags": [
      "현대차",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-17",
    "type": "signal",
    "author": {
      "id": "장우진",
      "name": "장우진",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T10:42:31.697Z",
    "content": {
      "text": "노트북LM, 뮤직 등으로 오픈AI 추격하며 확실한 1등. 데이터 자산으로 앞서나가고 있다",
      "signal": {
        "stock": "구글(알파벳)",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 125386.57963292464
      }
    },
    "engagement": {
      "likes": 38,
      "comments": 11,
      "shares": 8,
      "bookmarks": 7
    },
    "tags": [
      "구글(알파벳)",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-18",
    "type": "signal",
    "author": {
      "id": "김동훈",
      "name": "김동훈",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T09:42:31.697Z",
    "content": {
      "text": "신세계를 저는 좋게 보고 있거든요... 외국인은 지금 주가에서도 여전히 순매수 상태입니다... 추가 상승 여력이 있다라고 배팅을 한 거로 보여지거든요",
      "signal": {
        "stock": "신세계",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 109777.61075735853
      }
    },
    "engagement": {
      "likes": 41,
      "comments": 6,
      "shares": 8,
      "bookmarks": 4
    },
    "tags": [
      "신세계",
      "BUY",
      "결론"
    ]
  },
  {
    "id": "signal-19",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T08:42:31.697Z",
    "content": {
      "text": "삼성전자 목표주가 34만원, 올해 멀티플 5배, 내년 2-3배 미만으로 저평가",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 59810.01710012157
      }
    },
    "engagement": {
      "likes": 45,
      "comments": 13,
      "shares": 5,
      "bookmarks": 14
    },
    "tags": [
      "삼성전자",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-20",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T07:42:31.697Z",
    "content": {
      "text": "SK하이닉스 목표주가 170만원, 현재 PER 5배 미만으로 매력적",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 75743.42176124552
      }
    },
    "engagement": {
      "likes": 82,
      "comments": 7,
      "shares": 0,
      "bookmarks": 8
    },
    "tags": [
      "SK하이닉스",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-21",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T06:42:31.697Z",
    "content": {
      "text": "하이닉스도 PER 5배로 저평가. 목표주가 144만원까지 가능하나 28년 사이클 고려 필요",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 117153.7136554021
      }
    },
    "engagement": {
      "likes": 13,
      "comments": 5,
      "shares": 8,
      "bookmarks": 17
    },
    "tags": [
      "SK하이닉스",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-22",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T05:42:31.697Z",
    "content": {
      "text": "LS증권 목표가 48만7천원 상향, LG엔솔 지분율 감축으로 주주가치 제고 기대",
      "signal": {
        "stock": "LG화학",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 121677.47017357631
      }
    },
    "engagement": {
      "likes": 98,
      "comments": 6,
      "shares": 2,
      "bookmarks": 23
    },
    "tags": [
      "LG화학",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-23",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T04:42:31.697Z",
    "content": {
      "text": "하이니켈 기술경쟁력과 전고체배터리 시장 확대로 2026년 연간 흑자전환 전망",
      "signal": {
        "stock": "에코프로머티",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 128740.36154361928
      }
    },
    "engagement": {
      "likes": 67,
      "comments": 3,
      "shares": 9,
      "bookmarks": 5
    },
    "tags": [
      "에코프로머티",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-24",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T03:42:31.697Z",
    "content": {
      "text": "NH투자증권 목표주가 17만원 상향, 다중적층 제품 캐파 조기 확보로 2027년 급증 수요 대응",
      "signal": {
        "stock": "이수페타시스",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 74308.49008133507
      }
    },
    "engagement": {
      "likes": 36,
      "comments": 10,
      "shares": 9,
      "bookmarks": 26
    },
    "tags": [
      "이수페타시스",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-25",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T02:42:31.697Z",
    "content": {
      "text": "NH증권 목표주가 13만8천원 상향, 2027년까지 매출 성장 가시성 확보로 전공정 장비 수혜",
      "signal": {
        "stock": "원익IPS",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 51609.15892763085
      }
    },
    "engagement": {
      "likes": 39,
      "comments": 17,
      "shares": 3,
      "bookmarks": 26
    },
    "tags": [
      "원익IPS",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-26",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T01:42:31.697Z",
    "content": {
      "text": "엔비디아 미결제 구매액 35억달러 확인으로 향후 매출 가시성 확보, 증설 투자도 긍정적",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 127629.44099783139
      }
    },
    "engagement": {
      "likes": 30,
      "comments": 18,
      "shares": 6,
      "bookmarks": 0
    },
    "tags": [
      "SK하이닉스",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-27",
    "type": "signal",
    "author": {
      "id": "박명석",
      "name": "박명석",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T00:42:31.697Z",
    "content": {
      "text": "LG전자도 시가총액이 비싸지 않아서 추가적인 상승 여력이 있다",
      "signal": {
        "stock": "LG전자",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 103561.93999018127
      }
    },
    "engagement": {
      "likes": 83,
      "comments": 6,
      "shares": 9,
      "bookmarks": 17
    },
    "tags": [
      "LG전자",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-28",
    "type": "signal",
    "author": {
      "id": "고연수",
      "name": "고연수",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T23:42:31.697Z",
    "content": {
      "text": "배당성향 43%로 추정하며 DPS가 전년 대비 20% 성장할 수 있다",
      "signal": {
        "stock": "NH투자증권",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 143163.72317212465
      }
    },
    "engagement": {
      "likes": 24,
      "comments": 1,
      "shares": 3,
      "bookmarks": 15
    },
    "tags": [
      "NH투자증권",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-29",
    "type": "signal",
    "author": {
      "id": "고연수",
      "name": "고연수",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T22:42:31.697Z",
    "content": {
      "text": "올해도 최소 2조원 순익을 달성할 수 있고 트레이딩 역량이 매우 좋다",
      "signal": {
        "stock": "한국금융지주",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 119174.25910472193
      }
    },
    "engagement": {
      "likes": 5,
      "comments": 14,
      "shares": 3,
      "bookmarks": 17
    },
    "tags": [
      "한국금융지주",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-30",
    "type": "signal",
    "author": {
      "id": "박현지",
      "name": "박현지",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T21:42:31.697Z",
    "content": {
      "text": "삼성전기 좀 보시면 좋을 것 같아요... 전력 수급난이 계속 지속되면서 AI와 관련된 기업들 중심으로 이제 담는 그런 모양세가 국내 장에서도 계속 확인이 되고 있다",
      "signal": {
        "stock": "삼성전기",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 89788.84900735252
      }
    },
    "engagement": {
      "likes": 35,
      "comments": 2,
      "shares": 5,
      "bookmarks": 14
    },
    "tags": [
      "삼성전기",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-31",
    "type": "signal",
    "author": {
      "id": "박명성",
      "name": "박명성",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T20:42:31.697Z",
    "content": {
      "text": "엔비디아 실적은 그냥 엔비디아 실적이에요. 매출 상회 EPS 상회하며 데이터센터 매출이 75% 증가",
      "signal": {
        "stock": "엔비디아",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 50457.83440103294
      }
    },
    "engagement": {
      "likes": 98,
      "comments": 8,
      "shares": 5,
      "bookmarks": 13
    },
    "tags": [
      "엔비디아",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-32",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T19:42:31.697Z",
    "content": {
      "text": "AI 기판에 대한 새로운 모멘텀 기대감이 높고 2분기 이후 점진적 대량 양산체제 진입 전망",
      "signal": {
        "stock": "심텍",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 104438.13147548836
      }
    },
    "engagement": {
      "likes": 89,
      "comments": 11,
      "shares": 6,
      "bookmarks": 28
    },
    "tags": [
      "심텍",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-33",
    "type": "signal",
    "author": {
      "id": "차영주",
      "name": "차영주",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T18:42:31.697Z",
    "content": {
      "text": "SK하이닉스 연동으로 목표주가 76만원 상향. 펀드 매니저들의 하이닉스 대안 투자처",
      "signal": {
        "stock": "SK스퀘어",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 119843.3272183445
      }
    },
    "engagement": {
      "likes": 75,
      "comments": 14,
      "shares": 2,
      "bookmarks": 28
    },
    "tags": [
      "SK스퀘어",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-34",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T17:42:31.697Z",
    "content": {
      "text": "2027년 매출 세계 최고 전망. 파운드리 흑자전환으로 추가 성장동력",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 145201.5932534082
      }
    },
    "engagement": {
      "likes": 44,
      "comments": 13,
      "shares": 1,
      "bookmarks": 27
    },
    "tags": [
      "삼성전자",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-35",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T16:42:31.697Z",
    "content": {
      "text": "원전 밸류와 AI 인프라 수혜로 현대건설, 대우건설 등 재평가 가능성",
      "signal": {
        "stock": "건설주",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 112317.99524752169
      }
    },
    "engagement": {
      "likes": 88,
      "comments": 15,
      "shares": 6,
      "bookmarks": 10
    },
    "tags": [
      "건설주",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-36",
    "type": "signal",
    "author": {
      "id": "장우진",
      "name": "장우진",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T15:42:31.697Z",
    "content": {
      "text": "메타와 6GW 계약하며 0.01달러 신주인수권 부여. 파트너십 강화로 엔비디아 견제",
      "signal": {
        "stock": "AMD",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 86529.19149779872
      }
    },
    "engagement": {
      "likes": 62,
      "comments": 0,
      "shares": 1,
      "bookmarks": 14
    },
    "tags": [
      "AMD",
      "POSITIVE",
      "논거"
    ]
  },
  {
    "id": "signal-37",
    "type": "signal",
    "author": {
      "id": "이권희",
      "name": "이권희",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T14:42:31.697Z",
    "content": {
      "text": "현대차 지금이라도 사야 돼요라고 물어보면 저는 예스라고 말씀드릴 수 있어요... 80만원까지 갈 수 있을까 말까 고민하다가 결국에는 외국인들이 쏜 거죠",
      "signal": {
        "stock": "현대차",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 131952.39927110024
      }
    },
    "engagement": {
      "likes": 28,
      "comments": 11,
      "shares": 4,
      "bookmarks": 17
    },
    "tags": [
      "현대차",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-38",
    "type": "signal",
    "author": {
      "id": "박지훈",
      "name": "박지훈",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T13:42:31.697Z",
    "content": {
      "text": "LG화학을 전 강력 추천드리는 바입니다... 행동주의 펀드들이 열받아 있다... LG화학은 약간 다른 각도로 접근하면 되지 않을까 싶습니다",
      "signal": {
        "stock": "LG화학",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 56348.20423837087
      }
    },
    "engagement": {
      "likes": 57,
      "comments": 6,
      "shares": 3,
      "bookmarks": 4
    },
    "tags": [
      "LG화학",
      "POSITIVE",
      "결론"
    ]
  },
  {
    "id": "signal-39",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T12:42:31.697Z",
    "content": {
      "text": "목표주가 26만원 평균, 하지만 신규 매수는 신중해야. ROE 평균치 고려 시 업사이드 제한적",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 71182.08709554828
      }
    },
    "engagement": {
      "likes": 40,
      "comments": 9,
      "shares": 2,
      "bookmarks": 16
    },
    "tags": [
      "삼성전자",
      "HOLD",
      "결론"
    ]
  },
  {
    "id": "signal-40",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T11:42:31.697Z",
    "content": {
      "text": "시장 견인 역할 지속 중이나 솔림현상으로 조정 시 타격 가능성, 대형주 70% 비중 유지 필요",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 79552.01382260318
      }
    },
    "engagement": {
      "likes": 72,
      "comments": 9,
      "shares": 7,
      "bookmarks": 11
    },
    "tags": [
      "삼성전자",
      "HOLD",
      "결론"
    ]
  },
  {
    "id": "signal-41",
    "type": "signal",
    "author": {
      "id": "박명성",
      "name": "박명성",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T10:42:31.697Z",
    "content": {
      "text": "국내 반도체는 엔비디아 영향받을 수 있지만 한국 ETF 상승으로 상쇄 가능성",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 120630.0745387049
      }
    },
    "engagement": {
      "likes": 12,
      "comments": 12,
      "shares": 2,
      "bookmarks": 5
    },
    "tags": [
      "삼성전자",
      "NEUTRAL",
      "뉴스"
    ]
  },
  {
    "id": "signal-42",
    "type": "signal",
    "author": {
      "id": "장우진",
      "name": "장우진",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T09:42:31.697Z",
    "content": {
      "text": "엔비디아 실적에 대한 주목도가 예전보다 낮아졌다. 이미 빅테크 케펙스로 실적 좋을 것은 노출됐다",
      "signal": {
        "stock": "엔비디아",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 82956.09125230921
      }
    },
    "engagement": {
      "likes": 85,
      "comments": 6,
      "shares": 1,
      "bookmarks": 13
    },
    "tags": [
      "엔비디아",
      "NEUTRAL",
      "뉴스"
    ]
  }
];
