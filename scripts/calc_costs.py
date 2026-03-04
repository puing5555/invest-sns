"""오늘 API 비용 정산 — 서브에이전트 announce 데이터 기반"""

# 서브에이전트 비용 (announce stats에서 추출)
subagents = [
    # (name, runtime, total_tokens_k, input_msgs, output_tokens_k)
    ("DEV-AB-TEST (V10.8vs9)", "4m16s", 200, 13, 13.9),
    ("RES-채널리서치2차", "8m20s", 200, 21, 33.8),
    ("PROMPT-V10.10", "42s", 135.6, 11, 1.6),
    ("DEV-STOCK-NAME-FIX", "1m59s", 200, 18, 6.3),
    ("QA-STOCKNAME-GATE", "1m31s", 200, 20, 3.9),
    ("PROMPT-V10.10-LENGTH", "40s", 131.4, 11, 1.8),
    ("DEV-PRICE-FIX", "6m47s", 200, 38, 16.4),
    ("DEV-GUEST-SPEAKER", "5m40s", 200, 27, 18.7),
    ("DEV-RETURN-FIX", "8m27s", 200, 67, 13.5),
    ("QA-SIGNAL-QUALITY", "4m32s", 200, 21, 13.2),
    ("QA-HAIKU-VS-SONNET", "3m23s", 200, 20, 6.3),
]

# Opus pricing: $15/M input, $75/M output, $1.875/M cache read
# But subagents are actually using default model (Opus) since sonnet override failed
# From the session data, subagents used Opus
# Cache read is dominant (~80% of input)

print("=" * 70)
print("오늘 API 비용 정산 (2026-03-04)")
print("=" * 70)

# 1. 서브에이전트 비용 (OpenClaw 통해 실행, Opus)
print("\n## 서브에이전트 비용 (Opus)")
total_sub = 0
for name, runtime, total_k, msgs, out_k in subagents:
    # Estimate: cache read ~80%, fresh input ~20%
    input_k = total_k - out_k
    cache_read_k = input_k * 0.8
    fresh_input_k = input_k * 0.2
    cost = (fresh_input_k * 15 + cache_read_k * 1.875 + out_k * 75) / 1000
    total_sub += cost
    print(f"  {name:35s} | {runtime:8s} | ~{total_k:.0f}K tok | out {out_k:.1f}K | ${cost:.2f}")

print(f"\n  서브에이전트 소계: ${total_sub:.2f}")

# 2. 메인 세션 (CTO Opus) - 3 sessions today ~200K each
print("\n## 메인 세션 (CTO Opus)")
# Estimated from context sizes
main_sessions = [
    ("Main session 1 (오전)", 200, 15),
    ("Main session 2 (오후1)", 200, 20),
    ("Main session 3 (오후2, 현재)", 200, 10),
    ("Group session", 200, 8),
]
total_main = 0
for name, total_k, out_k in main_sessions:
    input_k = total_k - out_k
    cache_read_k = input_k * 0.85
    fresh_input_k = input_k * 0.15
    cost = (fresh_input_k * 15 + cache_read_k * 1.875 + out_k * 75) / 1000
    total_main += cost
    print(f"  {name:35s} | ~{total_k}K tok | out ~{out_k}K | ${cost:.2f}")

print(f"\n  메인 세션 소계: ${total_main:.2f}")

# 3. 이효석 692개 시그널 추출 (이전 세션, Sonnet)
print("\n## 이효석 692개 시그널 추출 (Sonnet, 이전 세션)")
# ~100K input per batch * ~7 batches + output
hs_input = 700  # K tokens
hs_output = 200  # K tokens
# Sonnet: $3/M input, $15/M output
hs_cost = (hs_input * 3 + hs_output * 15) / 1000
print(f"  입력: ~{hs_input}K tok | 출력: ~{hs_output}K tok | ${hs_cost:.2f}")

# 4. Summary 보강 702건 (진행중, Sonnet 예상)
print("\n## Summary 보강 702건 (Sonnet, 진행중)")
sum_input = 702 * 0.25  # 250 tokens each
sum_output = 702 * 0.2  # 200 tokens each
sum_cost = (sum_input * 3 + sum_output * 15) / 1000
print(f"  입력: ~{sum_input:.0f}K tok | 출력: ~{sum_output:.0f}K tok | ${sum_cost:.2f}")

# 5. 833개 전체 검증 (진행중)
print("\n## 833개 전체 검증 (Haiku+Sonnet, 진행중)")
# Haiku: 833 * 0.4K = 333K input, 833 * 0.1K = 83K output
haiku_cost = (333 * 0.25 + 83 * 1.25) / 1000  # Haiku 3 pricing
# Sonnet: ~200 * 0.4K = 80K input, 200 * 0.1K = 20K output  
sonnet_cost = (80 * 3 + 20 * 15) / 1000
audit_cost = haiku_cost + sonnet_cost
print(f"  Haiku 833건: ${haiku_cost:.2f}")
print(f"  Sonnet ~200건: ${sonnet_cost:.2f}")
print(f"  소계: ${audit_cost:.2f}")

# 6. 무료 도구
print("\n## 무료 도구 (API 비용 없음)")
print("  yfinance 가격 수집: $0.00")
print("  yt-dlp 영상 정보: $0.00")
print("  Supabase (무료 플랜): $0.00")

# 총합
total = total_sub + total_main + hs_cost + sum_cost + audit_cost
print("\n" + "=" * 70)
print(f"총합: ${total:.2f}")
print("=" * 70)
print(f"\n  서브에이전트 (Opus): ${total_sub:.2f}")
print(f"  메인 세션 (Opus): ${total_main:.2f}")  
print(f"  이효석 추출 (Sonnet): ${hs_cost:.2f}")
print(f"  Summary 보강 (Sonnet): ${sum_cost:.2f}")
print(f"  전체 검증 (Haiku+Sonnet): ${audit_cost:.2f}")
