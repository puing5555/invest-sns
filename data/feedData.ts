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
      direction: string; // V9: 매수, 긍정, 중립, 경계, 매도
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

// V9 기준 피드 데이터
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
    "timestamp": "2026-02-28T02:56:23.724Z",
    "content": {
      "text": "증권주는 거의 다 편하게 가져가도 된다. 무조건 지금보다는 수익률이 더 나을 수 있다",
      "signal": {
        "stock": "증권주전체",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 69706.67482313138
      }
    },
    "engagement": {
      "likes": 80,
      "comments": 10,
      "shares": 0,
      "bookmarks": 14
    },
    "tags": [
      "증권주전체",
      "매수",
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
    "timestamp": "2026-02-28T01:56:23.725Z",
    "content": {
      "text": "영업이익 추정치가 계속 상향되고 있는데 매도할 이유가 없다. 지금이라도 들어가야 된다",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 120357.03408464967
      }
    },
    "engagement": {
      "likes": 36,
      "comments": 7,
      "shares": 4,
      "bookmarks": 0
    },
    "tags": [
      "삼성전자",
      "매수",
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
    "timestamp": "2026-02-28T00:56:23.725Z",
    "content": {
      "text": "목표주가가 계속 높아지고 있는 상황에서 매수하지 않을 이유가 뭔지 오히려 궁금하다",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 139900.48876880747
      }
    },
    "engagement": {
      "likes": 67,
      "comments": 2,
      "shares": 7,
      "bookmarks": 1
    },
    "tags": [
      "SK하이닉스",
      "매수",
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
    "timestamp": "2026-02-27T23:56:23.725Z",
    "content": {
      "text": "상반기에 정말 7,000포인트라는 더 역사적인 순간도 볼 수 있지 않을까",
      "signal": {
        "stock": "코스피",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 120583.47473901564
      }
    },
    "engagement": {
      "likes": 91,
      "comments": 15,
      "shares": 0,
      "bookmarks": 10
    },
    "tags": [
      "코스피",
      "매수",
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
    "timestamp": "2026-02-27T22:56:23.725Z",
    "content": {
      "text": "서클 주가가 30% 넘게 급등했고 USDC 순환량이 전년 대비 72% 급증. 스테이블코인 인프라가 계속 구축되고 있어",
      "signal": {
        "stock": "서클",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 121007.55487583204
      }
    },
    "engagement": {
      "likes": 81,
      "comments": 4,
      "shares": 9,
      "bookmarks": 17
    },
    "tags": [
      "서클",
      "매수",
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
    "timestamp": "2026-02-27T21:56:23.725Z",
    "content": {
      "text": "5% 급락은 과도해. 실적 완벽했고 기술주가 필수소비재보다 저평가. 없는 분들에게 기회",
      "signal": {
        "stock": "엔비디아",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 89286.62606356543
      }
    },
    "engagement": {
      "likes": 35,
      "comments": 8,
      "shares": 7,
      "bookmarks": 8
    },
    "tags": [
      "엔비디아",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-7",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T20:56:23.725Z",
    "content": {
      "text": "메코리 목표주가 33만원, 향후 3-4개월간 업사이드 존재하며 배당 상향 기대감도 긍정적",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 93352.32841748072
      }
    },
    "engagement": {
      "likes": 61,
      "comments": 2,
      "shares": 0,
      "bookmarks": 26
    },
    "tags": [
      "삼성전자",
      "매수",
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
    "timestamp": "2026-02-27T19:56:23.725Z",
    "content": {
      "text": "270조 이익 전망에도 불구 밸류에이션 디스카운트, 중국 공장 업그레이드 제약이 리스크 요인",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 132861.8913663074
      }
    },
    "engagement": {
      "likes": 45,
      "comments": 8,
      "shares": 9,
      "bookmarks": 10
    },
    "tags": [
      "SK하이닉스",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-9",
    "type": "signal",
    "author": {
      "id": "박명석",
      "name": "박명석",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T18:56:23.725Z",
    "content": {
      "text": "2027년 포워드 PER로 계산해도 3-4배밖에 안 되기 때문에 지금 삼성전자는 계속 가도 전혀 이상하지 않다",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 51882.477488055236
      }
    },
    "engagement": {
      "likes": 42,
      "comments": 5,
      "shares": 1,
      "bookmarks": 8
    },
    "tags": [
      "삼성전자",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-10",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T17:56:23.725Z",
    "content": {
      "text": "대형주들의 장세가 좀 더 이어질 가능성이 높고, 7,000포인트까지 열려 있다",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 125271.5896846632
      }
    },
    "engagement": {
      "likes": 33,
      "comments": 18,
      "shares": 8,
      "bookmarks": 20
    },
    "tags": [
      "SK하이닉스",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-11",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T16:56:23.725Z",
    "content": {
      "text": "결론은 삼성전자 SK하이닉스의 이익이 증가하는 걸 계산해 가지고 지수가 올라간다... 이번 상승에서 이 수익률을 쫓아가려면 삼성전자 SK하이닉스를 가지고 있어야 되는 거고",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 120578.56126722388
      }
    },
    "engagement": {
      "likes": 64,
      "comments": 3,
      "shares": 9,
      "bookmarks": 10
    },
    "tags": [
      "삼성전자",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-12",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T15:56:23.725Z",
    "content": {
      "text": "우선순위는... 메모리죠... 삼성전자나 SK하이닉스가 오늘 본장에서... 빠질 이유가 없죠... 대기하고 있는 사람이 너무 많아요",
      "signal": {
        "stock": "삼성전자",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 63927.74004657385
      }
    },
    "engagement": {
      "likes": 43,
      "comments": 6,
      "shares": 1,
      "bookmarks": 12
    },
    "tags": [
      "삼성전자",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-13",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T14:56:23.725Z",
    "content": {
      "text": "로봇 밸류와 자율주행 모멘텀 부각. 테슬라 PER 280배 대비 현대차는 상승 밸류 남아있다",
      "signal": {
        "stock": "현대차",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 104634.97428783283
      }
    },
    "engagement": {
      "likes": 92,
      "comments": 4,
      "shares": 5,
      "bookmarks": 26
    },
    "tags": [
      "현대차",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-14",
    "type": "signal",
    "author": {
      "id": "장우진",
      "name": "장우진",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T13:56:23.725Z",
    "content": {
      "text": "노트북LM, 뮤직 등으로 오픈AI 추격하며 확실한 1등. 데이터 자산으로 앞서나가고 있다",
      "signal": {
        "stock": "구글(알파벳)",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 117247.74688450768
      }
    },
    "engagement": {
      "likes": 99,
      "comments": 11,
      "shares": 2,
      "bookmarks": 10
    },
    "tags": [
      "구글(알파벳)",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-15",
    "type": "signal",
    "author": {
      "id": "김동훈",
      "name": "김동훈",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T12:56:23.725Z",
    "content": {
      "text": "신세계를 저는 좋게 보고 있거든요... 외국인은 지금 주가에서도 여전히 순매수 상태입니다... 추가 상승 여력이 있다라고 배팅을 한 거로 보여지거든요",
      "signal": {
        "stock": "신세계",
        "direction": "매수",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 56387.2460978499
      }
    },
    "engagement": {
      "likes": 56,
      "comments": 19,
      "shares": 3,
      "bookmarks": 9
    },
    "tags": [
      "신세계",
      "매수",
      "결론"
    ]
  },
  {
    "id": "signal-16",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T11:56:23.725Z",
    "content": {
      "text": "삼성전자 목표주가 34만원, 올해 멀티플 5배, 내년 2-3배 미만으로 저평가",
      "signal": {
        "stock": "삼성전자",
        "direction": "긍정",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 79852.01194895717
      }
    },
    "engagement": {
      "likes": 14,
      "comments": 11,
      "shares": 2,
      "bookmarks": 5
    },
    "tags": [
      "삼성전자",
      "긍정",
      "결론"
    ]
  },
  {
    "id": "signal-17",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T10:56:23.725Z",
    "content": {
      "text": "SK하이닉스 목표주가 170만원, 현재 PER 5배 미만으로 매력적",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "긍정",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 100965.83244800719
      }
    },
    "engagement": {
      "likes": 74,
      "comments": 4,
      "shares": 1,
      "bookmarks": 26
    },
    "tags": [
      "SK하이닉스",
      "긍정",
      "결론"
    ]
  },
  {
    "id": "signal-18",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T09:56:23.725Z",
    "content": {
      "text": "엔비디아 미결제 구매액 35억달러 확인으로 향후 매출 가시성 확보, 증설 투자도 긍정적",
      "signal": {
        "stock": "SK하이닉스",
        "direction": "긍정",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 63370.75038135723
      }
    },
    "engagement": {
      "likes": 51,
      "comments": 19,
      "shares": 2,
      "bookmarks": 6
    },
    "tags": [
      "SK하이닉스",
      "긍정",
      "결론"
    ]
  },
  {
    "id": "signal-19",
    "type": "signal",
    "author": {
      "id": "고연수",
      "name": "고연수",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T08:56:23.725Z",
    "content": {
      "text": "배당성향 43%로 추정하며 DPS가 전년 대비 20% 성장할 수 있다",
      "signal": {
        "stock": "NH투자증권",
        "direction": "긍정",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 91524.59402727812
      }
    },
    "engagement": {
      "likes": 86,
      "comments": 3,
      "shares": 0,
      "bookmarks": 22
    },
    "tags": [
      "NH투자증권",
      "긍정",
      "논거"
    ]
  },
  {
    "id": "signal-20",
    "type": "signal",
    "author": {
      "id": "고연수",
      "name": "고연수",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T07:56:23.725Z",
    "content": {
      "text": "올해도 최소 2조원 순익을 달성할 수 있고 트레이딩 역량이 매우 좋다",
      "signal": {
        "stock": "한국금융지주",
        "direction": "긍정",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 119219.65433433247
      }
    },
    "engagement": {
      "likes": 88,
      "comments": 3,
      "shares": 8,
      "bookmarks": 19
    },
    "tags": [
      "한국금융지주",
      "긍정",
      "논거"
    ]
  },
  {
    "id": "signal-21",
    "type": "signal",
    "author": {
      "id": "박현지",
      "name": "박현지",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T06:56:23.725Z",
    "content": {
      "text": "삼성전기 좀 보시면 좋을 것 같아요... 전력 수급난이 계속 지속되면서 AI와 관련된 기업들 중심으로 이제 담는 그런 모양세가 국내 장에서도 계속 확인이 되고 있다",
      "signal": {
        "stock": "삼성전기",
        "direction": "긍정",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 75771.41564770226
      }
    },
    "engagement": {
      "likes": 38,
      "comments": 3,
      "shares": 0,
      "bookmarks": 15
    },
    "tags": [
      "삼성전기",
      "긍정",
      "결론"
    ]
  },
  {
    "id": "signal-22",
    "type": "signal",
    "author": {
      "id": "박명성",
      "name": "박명성",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T05:56:23.725Z",
    "content": {
      "text": "엔비디아 실적은 그냥 엔비디아 실적이에요. 매출 상회 EPS 상회하며 데이터센터 매출이 75% 증가",
      "signal": {
        "stock": "엔비디아",
        "direction": "긍정",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 127558.2703938462
      }
    },
    "engagement": {
      "likes": 36,
      "comments": 18,
      "shares": 4,
      "bookmarks": 26
    },
    "tags": [
      "엔비디아",
      "긍정",
      "결론"
    ]
  },
  {
    "id": "signal-23",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T04:56:23.725Z",
    "content": {
      "text": "2027년 매출 세계 최고 전망. 파운드리 흑자전환으로 추가 성장동력",
      "signal": {
        "stock": "삼성전자",
        "direction": "긍정",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 130197.39858248658
      }
    },
    "engagement": {
      "likes": 10,
      "comments": 7,
      "shares": 6,
      "bookmarks": 9
    },
    "tags": [
      "삼성전자",
      "긍정",
      "논거"
    ]
  },
  {
    "id": "signal-24",
    "type": "signal",
    "author": {
      "id": "이재규",
      "name": "이재규",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T03:56:23.725Z",
    "content": {
      "text": "원전 밸류와 AI 인프라 수혜로 현대건설, 대우건설 등 재평가 가능성",
      "signal": {
        "stock": "건설주",
        "direction": "긍정",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 97167.96279790127
      }
    },
    "engagement": {
      "likes": 99,
      "comments": 3,
      "shares": 9,
      "bookmarks": 24
    },
    "tags": [
      "건설주",
      "긍정",
      "논거"
    ]
  },
  {
    "id": "signal-25",
    "type": "signal",
    "author": {
      "id": "장우진",
      "name": "장우진",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T02:56:23.725Z",
    "content": {
      "text": "메타와 6GW 계약하며 0.01달러 신주인수권 부여. 파트너십 강화로 엔비디아 견제",
      "signal": {
        "stock": "AMD",
        "direction": "긍정",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 147882.31562805944
      }
    },
    "engagement": {
      "likes": 10,
      "comments": 3,
      "shares": 6,
      "bookmarks": 10
    },
    "tags": [
      "AMD",
      "긍정",
      "논거"
    ]
  },
  {
    "id": "signal-26",
    "type": "signal",
    "author": {
      "id": "이권희",
      "name": "이권희",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T01:56:23.725Z",
    "content": {
      "text": "현대차 지금이라도 사야 돼요라고 물어보면 저는 예스라고 말씀드릴 수 있어요... 80만원까지 갈 수 있을까 말까 고민하다가 결국에는 외국인들이 쏜 거죠",
      "signal": {
        "stock": "현대차",
        "direction": "긍정",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 72019.2403554806
      }
    },
    "engagement": {
      "likes": 54,
      "comments": 6,
      "shares": 7,
      "bookmarks": 24
    },
    "tags": [
      "현대차",
      "긍정",
      "결론"
    ]
  },
  {
    "id": "signal-27",
    "type": "signal",
    "author": {
      "id": "박지훈",
      "name": "박지훈",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-27T00:56:23.725Z",
    "content": {
      "text": "LG화학을 전 강력 추천드리는 바입니다... 행동주의 펀드들이 열받아 있다... LG화학은 약간 다른 각도로 접근하면 되지 않을까 싶습니다",
      "signal": {
        "stock": "LG화학",
        "direction": "긍정",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 77925.60305225043
      }
    },
    "engagement": {
      "likes": 97,
      "comments": 6,
      "shares": 0,
      "bookmarks": 26
    },
    "tags": [
      "LG화학",
      "긍정",
      "결론"
    ]
  },
  {
    "id": "signal-28",
    "type": "signal",
    "author": {
      "id": "김장열",
      "name": "김장열",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T23:56:23.725Z",
    "content": {
      "text": "목표주가 26만원 평균, 하지만 신규 매수는 신중해야. ROE 평균치 고려 시 업사이드 제한적",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 106075.58981074713
      }
    },
    "engagement": {
      "likes": 72,
      "comments": 16,
      "shares": 5,
      "bookmarks": 17
    },
    "tags": [
      "삼성전자",
      "중립",
      "결론"
    ]
  },
  {
    "id": "signal-29",
    "type": "signal",
    "author": {
      "id": "박병창",
      "name": "박병창",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T22:56:23.725Z",
    "content": {
      "text": "시장 견인 역할 지속 중이나 솔림현상으로 조정 시 타격 가능성, 대형주 70% 비중 유지 필요",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "high",
        "targetPrice": null,
        "currentPrice": 58862.74603223126
      }
    },
    "engagement": {
      "likes": 54,
      "comments": 16,
      "shares": 2,
      "bookmarks": 4
    },
    "tags": [
      "삼성전자",
      "중립",
      "결론"
    ]
  },
  {
    "id": "signal-30",
    "type": "signal",
    "author": {
      "id": "박명성",
      "name": "박명성",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T21:56:23.725Z",
    "content": {
      "text": "국내 반도체는 엔비디아 영향받을 수 있지만 한국 ETF 상승으로 상쇄 가능성",
      "signal": {
        "stock": "삼성전자",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 57644.20569378349
      }
    },
    "engagement": {
      "likes": 17,
      "comments": 19,
      "shares": 2,
      "bookmarks": 8
    },
    "tags": [
      "삼성전자",
      "중립",
      "뉴스"
    ]
  },
  {
    "id": "signal-31",
    "type": "signal",
    "author": {
      "id": "장우진",
      "name": "장우진",
      "avatar": "/avatars/default.jpg",
      "verified": true,
      "followers": "10K+"
    },
    "timestamp": "2026-02-26T20:56:23.725Z",
    "content": {
      "text": "엔비디아 실적에 대한 주목도가 예전보다 낮아졌다. 이미 빅테크 케펙스로 실적 좋을 것은 노출됐다",
      "signal": {
        "stock": "엔비디아",
        "direction": "중립",
        "confidence": "medium",
        "targetPrice": null,
        "currentPrice": 58378.40312981328
      }
    },
    "engagement": {
      "likes": 50,
      "comments": 13,
      "shares": 5,
      "bookmarks": 16
    },
    "tags": [
      "엔비디아",
      "중립",
      "뉴스"
    ]
  }
];
