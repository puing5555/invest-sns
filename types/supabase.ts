/**
 * Supabase Database Types
 * 기본 스키마 타입 정의 (자동 생성 대신 수동 정의)
 * 
 * 실제 프로덕션에서는 다음 명령으로 자동 생성:
 * npx supabase gen types typescript --project-id arypzhotxflimroprmdk
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      // 사용자 프로필 테이블
      user_profiles: {
        Row: {
          id: string
          email: string
          display_name: string | null
          avatar_url: string | null
          dashboard_preferences: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          display_name?: string | null
          avatar_url?: string | null
          dashboard_preferences?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          display_name?: string | null
          avatar_url?: string | null
          dashboard_preferences?: Json
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      
      // 사용자 보유 종목 테이블
      user_stocks: {
        Row: {
          id: string
          user_id: string
          stock_code: string
          stock_name: string
          market: string
          quantity: number
          avg_buy_price: number
          total_investment: number
          first_bought_at: string
          last_updated_at: string
          notes: string | null
        }
        Insert: {
          id?: string
          user_id: string
          stock_code: string
          stock_name: string
          market: string
          quantity: number
          avg_buy_price: number
          first_bought_at?: string
          last_updated_at?: string
          notes?: string | null
        }
        Update: {
          id?: string
          user_id?: string
          stock_code?: string
          stock_name?: string
          market?: string
          quantity?: number
          avg_buy_price?: number
          first_bought_at?: string
          last_updated_at?: string
          notes?: string | null
        }
        Relationships: []
      }
      
      // 사용자 관심 종목 테이블
      user_watchlist: {
        Row: {
          id: string
          user_id: string
          stock_code: string
          stock_name: string
          market: string
          alert_on_signals: boolean
          alert_price_target: number | null
          alert_price_type: string | null
          added_at: string
          notes: string | null
        }
        Insert: {
          id?: string
          user_id: string
          stock_code: string
          stock_name: string
          market: string
          alert_on_signals?: boolean
          alert_price_target?: number | null
          alert_price_type?: string | null
          added_at?: string
          notes?: string | null
        }
        Update: {
          id?: string
          user_id?: string
          stock_code?: string
          stock_name?: string
          market?: string
          alert_on_signals?: boolean
          alert_price_target?: number | null
          alert_price_type?: string | null
          added_at?: string
          notes?: string | null
        }
        Relationships: []
      }
      
      // 사용자 알림 설정 테이블
      user_notification_settings: {
        Row: {
          user_id: string
          enabled: boolean
          portfolio_alerts: boolean
          watchlist_alerts: boolean
          price_alerts: boolean
          analyst_reports: boolean
          market_summary: boolean
          ai_insights: boolean
          email_enabled: boolean
          push_enabled: boolean
          updated_at: string
        }
        Insert: {
          user_id: string
          enabled?: boolean
          portfolio_alerts?: boolean
          watchlist_alerts?: boolean
          price_alerts?: boolean
          analyst_reports?: boolean
          market_summary?: boolean
          ai_insights?: boolean
          email_enabled?: boolean
          push_enabled?: boolean
          updated_at?: string
        }
        Update: {
          user_id?: string
          enabled?: boolean
          portfolio_alerts?: boolean
          watchlist_alerts?: boolean
          price_alerts?: boolean
          analyst_reports?: boolean
          market_summary?: boolean
          ai_insights?: boolean
          email_enabled?: boolean
          push_enabled?: boolean
          updated_at?: string
        }
        Relationships: []
      }
      
      // 사용자 알림 기록 테이블
      user_notifications: {
        Row: {
          id: string
          user_id: string
          type: string
          title: string
          message: string
          stock_code: string | null
          is_read: boolean
          created_at: string
          read_at: string | null
          metadata: Json
        }
        Insert: {
          id?: string
          user_id: string
          type: string
          title: string
          message: string
          stock_code?: string | null
          is_read?: boolean
          created_at?: string
          read_at?: string | null
          metadata?: Json
        }
        Update: {
          id?: string
          user_id?: string
          type?: string
          title?: string
          message?: string
          stock_code?: string | null
          is_read?: boolean
          created_at?: string
          read_at?: string | null
          metadata?: Json
        }
        Relationships: []
      }

      // 기존 테이블들 (참고용)
      influencer_signals: {
        Row: {
          id: string
          ticker: string
          signal: string
          confidence: number
          key_quote: string
          created_at: string
          video_id: string
          review_status: string
        }
        Insert: {
          id?: string
          ticker: string
          signal: string
          confidence: number
          key_quote: string
          created_at?: string
          video_id: string
          review_status?: string
        }
        Update: {
          id?: string
          ticker?: string
          signal?: string
          confidence?: number
          key_quote?: string
          created_at?: string
          video_id?: string
          review_status?: string
        }
        Relationships: []
      }
      
      influencer_videos: {
        Row: {
          id: string
          title: string
          published_at: string
          channel_id: string
        }
        Insert: {
          id?: string
          title: string
          published_at: string
          channel_id: string
        }
        Update: {
          id?: string
          title?: string
          published_at?: string
          channel_id?: string
        }
        Relationships: []
      }
      
      influencer_channels: {
        Row: {
          id: string
          channel_name: string
          influencer_id: string
        }
        Insert: {
          id?: string
          channel_name: string
          influencer_id: string
        }
        Update: {
          id?: string
          channel_name?: string
          influencer_id?: string
        }
        Relationships: []
      }
      
      influencers: {
        Row: {
          id: string
          name: string
        }
        Insert: {
          id?: string
          name: string
        }
        Update: {
          id?: string
          name?: string
        }
        Relationships: []
      }
    }
    Views: {
      user_personalized_signals: {
        Row: {
          user_id: string
          source_type: string
          id: string
          ticker: string
          signal: string
          confidence: number
          key_quote: string
          created_at: string
          video_id: string
          review_status: string
        }
        Relationships: []
      }
    }
    Functions: {
      create_user_notification: {
        Args: {
          p_user_id: string
          p_type: string
          p_title: string
          p_message: string
          p_stock_code?: string
          p_metadata?: Json
        }
        Returns: string
      }
      check_user_stock_duplicates: {
        Args: {}
        Returns: {
          user_id: string
          stock_code: string
          count: number
        }[]
      }
      check_user_watchlist_duplicates: {
        Args: {}
        Returns: {
          user_id: string
          stock_code: string
          count: number
        }[]
      }
    }
    Enums: {
      // 필요에 따라 추가
    }
    CompositeTypes: {
      // 필요에 따라 추가
    }
  }
}