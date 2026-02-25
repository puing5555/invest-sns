import { useParams } from 'next/navigation';
import Link from 'next/link';

// User data mapping
const USER_DATA = {
  korini_papa: { name: '코린이아빠', type: 'influencer', accuracy: 68, followers: '12.3K' },
  doctor_stock: { name: '주식하는의사', type: 'influencer', accuracy: 72, followers: '8.9K' },
  valueup_lab: { name: '밸류업연구소', type: 'influencer', accuracy: 75, followers: '15.2K' },
  system: { name: 'A등급 공시 속보', type: 'system' },
  rookie_kim: { name: '주식초보 김대리', type: 'normal', followers: '234' },
  swing_master: { name: '스윙매매 전문가', type: 'normal', followers: '1.2K' },
  dividend_lover: { name: '배당쟁이', type: 'normal', followers: '567' },
  office_trader: { name: '직장인투자자', type: 'normal', followers: '89' },
  busan_bull: { name: '부산사나이', type: 'normal', followers: '156' },
  soyeon_chart: { name: '차트쟁이 소연', type: 'normal', followers: '445' },
  dividend_newbie: { name: '배당초보', type: 'normal', followers: '12' },
  ant_veteran: { name: '10년차 개미', type: 'normal', followers: '890' },
  quant_minsu: { name: '퀀트개발자 민수', type: 'normal', followers: '2.1K' },
  working_mom: { name: '워킹맘 투자', type: 'normal', followers: '234' },
  us_stock_newbie: { name: '해외주식도전기', type: 'normal', followers: '123' },
  swing_pro: { name: '스윙장인', type: 'normal', followers: '345' },
  careful_investor: { name: '신중파', type: 'normal', followers: '567' },
  semi_mania: { name: '반도체매니아', type: 'normal', followers: '789' },
  data_lover: { name: '데이터분석가', type: 'normal', followers: '456' },
  follow_master: { name: '따라쟁이', type: 'normal', followers: '234' },
  value_only: { name: '가치투자자', type: 'normal', followers: '1.1K' },
};

// Generate static params for build
export async function generateStaticParams() {
  return Object.keys(USER_DATA).map((username) => ({
    username,
  }));
}

export default function ProfilePage({ params }: { params: { username: string } }) {
  const { username } = params;
  const user = USER_DATA[username as keyof typeof USER_DATA];

  if (!user) {
    return <div className="p-4 text-center">사용자를 찾을 수 없습니다.</div>;
  }

  const getAvatar = () => {
    if (user.type === 'system') {
      return (
        <div className="w-16 h-16 rounded-full bg-[#3182f6] flex items-center justify-center text-white text-2xl">
          🤖
        </div>
      );
    }
    
    const avatarMap: { [key: string]: number } = {
      korini_papa: 11, doctor_stock: 15, rookie_kim: 32, swing_master: 22,
      valueup_lab: 52, dividend_lover: 44, office_trader: 33, busan_bull: 28,
      soyeon_chart: 47, dividend_newbie: 19, ant_veteran: 36, quant_minsu: 55,
      working_mom: 24, us_stock_newbie: 41, swing_pro: 25, careful_investor: 30,
      semi_mania: 35, data_lover: 40, follow_master: 45, value_only: 50
    };
    
    return (
      <img 
        src={`https://i.pravatar.cc/150?img=${avatarMap[username] || 1}`}
        alt={user.name}
        className="w-16 h-16 rounded-full object-cover"
      />
    );
  };

  const getBadge = () => {
    if (user.type === 'system') {
      return <div className="text-sm text-[#8b95a1] mt-2">🤖 투자SNS 공식 계정입니다</div>;
    }
    
    if (user.type === 'influencer') {
      return (
        <div className="flex items-center gap-2 mt-2">
          <span className="text-blue-500">✅ 인증 인플루언서</span>
          <span className="text-xs bg-[#f2f4f6] px-2 py-1 rounded">
            적중률 {user.accuracy}%
          </span>
          <span className="text-sm text-[#8b95a1]">팔로워 {user.followers}</span>
        </div>
      );
    }
    
    return (
      <div className="text-sm text-[#8b95a1] mt-2">
        가입일 2025.01 · 팔로워 {user.followers}
      </div>
    );
  };

  const dummyPosts = [
    {
      id: 1,
      text: "오늘도 좋은 하루 되세요! 투자는 신중하게 💪",
      time: "2시간전",
      likes: 12,
      comments: 3
    },
    {
      id: 2, 
      text: "시장이 많이 흔들리네요. 이럴 때일수록 기본에 충실해야겠습니다.",
      time: "1일전",
      likes: 45,
      comments: 8
    }
  ];

  return (
    <div className="bg-[#f4f4f4] min-h-screen">
      {/* Header with gradient */}
      <div className="bg-gradient-to-r from-[#3182f6] to-[#1b64da] h-32 relative">
        <div className="absolute -bottom-8 left-4">
          {getAvatar()}
        </div>
      </div>

      {/* Profile Info */}
      <div className="bg-white px-4 pt-12 pb-4 border-b border-[#f0f0f0]">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-[#191f28]">{user.name}</h1>
            <p className="text-[#8b95a1]">@{username}</p>
            {getBadge()}
          </div>
          <button className="bg-[#3182f6] text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-[#1b64da] transition-colors">
            팔로우
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[#f0f0f0] bg-white">
        <button className="flex-1 py-3 text-[15px] font-bold text-[#191f28] relative">
          게시물
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-14 h-1 rounded-full bg-[#3182f6]" />
        </button>
        <button className="flex-1 py-3 text-[15px] font-medium text-[#8b95a1]">
          콜
        </button>
        <button className="flex-1 py-3 text-[15px] font-medium text-[#8b95a1]">
          좋아요
        </button>
      </div>

      {/* Posts */}
      <div className="bg-white">
        {dummyPosts.map((post) => (
          <article key={post.id} className="px-4 py-3 border-b border-[#f0f0f0]">
            <div className="flex gap-3">
              {getAvatar()}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1 mb-1">
                  <span className="font-bold text-[15px] text-[#191f28]">
                    {user.name}
                  </span>
                  <span className="text-sm text-[#8b95a1]">@{username}</span>
                  <span className="text-sm text-[#8b95a1]"> · {post.time}</span>
                </div>
                <div className="text-[15px] text-[#191f28] leading-[1.4] mb-2">
                  {post.text}
                </div>
                <div className="flex items-center gap-6 text-[#8b95a1] text-sm">
                  <span>💬 {post.comments}</span>
                  <span>❤️ {post.likes}</span>
                </div>
              </div>
            </div>
          </article>
        ))}
        
        <div className="text-center py-8 text-[#8b95a1] text-sm">
          더 많은 게시물을 보려면 팔로우하세요
        </div>
      </div>
    </div>
  );
}