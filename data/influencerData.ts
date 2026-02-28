export interface CallRecord {
  stock: string;
  date: string;
  direction: '매수' | '매도';
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

// Real data from 3protv signals
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
    "accuracy": 67,
    "totalCalls": 3,
    "successfulCalls": 2,
    "avgReturn": 7.31,
    "recentCalls": [
      {
        "stock": "증권주전체",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 138649.49903619717,
        "currentPrice": 149650.37684020324,
        "returnRate": 15.138062696137155,
        "status": "적중"
      },
      {
        "stock": "NH투자증권",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 132969.5674968172,
        "currentPrice": 71541.00181287435,
        "returnRate": 15.784433771921346,
        "status": "진행중"
      },
      {
        "stock": "한국금융지주",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 113270.41965930228,
        "currentPrice": 74881.22729132138,
        "returnRate": -8.978333748089451,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 93.18797374056496
      },
      {
        "month": "2026-02",
        "rate": 83.26764404852774
      },
      {
        "month": "2026-03",
        "rate": 79.82027964358984
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
    "accuracy": 100,
    "totalCalls": 3,
    "successfulCalls": 3,
    "avgReturn": -3.21,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 139759.05719135317,
        "currentPrice": 95048.3787675295,
        "returnRate": 4.5653888603695965,
        "status": "적중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 99849.91469400303,
        "currentPrice": 89533.68626064595,
        "returnRate": -9.873782008933329,
        "status": "적중"
      },
      {
        "stock": "코스피",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 94472.37094599937,
        "currentPrice": 126337.81580047587,
        "returnRate": -4.31603249803816,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 88.98921468675583
      },
      {
        "month": "2026-02",
        "rate": 94.50173902442815
      },
      {
        "month": "2026-03",
        "rate": 78.88562913078067
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
    "accuracy": 50,
    "totalCalls": 4,
    "successfulCalls": 2,
    "avgReturn": 12.56,
    "recentCalls": [
      {
        "stock": "서클",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 81517.87736155212,
        "currentPrice": 132475.81246548868,
        "returnRate": 17.34897762895364,
        "status": "적중"
      },
      {
        "stock": "엔비디아",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 52107.98317253953,
        "currentPrice": 115674.87943372579,
        "returnRate": 10.503935865530575,
        "status": "진행중"
      },
      {
        "stock": "엔비디아",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 141953.10019289202,
        "currentPrice": 126050.40704909537,
        "returnRate": 9.92630785155077,
        "status": "진행중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 66107.07324863617,
        "currentPrice": 59556.22623991364,
        "returnRate": 12.469939798360649,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 93.43480978017016
      },
      {
        "month": "2026-02",
        "rate": 93.56605907355316
      },
      {
        "month": "2026-03",
        "rate": 75.48567518733897
      }
    ]
  },
  {
    "id": "차영주",
    "name": "차영주",
    "platforms": [
      {
        "name": "유튜브",
        "color": "red"
      }
    ],
    "followers": "10K+",
    "accuracy": 100,
    "totalCalls": 9,
    "successfulCalls": 9,
    "avgReturn": 5.44,
    "recentCalls": [
      {
        "stock": "LG이노텍",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 109185.81508979328,
        "currentPrice": 147436.98725122347,
        "returnRate": -3.741521748107994,
        "status": "적중"
      },
      {
        "stock": "기아",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 128143.8723843325,
        "currentPrice": 115119.35074726981,
        "returnRate": 19.158421471883333,
        "status": "적중"
      },
      {
        "stock": "한국전력",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 121326.34087204411,
        "currentPrice": 57084.21680274171,
        "returnRate": -8.69002454555021,
        "status": "적중"
      },
      {
        "stock": "LG화학",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 87013.54357897394,
        "currentPrice": 76815.71970937781,
        "returnRate": 3.4852185677015246,
        "status": "적중"
      },
      {
        "stock": "에코프로머티",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 73347.83887728871,
        "currentPrice": 95651.16957567679,
        "returnRate": 5.012959749691532,
        "status": "적중"
      },
      {
        "stock": "이수페타시스",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 120137.24164198613,
        "currentPrice": 75192.82712773298,
        "returnRate": 10.196008826342968,
        "status": "적중"
      },
      {
        "stock": "원익IPS",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 124145.19447196567,
        "currentPrice": 144757.293622163,
        "returnRate": 10.59029893396632,
        "status": "적중"
      },
      {
        "stock": "심텍",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 121333.92125940496,
        "currentPrice": 79125.403147898,
        "returnRate": 16.875412817138603,
        "status": "적중"
      },
      {
        "stock": "SK스퀘어",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 139147.01118868223,
        "currentPrice": 111377.00339370323,
        "returnRate": -3.929845241047449,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 72.90479907725857
      },
      {
        "month": "2026-02",
        "rate": 83.46102855485654
      },
      {
        "month": "2026-03",
        "rate": 77.85637231573848
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
    "totalCalls": 5,
    "successfulCalls": 5,
    "avgReturn": 11.96,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 75821.61972911771,
        "currentPrice": 145042.16815712245,
        "returnRate": 18.13556523898622,
        "status": "적중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 136047.2989479617,
        "currentPrice": 115224.70473331251,
        "returnRate": 18.16438392141623,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 68606.35849596263,
        "currentPrice": 83348.7983154282,
        "returnRate": 7.703373179777554,
        "status": "적중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 106598.10045283654,
        "currentPrice": 93362.66013286098,
        "returnRate": 13.976252798379367,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 57468.46009558081,
        "currentPrice": 104875.38848005419,
        "returnRate": 1.8418776208133067,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 93.90479412504129
      },
      {
        "month": "2026-02",
        "rate": 82.87058935780895
      },
      {
        "month": "2026-03",
        "rate": 70.39737656561712
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
    "totalCalls": 2,
    "successfulCalls": 2,
    "avgReturn": 6.57,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 135126.84395231341,
        "currentPrice": 64559.62424625573,
        "returnRate": 0.36349288339357955,
        "status": "적중"
      },
      {
        "stock": "LG전자",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 65920.85963905217,
        "currentPrice": 82120.6553885706,
        "returnRate": 12.779041723417059,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 71.92669206736554
      },
      {
        "month": "2026-02",
        "rate": 92.86335823254858
      },
      {
        "month": "2026-03",
        "rate": 94.26725628152053
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
    "accuracy": 50,
    "totalCalls": 4,
    "successfulCalls": 2,
    "avgReturn": -2.32,
    "recentCalls": [
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 144946.84456558223,
        "currentPrice": 69278.76653571798,
        "returnRate": -8.905119442635137,
        "status": "적중"
      },
      {
        "stock": "현대차",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 84665.38803234612,
        "currentPrice": 123368.13451213735,
        "returnRate": 4.384120467410309,
        "status": "진행중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 148061.20005260213,
        "currentPrice": 126341.14457968886,
        "returnRate": 0.8962824094954751,
        "status": "진행중"
      },
      {
        "stock": "건설주",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 139491.3871567431,
        "currentPrice": 92524.94097036531,
        "returnRate": -5.661309928267055,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 89.09885352887196
      },
      {
        "month": "2026-02",
        "rate": 83.12432807798862
      },
      {
        "month": "2026-03",
        "rate": 72.09854636976996
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
    "avgReturn": 0.18,
    "recentCalls": [
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 101160.53331442561,
        "currentPrice": 143547.92887882955,
        "returnRate": 15.524765387628175,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 101041.10411722909,
        "currentPrice": 71305.42988876671,
        "returnRate": -7.367241498870615,
        "status": "진행중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 82840.84156504486,
        "currentPrice": 139169.12694895547,
        "returnRate": -3.789429003512982,
        "status": "적중"
      },
      {
        "stock": "SK하이닉스",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 125527.14268076405,
        "currentPrice": 119052.13527733949,
        "returnRate": -8.419000549896479,
        "status": "적중"
      },
      {
        "stock": "삼성전자",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 113223.875182777,
        "currentPrice": 73473.2786290712,
        "returnRate": 4.944746079239964,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 81.86134790096168
      },
      {
        "month": "2026-02",
        "rate": 77.24094852546264
      },
      {
        "month": "2026-03",
        "rate": 78.16515200768124
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
    "accuracy": 67,
    "totalCalls": 3,
    "successfulCalls": 2,
    "avgReturn": 3.7,
    "recentCalls": [
      {
        "stock": "구글(알파벳)",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 51219.38491010924,
        "currentPrice": 108363.12434850496,
        "returnRate": -9.316141927136918,
        "status": "진행중"
      },
      {
        "stock": "AMD",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 90780.11116808976,
        "currentPrice": 93930.04176877756,
        "returnRate": 0.42127342416909386,
        "status": "적중"
      },
      {
        "stock": "엔비디아",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 93971.49290795159,
        "currentPrice": 127421.08490607243,
        "returnRate": 19.993105959029478,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 74.60042421047756
      },
      {
        "month": "2026-02",
        "rate": 74.84461576107415
      },
      {
        "month": "2026-03",
        "rate": 79.76939642030446
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
    "accuracy": 0,
    "totalCalls": 1,
    "successfulCalls": 0,
    "avgReturn": 17.76,
    "recentCalls": [
      {
        "stock": "신세계",
        "date": "2026-02-27",
        "direction": "매수",
        "callPrice": 145387.20395687642,
        "currentPrice": 112761.24062674647,
        "returnRate": 17.75548000255273,
        "status": "진행중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 78.73275116311814
      },
      {
        "month": "2026-02",
        "rate": 89.1217362726046
      },
      {
        "month": "2026-03",
        "rate": 76.29002408580831
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
    "avgReturn": 0.7,
    "recentCalls": [
      {
        "stock": "삼성전기",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 94965.85858124157,
        "currentPrice": 68573.40327239662,
        "returnRate": 0.7031857751756441,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 89.70642295700122
      },
      {
        "month": "2026-02",
        "rate": 80.19433701586863
      },
      {
        "month": "2026-03",
        "rate": 88.49270794724404
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
    "avgReturn": 3.33,
    "recentCalls": [
      {
        "stock": "현대차",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 106137.1374032948,
        "currentPrice": 70181.47170641608,
        "returnRate": 3.333628669263568,
        "status": "진행중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 83.228941921664
      },
      {
        "month": "2026-02",
        "rate": 91.94572047529137
      },
      {
        "month": "2026-03",
        "rate": 71.03003509882954
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
    "avgReturn": 1.41,
    "recentCalls": [
      {
        "stock": "LG화학",
        "date": "2026-02-27",
        "direction": "매도",
        "callPrice": 86393.46000762304,
        "currentPrice": 54767.17442919383,
        "returnRate": 1.407010037666085,
        "status": "적중"
      }
    ],
    "monthlyAccuracy": [
      {
        "month": "2026-01",
        "rate": 93.00163211459045
      },
      {
        "month": "2026-02",
        "rate": 87.38254820204276
      },
      {
        "month": "2026-03",
        "rate": 83.95956525248822
      }
    ]
  }
];
