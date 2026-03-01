/**
 * 클라이언트 사이드에서 Anthropic API를 호출하기 위한 유틸리티
 * CORS 제한을 우회하기 위해 corsproxy.io를 사용
 * API 키는 런타임에 입력받아 sessionStorage에 저장
 */

const CORS_PROXY = 'https://corsproxy.io/';
const ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages';

function getApiKey(): string {
  // sessionStorage에서 먼저 확인
  if (typeof window !== 'undefined') {
    const stored = sessionStorage.getItem('anthropic_api_key');
    if (stored) return stored;

    // 없으면 프롬프트로 입력받기
    const key = prompt('Anthropic API Key를 입력하세요 (세션 동안 유지됩니다):');
    if (key && key.trim()) {
      sessionStorage.setItem('anthropic_api_key', key.trim());
      return key.trim();
    }
    throw new Error('API 키가 입력되지 않았습니다.');
  }
  throw new Error('브라우저 환경에서만 사용 가능합니다.');
}

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
  const apiKey = getApiKey();

  try {
    const response = await fetch(CORS_PROXY + '?' + ANTHROPIC_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const errorData = await response.text();
      if (response.status === 401) {
        // 잘못된 키면 삭제
        sessionStorage.removeItem('anthropic_api_key');
        throw new Error('API 키가 유효하지 않습니다. 페이지를 새로고침하고 다시 입력하세요.');
      }
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
