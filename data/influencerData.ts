export interface CallRecord {
  stock: string;
  date: string;
  direction: string; // V9: 매수, 긍정, 중립, 경계, 매도
  callPrice: number;
  currentPrice: number;
  returnRate: number;
  status: '진행중' | '적중' | '손절';
}

export interface Platform {
  name: '유튜브' | '텔레그램' | '블로그';
  color: string;
}

export interface MonthlyAccuracy {
  month: string;
  rate: number;
}

export interface Influencer {
  id: string;
  name: string;
  platforms: Platform[];
  followers: string;
  accuracy: number;
  totalCalls: number;
  successfulCalls: number;
  avgReturn: number;
  recentCalls: CallRecord[];
  monthlyAccuracy: MonthlyAccuracy[];
}

// V9 기준 시그널 색상
export const V9_SIGNAL_COLORS = {
  '매수': 'bg-red-600 text-white',
  '긍정': 'bg-green-600 text-white', 
  '중립': 'bg-gray-500 text-white',
  '경계': 'bg-yellow-600 text-white',
  '매도': 'bg-red-800 text-white'
};

// V9 기준 인플루언서 데이터
export const influencers: Influencer[] = [
  {
    "id": "고연수",
    "name": "고연수",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 3,
    "successfulCalls": 3,
    "avgReturn": 10.67,
    "recentCalls": [
      {
        "stock": "증권주전체",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 93125.10429758759,
        "currentPrice": 111317.07316686262,
        "returnRate": 11.67753919581667,
        "status": "적중"
      },
      {
        "stock": "NH투자증권",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 134698.2452952681,
        "currentPrice": 105691.45451582069,
        "returnRate": 18.503994869200188,
        "status": "적중"
      },
      {
        "stock": "한국금융지주",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 76142.60265506018,
        "currentPrice": 100475.09703458427,
        "returnRate": 1.8358897670277354,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 72.7548835175682
      },
      {
        "month": "2026-02",
        "rate": 73.34087587369088
      },
      {
        "month": "2026-03",
        "rate": 75.65141150577479
      }
    ]
  },
  {
    "id": "배재원",
    "name": "배재원",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 67,
    "totalCalls": 3,
    "successfulCalls": 2,
    "avgReturn": -4.41,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 136591.37562714337,
        "currentPrice": 118644.02553816736,
        "returnRate": -8.065836244401725,
        "status": "진행중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 65893.60383685527,
        "currentPrice": 137852.75142281473,
        "returnRate": -9.23537799878863,
        "status": "적중"
      },
      {
        "stock": "코스피",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 140479.10219868115,
        "currentPrice": 124622.50651375807,
        "returnRate": 4.057222074298464,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 77.45881599777549
      },
      {
        "month": "2026-02",
        "rate": 72.24027153228808
      },
      {
        "month": "2026-03",
        "rate": 84.33065766681003
      }
    ]
  },
  {
    "id": "박명성",
    "name": "박명성",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 75,
    "totalCalls": 4,
    "successfulCalls": 3,
    "avgReturn": -3.36,
    "recentCalls": [
      {
        "stock": "서클",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 141625.42479359367,
        "currentPrice": 74572.81396775563,
        "returnRate": -9.903827318312414,
        "status": "적중"
      },
      {
        "stock": "엔비디아",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 149438.9670281258,
        "currentPrice": 106194.89753785334,
        "returnRate": 2.083859755697766,
        "status": "적중"
      },
      {
        "stock": "엔비디아",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 66729.73947230924,
        "currentPrice": 127389.09171978934,
        "returnRate": -7.194030351648837,
        "status": "진행중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "중립",
        "callPrice": 67311.94289630653,
        "currentPrice": 76718.08548673874,
        "returnRate": 1.5784634692923944,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 90.85426544955453
      },
      {
        "month": "2026-02",
        "rate": 72.62110044595477
      },
      {
        "month": "2026-03",
        "rate": 82.37078218210264
      }
    ]
  },
  {
    "id": "김장열",
    "name": "김장열",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 4,
    "successfulCalls": 4,
    "avgReturn": -0.74,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 117832.89287171033,
        "currentPrice": 139247.72598216077,
        "returnRate": 0.7891503042784613,
        "status": "적중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 77249.94083658344,
        "currentPrice": 101720.92243896335,
        "returnRate": -3.939548925420416,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 59106.45964798239,
        "currentPrice": 60757.307052859454,
        "returnRate": 6.18411848456126,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "중립",
        "callPrice": 136341.77683974485,
        "currentPrice": 53213.143567008,
        "returnRate": -5.992229110437018,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 82.80826897502226
      },
      {
        "month": "2026-02",
        "rate": 94.07628906729157
      },
      {
        "month": "2026-03",
        "rate": 84.21995130649857
      }
    ]
  },
  {
    "id": "박명석",
    "name": "박명석",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 1,
    "successfulCalls": 1,
    "avgReturn": 17.24,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 140140.34975081024,
        "currentPrice": 138342.68051187292,
        "returnRate": 17.239541736538282,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 90.41080508023241
      },
      {
        "month": "2026-02",
        "rate": 75.58816932189646
      },
      {
        "month": "2026-03",
        "rate": 90.34200793666834
      }
    ]
  },
  {
    "id": "이재규",
    "name": "이재규",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 75,
    "totalCalls": 4,
    "successfulCalls": 3,
    "avgReturn": 1.4,
    "recentCalls": [
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 65842.6822613934,
        "currentPrice": 58791.14620825516,
        "returnRate": 1.6199637552116624,
        "status": "적중"
      },
      {
        "stock": "현대차",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 115456.65185828546,
        "currentPrice": 114189.31192727675,
        "returnRate": 12.931795424262607,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 129558.60829783877,
        "currentPrice": 142050.22135618198,
        "returnRate": -7.161660601236043,
        "status": "진행중"
      },
      {
        "stock": "건설주",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 107916.7790657446,
        "currentPrice": 70573.81437369688,
        "returnRate": -1.7876843132761326,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 72.02378628078355
      },
      {
        "month": "2026-02",
        "rate": 71.51064632864617
      },
      {
        "month": "2026-03",
        "rate": 94.03070607479846
      }
    ]
  },
  {
    "id": "박병창",
    "name": "박병창",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 80,
    "totalCalls": 5,
    "successfulCalls": 4,
    "avgReturn": 7.56,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 116113.53082428528,
        "currentPrice": 115384.3533263897,
        "returnRate": 4.26716852395619,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 51602.168385984594,
        "currentPrice": 149817.93553545157,
        "returnRate": 11.747483937354257,
        "status": "진행중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 71341.92655078035,
        "currentPrice": 60515.47739910914,
        "returnRate": 2.4497316189639466,
        "status": "적중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 50817.56094791264,
        "currentPrice": 107233.33373091818,
        "returnRate": 5.734947046792559,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "중립",
        "callPrice": 60906.36151285551,
        "currentPrice": 145104.35142146907,
        "returnRate": 13.608764883811567,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 89.93171038860322
      },
      {
        "month": "2026-02",
        "rate": 80.09083200907992
      },
      {
        "month": "2026-03",
        "rate": 85.52282336311795
      }
    ]
  },
  {
    "id": "장우진",
    "name": "장우진",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 3,
    "successfulCalls": 3,
    "avgReturn": -0.86,
    "recentCalls": [
      {
        "stock": "구글(알파벳)",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 123541.60617522427,
        "currentPrice": 101967.30960599436,
        "returnRate": 1.3929808576291425,
        "status": "적중"
      },
      {
        "stock": "AMD",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 84770.42730880252,
        "currentPrice": 148628.3944284547,
        "returnRate": -2.6840402873714986,
        "status": "적중"
      },
      {
        "stock": "엔비디아",
        "date": "2026-02-27",
        "direction": "중립",
        "callPrice": 102065.83813992655,
        "currentPrice": 74582.32995640817,
        "returnRate": -1.2901665741893318,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 90.61193933114652
      },
      {
        "month": "2026-02",
        "rate": 94.492933498287
      },
      {
        "month": "2026-03",
        "rate": 80.3995688683418
      }
    ]
  },
  {
    "id": "김동훈",
    "name": "김동훈",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 1,
    "successfulCalls": 1,
    "avgReturn": -8.48,
    "recentCalls": [
      {
        "stock": "신세계",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 145800.3725513463,
        "currentPrice": 58319.60411557187,
        "returnRate": -8.480428729449557,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 93.90367505674315
      },
      {
        "month": "2026-02",
        "rate": 73.92807636538568
      },
      {
        "month": "2026-03",
        "rate": 91.40472838438609
      }
    ]
  },
  {
    "id": "박현지",
    "name": "박현지",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 1,
    "successfulCalls": 1,
    "avgReturn": -8.17,
    "recentCalls": [
      {
        "stock": "삼성전기",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 104390.83077478748,
        "currentPrice": 144117.06724051666,
        "returnRate": -8.17061738597793,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 91.1781119438169
      },
      {
        "month": "2026-02",
        "rate": 92.6223674175906
      },
      {
        "month": "2026-03",
        "rate": 94.8339973531418
      }
    ]
  },
  {
    "id": "이권희",
    "name": "이권희",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 0,
    "totalCalls": 1,
    "successfulCalls": 0,
    "avgReturn": 18.08,
    "recentCalls": [
      {
        "stock": "현대차",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 106590.92164966464,
        "currentPrice": 107014.38985129056,
        "returnRate": 18.075840232141843,
        "status": "진행중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 94.14672950584549
      },
      {
        "month": "2026-02",
        "rate": 83.25864064034938
      },
      {
        "month": "2026-03",
        "rate": 85.56227486417495
      }
    ]
  },
  {
    "id": "박지훈",
    "name": "박지훈",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 1,
    "successfulCalls": 1,
    "avgReturn": -2.55,
    "recentCalls": [
      {
        "stock": "LG화학",
        "date": "2026-02-27",
        "direction": "긍정",
        "callPrice": 138226.18178553227,
        "currentPrice": 55583.99799900511,
        "returnRate": -2.551627827969421,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 79.35956024662235
      },
      {
        "month": "2026-02",
        "rate": 84.86073537530247
      },
      {
        "month": "2026-03",
        "rate": 72.46357283037787
      }
    ]
  }
];
