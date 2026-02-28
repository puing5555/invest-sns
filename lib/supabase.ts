import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// 신호 한글↔영문 매핑 함수
export const signalMapping = {
  '매수': 'BUY',
  '긍정': 'POSITIVE',
  '중립': 'NEUTRAL',
  '경계': 'CONCERN',
  '매도': 'SELL'
} as const;

export const reverseSignalMapping = {
  'BUY': '매수',
  'POSITIVE': '긍정',
  'NEUTRAL': '중립',
  'CONCERN': '경계',
  'SELL': '매도'
} as const;

// 신호별 색상 매핑
export const getSignalColor = (signal: string) => {
  switch (signal) {
    case '매수':
    case 'BUY': 
      return 'bg-green-100 text-[#22c55e] border-green-200';
    case '긍정':
    case 'POSITIVE': 
      return 'bg-blue-100 text-[#3182f6] border-blue-200';
    case '중립':
    case 'NEUTRAL': 
      return 'bg-yellow-100 text-[#eab308] border-yellow-200';
    case '경계':
    case 'CONCERN': 
      return 'bg-orange-100 text-[#f97316] border-orange-200';
    case '매도':
    case 'SELL': 
      return 'bg-red-100 text-[#ef4444] border-red-200';
    default: 
      return 'bg-gray-100 text-gray-600 border-gray-200';
  }
};

// 최신 승인된 시그널들을 가져오는 함수
export async function getLatestInfluencerSignals(limit = 20) {
  try {
    const { data, error } = await supabase
      .from('influencer_signals')
      .select(`
        *,
        influencer_videos (
          title,
          published_at,
          channel_id,
          influencer_channels (
            channel_name,
            channel_handle
          )
        ),
        speakers (
          name
        )
      `)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching latest signals:', error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error('Error in getLatestInfluencerSignals:', error);
    return [];
  }
}

// 인플루언서 채널 목록과 시그널 수를 가져오는 함수
export async function getInfluencerChannels() {
  try {
    const { data, error } = await supabase
      .from('influencer_channels')
      .select(`
        *,
        influencer_signals!inner (
          id
        )
      `);

    if (error) {
      console.error('Error fetching influencer channels:', error);
      return [];
    }

    // 채널별 시그널 수 계산
    const channelsWithSignalCount = await Promise.all(
      (data || []).map(async (channel) => {
        const { count } = await supabase
          .from('influencer_signals')
          .select('*', { count: 'exact', head: true })
          .in('video_id', 
            await supabase
              .from('influencer_videos')
              .select('id')
              .eq('channel_id', channel.id)
              .then(({ data: videos }) => videos?.map(v => v.id) || [])
          );

        return {
          ...channel,
          totalSignals: count || 0
        };
      })
    );

    return channelsWithSignalCount;
  } catch (error) {
    console.error('Error in getInfluencerChannels:', error);
    return [];
  }
}

// 종목별 시그널 그룹핑
export async function getStockSignalGroups() {
  try {
    const { data, error } = await supabase
      .from('influencer_signals')
      .select(`
        stock,
        ticker,
        id,
        speakers (
          name
        )
      `);

    if (error) {
      console.error('Error fetching stock signals:', error);
      return [];
    }

    // 종목별로 그룹핑
    const stockGroups = (data || []).reduce((acc: any, signal) => {
      const stockKey = signal.stock;
      if (!acc[stockKey]) {
        acc[stockKey] = {
          name: signal.stock,
          ticker: signal.ticker,
          mentionCount: 0,
          speakers: new Set()
        };
      }
      acc[stockKey].mentionCount++;
      if (signal.speakers?.name) {
        acc[stockKey].speakers.add(signal.speakers.name);
      }
      return acc;
    }, {});

    // 배열로 변환하고 언급 수순 정렬
    return Object.values(stockGroups)
      .map((group: any) => ({
        ...group,
        topSpeakers: Array.from(group.speakers).slice(0, 3),
        otherCount: Math.max(0, group.speakers.size - 3)
      }))
      .sort((a: any, b: any) => b.mentionCount - a.mentionCount);
  } catch (error) {
    console.error('Error in getStockSignalGroups:', error);
    return [];
  }
}

