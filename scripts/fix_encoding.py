#!/usr/bin/env python3
# Fix VALID_SIGNALS encoding corruption
with open(r'C:\Users\Mario\work\invest-sns\scripts\godofIT_analyze.py', 'rb') as f:
    content = f.read()

lines = content.split(b'\r\n')
for i, line in enumerate(lines):
    if b'VALID_SIGNALS' in line:
        print(f'Line {i+1}: {repr(line)}')
        # Replace with correct UTF-8 Korean
        # 매수=\xeb\xa7\xa4\xec\x88\x98, 긍정=\xea\xb8\x8d\xec\xa0\x95
        # 중립=\xec\xa4\x91\xeb\xa6\xbd, 부정=\xeb\xb6\x80\xec\xa0\x95, 매도=\xeb\xa7\xa4\xeb\x8f\x84
        maesu = '\ub9e4\uc218'.encode('utf-8')
        geungjeong = '\uae0d\uc815'.encode('utf-8')
        junglib = '\uc911\ub9bd'.encode('utf-8')
        bujeong = '\ubd80\uc815'.encode('utf-8')
        maedo = '\ub9e4\ub3c4'.encode('utf-8')
        
        quote = b"'"
        good_line = b"    VALID_SIGNALS = {" + quote + maesu + quote + b", " + quote + geungjeong + quote + b", " + quote + junglib + quote + b", " + quote + bujeong + quote + b", " + quote + maedo + quote + b"}"
        print('Good line:', good_line.decode('utf-8'))
        lines[i] = good_line
        break

new_content = b'\r\n'.join(lines)
with open(r'C:\Users\Mario\work\invest-sns\scripts\godofIT_analyze.py', 'wb') as f:
    f.write(new_content)
print('Done!')
