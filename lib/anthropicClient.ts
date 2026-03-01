/**
 * 클라이언트 사이드에서 Anthropic API를 호출하기 위한 유틸리티
 * Supabase Edge Function을 통해 Anthropic API를 프록시로 호출
 * API 키는 Edge Function 환경변수에 저장됨
 */

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';
const EDGE_FUNCTION_URL = `${SUPABASE_URL}/functions/v1/anthropic-proxy`;

interface AnthropicMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface AnthropicRequest {
  model: string;
  max_tokens: number;
  messages: AnthropicMessage[];
}

interface AnthropicResponse {
  content: Array<{
    type: 'text';
    text: string;
  }>;
}

export async function callAnthropicAPI(request: AnthropicRequest): Promise<string> {
  try {
    const response = await fetch(EDGE_FUNCTION_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'apikey': SUPABASE_ANON_KEY,
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Edge Function 오류:', errorData);
      throw new Error(`Anthropic API 오류 (${response.status}): ${errorData}`);
    }

    const data: AnthropicResponse = await response.json();
    return data.content[0].text;
  } catch (error) {
    console.error('Anthropic API 호출 실패:', error);
    throw error instanceof Error ? error : new Error('알 수 없는 오류가 발생했습니다.');
  }
}

export default { callAnthropicAPI };
