'use client'

import { useState } from 'react'

interface UserData {
  id: string
  nickname: string
  avatar: string
  level: number
  joinDate: string
  followers: number
  following: number
  interests: string[]
  stats: {
    posts: number
    likes: number
    watchedStocks: number
    memos: number
  }
  posts: Array<{
    id: string
    content: string
    date: string
    likes: number
    comments: number
    stock?: string
  }>
  comments: Array<{
    id: string
    content: string
    date: string
    postTitle: string
  }>
  watchedStocks: Array<{
    code: string
    name: string
    addedDate: string
    currentPrice: string
    change: string
  }>
  memos: Array<{
    id: string
    title: string
    date: string
    stock?: string
    content: string
  }>
}

type TabType = 'posts' | 'comments' | 'stocks' | 'memos'

export default function UserProfileClient({ user }: { user: UserData }) {
  const [activeTab, setActiveTab] = useState<TabType>('posts')
  
  const getLevelColor = (level: number) => {
    if (level >= 10) return 'bg-purple-100 text-purple-700 border-purple-200'
    if (level >= 5) return 'bg-blue-100 text-blue-700 border-blue-200'
    return 'bg-green-100 text-green-700 border-green-200'
  }
  
  const renderTabContent = () => {
    switch (activeTab) {
      case 'posts':
        return (
          <div className="space-y-4">
            {user.posts.map(post => (
              <div key={post.id} className="border border-[#e8e8e8] rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    {post.stock && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full border border-blue-200">
                        {post.stock}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-[#8b95a1]">{post.date}</span>
                </div>
                <p className="text-[#191f28] mb-3">{post.content}</p>
                <div className="flex gap-4 text-xs text-[#8b95a1]">
                  <span>❤️ {post.likes}</span>
                  <span>💬 {post.comments}</span>
                </div>
              </div>
            ))}
          </div>
        )
      
      case 'comments':
        return (
          <div className="space-y-4">
            {user.comments.map(comment => (
              <div key={comment.id} className="border border-[#e8e8e8] rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-medium text-[#191f28]">{comment.postTitle}</span>
                  <span className="text-xs text-[#8b95a1]">{comment.date}</span>
                </div>
                <p className="text-[#191f28]">{comment.content}</p>
              </div>
            ))}
          </div>
        )
      
      case 'stocks':
        return (
          <div className="space-y-3">
            {user.watchedStocks.map(stock => (
              <div key={stock.code} className="border border-[#e8e8e8] rounded-lg p-4 flex justify-between items-center">
                <div>
                  <div className="font-medium text-[#191f28]">{stock.name}</div>
                  <div className="text-xs text-[#8b95a1]">{stock.addedDate} 추가</div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-[#191f28]">{stock.currentPrice}원</div>
                  <div className={`text-xs ${stock.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {stock.change}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      
      case 'memos':
        return (
          <div className="space-y-4">
            {user.memos.map(memo => (
              <div key={memo.id} className="border border-[#e8e8e8] rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-[#191f28]">{memo.title}</span>
                    {memo.stock && (
                      <span className="px-2 py-1 bg-gray-100 text-[#191f28] text-xs rounded-full border border-gray-200">
                        {memo.stock}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-[#8b95a1]">{memo.date}</span>
                </div>
                <p className="text-[#191f28] text-sm">{memo.content}</p>
              </div>
            ))}
          </div>
        )
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <div className="flex gap-5 items-start">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0">
            {user.avatar}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-xl font-bold text-[#191f28]">{user.nickname}</h1>
              <span className={`px-2 py-1 text-xs rounded-full border ${getLevelColor(user.level)}`}>
                Lv.{user.level}
              </span>
            </div>
            
            <div className="flex gap-6 mb-4 text-sm text-[#8b95a1]">
              <div>
                <div className="font-semibold text-[#191f28]">{user.joinDate}</div>
                <div>가입일</div>
              </div>
              <div>
                <div className="font-semibold text-[#191f28]">{user.followers.toLocaleString()}</div>
                <div>팔로워</div>
              </div>
              <div>
                <div className="font-semibold text-[#191f28]">{user.following.toLocaleString()}</div>
                <div>팔로잉</div>
              </div>
            </div>
            
            {/* Interest Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              {user.interests.map(interest => (
                <span
                  key={interest}
                  className="px-2 py-1 bg-gray-100 text-[#191f28] text-xs rounded-full border border-gray-200"
                >
                  {interest}
                </span>
              ))}
            </div>
          </div>
          
          <button className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors">
            팔로우
          </button>
        </div>
      </div>
      
      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{user.stats.posts}</div>
          <div className="text-sm text-[#8b95a1]">게시글</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{user.stats.likes.toLocaleString()}</div>
          <div className="text-sm text-[#8b95a1]">받은 좋아요</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{user.stats.watchedStocks}</div>
          <div className="text-sm text-[#8b95a1]">관심 종목</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{user.stats.memos}</div>
          <div className="text-sm text-[#8b95a1]">메모</div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg">
        <div className="flex border-b border-[#e8e8e8]">
          {[
            { id: 'posts', label: '게시글' },
            { id: 'comments', label: '댓글' },
            { id: 'stocks', label: '관심종목' },
            { id: 'memos', label: '메모' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 bg-blue-50'
                  : 'border-transparent text-[#8b95a1] hover:text-[#191f28]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}