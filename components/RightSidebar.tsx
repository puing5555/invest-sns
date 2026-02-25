export default function RightSidebar() {
  const trends = [
    { tag: '#비트코인', posts: '84.2K 게시물' },
    { tag: '#NVIDIA실적', posts: '23.1K 게시물' },
    { tag: '#코스피2500', posts: '15.7K 게시물' },
    { tag: '#이더리움스테이킹', posts: '9.8K 게시물' },
    { tag: '#삼성전자실적', posts: '7.2K 게시물' },
  ];

  const recommendedUsers = [
    { name: '김작가', username: '@writer_kim' },
    { name: '부동산왕', username: '@realestate_king' },
    { name: '퀀트투자', username: '@quant_invest' },
  ];

  return (
    <div className="hidden xl:flex flex-col w-[320px] h-screen sticky top-0">
      <div className="px-4 py-6 space-y-6">
        {/* Search Bar */}
        <div className="sticky top-6">
          <div className="relative">
            <input
              type="text"
              placeholder="검색"
              className="w-full bg-[#f7f9fa] border border-[#e5e7eb] rounded-full px-6 py-3 text-[#111827] placeholder-[#6b7280] focus:outline-none focus:border-[#00d4aa]"
            />
            <svg
              className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[#6b7280]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
        </div>

        {/* Trends Box */}
        <div className="bg-[#f7f9fa] border border-[#e5e7eb] rounded-xl p-4">
          <h3 className="font-bold text-xl mb-4 text-[#111827]">무슨 일이 일어나고 있나요?</h3>
          <div className="space-y-3">
            {trends.map((trend, index) => (
              <div
                key={index}
                className="hover:bg-[#e5e7eb] p-3 rounded-lg cursor-pointer transition-colors"
              >
                <p className="font-bold text-[#00d4aa]">{trend.tag}</p>
                <p className="text-sm text-[#6b7280]">{trend.posts}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Accounts */}
        <div className="bg-[#f7f9fa] border border-[#e5e7eb] rounded-xl p-4">
          <h3 className="font-bold text-xl mb-4 text-[#111827]">팔로우할 계정</h3>
          <div className="space-y-4">
            {recommendedUsers.map((user, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                    <span className="text-[#111827] font-medium">
                      {user.name[0]}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-[#111827]">{user.name}</p>
                    <p className="text-sm text-[#6b7280]">{user.username}</p>
                  </div>
                </div>
                <button className="bg-white text-black px-4 py-1.5 rounded-full font-medium hover:bg-gray-200 transition-colors">
                  팔로우
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}