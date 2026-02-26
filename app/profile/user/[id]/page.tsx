import { notFound } from 'next/navigation'
import UserProfileClient from './UserProfileClient'

// Mock data
const mockUsers = {
  'dev-investor': {
    id: 'dev-investor',
    nickname: '투자하는개발자',
    avatar: '💻',
    level: 7,
    joinDate: '2024-03-15',
    followers: 1247,
    following: 892,
    interests: ['IT', '반도체', '바이오', 'ESG'],
    stats: {
      posts: 156,
      likes: 2847,
      watchedStocks: 23,
      memos: 89
    },
    posts: [
      {
        id: '1',
        content: '삼성전자 AI 반도체 전망에 대해 어떻게 생각하시나요? HBM 수요 증가로 실적 개선이 기대되는데...',
        date: '2026-02-26',
        likes: 24,
        comments: 8,
        stock: '삼성전자'
      },
      {
        id: '2',
        content: 'NAVER 클라우드 사업 분석 포스팅 작성했습니다. 클릭해서 확인해보세요!',
        date: '2026-02-25',
        likes: 67,
        comments: 15
      }
    ],
    comments: [
      {
        id: '1',
        content: '좋은 분석이네요. 특히 장기적 관점에서 봤을 때 매력적인 것 같습니다.',
        date: '2026-02-26',
        postTitle: 'SK하이닉스 실적 전망'
      }
    ],
    watchedStocks: [
      {
        code: '005930',
        name: '삼성전자',
        addedDate: '2026-01-15',
        currentPrice: '74,200',
        change: '+1.8%'
      },
      {
        code: '035420',
        name: 'NAVER',
        addedDate: '2026-01-20',
        currentPrice: '198,500',
        change: '-0.5%'
      }
    ],
    memos: [
      {
        id: '1',
        title: 'AI 반도체 관련 종목 정리',
        date: '2026-02-25',
        stock: '삼성전자',
        content: 'HBM3E 양산 본격화로 메모리 반도체 업황 개선 기대...'
      }
    ]
  }
}

export default function UserProfile({ params }: { params: { id: string } }) {
  const user = mockUsers[params.id as keyof typeof mockUsers]
  
  if (!user) {
    notFound()
  }
  
  return <UserProfileClient user={user} />
}

export async function generateStaticParams() {
  return [
    { id: 'dev-investor' }
  ]
}