// 특정 채널의 정보와 시그널을 가져오는 함수
export async function getInfluencerProfile(channelHandle: string) {
  try {
    // 채널 정보 가져오기
    const { data: channelData, error: channelError } = await supabase
      .from('influencer_channels')
      .select('*')
      .eq('channel_handle', channelHandle)
      .single();

    if (channelError) {
      console.error('Error fetching channel:', channelError);
      return null;
    }

    // 해당 채널의 시그널들 가져오기
    const { data: signalsData, error: signalsError } = await supabase
      .from('influencer_signals')
      .select(`
        *,
        influencer_videos (
          title,
          published_at,
          video_id
        ),
        speakers (
          name
        )
      `)
      .in('video_id', 
        await supabase
          .from('influencer_videos')
          .select('id')
          .eq('channel_id', channelData.id)
          .then(({ data: videos }) => videos?.map(v => v.id) || [])
      )
      .order('created_at', { ascending: false });

    if (signalsError) {
      console.error('Error fetching signals:', signalsError);
      return { ...channelData, signals: [] };
    }

    return {
      ...channelData,
      signals: signalsData || []
    };
  } catch (error) {
    console.error('Error in getInfluencerProfile:', error);
    return null;
  }
}

// 발언자 이름으로 프로필 + 시그널 가져오기
export async function getInfluencerProfileBySpeaker(speakerName: string) {
  try {
    // 1) speaker_id가 이름인 경우 직접 조회
    let { data: signals, error } = await supabase
      .from('influencer_signals')
      .select(`
        *,
        influencer_videos (
          title,
          published_at,
          video_id,
          influencer_channels (
            channel_name,
            channel_handle
          )
        ),
        speakers (
          name
        )
      `)
      .eq('speaker_id', speakerName)
      .order('created_at', { ascending: false });

    // 2) 결과 없으면 speakers 테이블에서 이름으로 UUID 찾아서 재조회
    if ((!signals || signals.length === 0) && !error) {
      const { data: speakerRows } = await supabase
        .from('speakers')
        .select('id')
        .eq('name', speakerName);

      if (speakerRows && speakerRows.length > 0) {
        const speakerIds = speakerRows.map((s: any) => s.id);
        const { data: signals2, error: error2 } = await supabase
          .from('influencer_signals')
          .select(`
            *,
            influencer_videos (
              title,
              published_at,
              video_id,
              influencer_channels (
                channel_name,
                channel_handle
              )
            ),
            speakers (
              name
            )
          `)
          .in('speaker_id', speakerIds)
          .order('created_at', { ascending: false });

        if (!error2) {
          signals = signals2;
          error = error2;
        }
      }
    }

    if (error) {
      console.error('Error fetching speaker signals:', error);
      return null;
    }

    return {
      speakerName,
      signals: signals || [],
      totalSignals: signals?.length || 0,
      stocks: [...new Set(signals?.map(s => s.stock).filter(Boolean))],
      channels: [...new Set(signals?.map(s => s.influencer_videos?.influencer_channels?.channel_name).filter(Boolean))],
    };
  } catch (error) {
    console.error('Error in getInfluencerProfileBySpeaker:', error);
    return null;
  }
}

// 특정 종목의 시그널을 가져오는 함수
export async function getStockSignals(ticker: string) {
  try {
    const { data, error } = await supabase
      .from('influencer_signals')
      .select(`
        *,
        influencer_videos (
          title,
          published_at,
          video_id,
          video_summary,
          channel_id,
          influencer_channels (
            channel_name,
            channel_handle
          )
        ),
        speakers (
          name
        )
      `)
      .eq('ticker', ticker)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching stock signals:', error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error('Error in getStockSignals:', error);
    return [];
  }
}
