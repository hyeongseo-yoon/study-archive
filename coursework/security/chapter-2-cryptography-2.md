# Chapter 2-3: Cryptographic Tools - 2

## 1. Block Cipher Modes of Operation (simplified) *(슬라이드 p.3~11)*

블록 암호는 한 블록(예: DES는 64bit)씩만 암호화할 수 있음 — 긴 메시지를 여러 블록으로 어떻게 처리할지 정하는 것이 "mode of operation". 이 자료에서는 5가지 모드(ECB, CBC, CFB, OFB, CTR) 중 **ECB**와 **CTR**만 다룸(나머지는 시간 관계상 스킵). *(p.4)*

### Electronic Codebook (ECB) Mode *(p.5~7)*
- **가장 단순한 모드**: plaintext를 64bit(DES 기준)씩 나눠, **각 블록을 같은 키로 독립적으로 암호화**
  ```
  Cᵢ = Encrypt_K(Pᵢ)   (각 블록이 서로 독립)
  ```
- 복호화도 마찬가지로 블록 단위, 항상 같은 키 사용
- **적합한 용도**: 암호화 키처럼 **짧은 데이터**를 암호화할 때 이상적
- **특징이자 약점**: 같은 plaintext 블록은 항상 같은 ciphertext 블록을 만듦 → **긴 메시지**에는 안전하지 않을 수 있음(패턴이 그대로 노출됨)

### Counter (CTR) Mode *(p.8~11)*
- 최근 ATM 네트워크 보안, IPSec 등에 적용이 늘어난 모드
- **counter 값이 각 plaintext 블록마다 달라야 함** (SP 800-38A의 요구사항) — counter를 어떤 값으로 초기화한 뒤, 블록마다 1씩 증가시킴
- 동작: `Cᵢ = Pᵢ ⊕ Encrypt_K(Counter+i)` / 복호화는 `Pᵢ = Cᵢ ⊕ Encrypt_K(Counter+i)` (스트림 암호처럼 XOR로 동작, **암호화 함수만** 필요)
- **장점** *(p.10~11)*:
  - **Hardware efficiency**: 여러 블록을 병렬로 처리 가능
  - **Software efficiency**: 병렬 처리를 지원하는 프로세서를 효과적으로 활용 가능
  - **Preprocessing**: plaintext/ciphertext의 실제 입력값과 무관하게 `Encrypt_K(Counter+i)` 부분을 미리 계산해둘 수 있음
  - **Random access**: i번째 블록을 순서와 무관하게 임의 접근(random access) 방식으로 처리 가능
  - **Provable security**: 다른 모드들만큼 안전함이 증명됨
  - **Simplicity**: **암호화 알고리즘만 구현**하면 되고 복호화 알고리즘은 구현할 필요 없음(복호화도 암호화 함수로 수행), decryption용 key scheduling도 구현할 필요 없음

---

## 2. AES (simplified) *(슬라이드 p.13~15)*

### 개요 *(p.13)*
- **AES (Advanced Encryption Standard)**: NIST가 2001년 11월 26일 US FIPS PUB 197로 발표
- **non-Feistel cipher** (Feistel 구조가 아님)
- Block size: **128 bit**
- Round 수: **10, 12, 14 rounds** (key size에 따라)
- Key size: **128, 192, or 256 bit** (라운드 수와 대응)

### 전체 구조 *(p.14~15)*
- 데이터 블록은 **4열×4바이트의 state**로 취급
- 키는 **word 배열로 확장(expand)**됨
- 각 라운드에서 state는 다음 연산들을 거침:
  - **Byte substitution**: 모든 바이트에 1개의 S-box 적용
  - **Shift rows**: 그룹(열) 사이에서 바이트를 순열(permute)
  - **Mix columns**: 그룹의 행렬곱을 이용한 치환
  - **Add round key**: state와 key material을 XOR
  - → 전체적으로 "**키와 XOR ↔ 데이터 뒤섞기**"가 번갈아 반복되는 구조로 볼 수 있음
- **초기 XOR** key material이 있고, **마지막 라운드는 불완전**(mix columns 생략)
- 빠른 XOR와 테이블 조회로 구현 가능
- Encryption/Decryption 다이어그램: Round1~Round10을 거치며 각 라운드에서 확장된 키(w[0,3], w[4,7], ..., w[40,43])를 사용, 복호화는 역순으로 inverse 연산(inverse sub bytes, inverse shift rows, inverse mix cols) 적용

---

## 3. Public Key Cryptography, RSA (simplified) *(슬라이드 p.17~49)*

### Symmetric encryption의 한계 *(p.18)*
- **Key distribution 문제**: 두 통신 당사자가 미리 키를 공유하고 있거나, key distribution center(KDC)를 써야 함 — KDC가 뚫리면 전체가 위험
- **디지털 서명(digital signature)**에 쓰기 어려움

### Public-Key Cryptosystems 원리 *(p.19~26)*
- **두 개의 분리된 키**(public key, private key) 사용
- **공개키와 알고리즘만 알아도 개인키를 알아내는 것은 계산적으로 불가능(infeasible)**해야 함
- 보통 public key로 암호화, private key로 복호화. RSA 같은 일부 알고리즘은 **어느 쪽으로 암호화해도 다른 쪽으로 복호화 가능**
- **6가지 구성요소**: Plaintext, Encryption algorithm, Ciphertext, Decryption algorithm, Public key, Private key *(p.20)*
- **사용 절차** *(p.21)*: 각자 공개키/개인키 쌍을 생성 → 공개키는 공개 register에 게시, 개인키는 비밀 유지 → Bob이 Alice에게 보낼 땐 **Alice의 공개키**로 암호화 → Alice는 **자신의 개인키**로 복호화
- **Encryption 용도(비밀성)** *(p.22)*: Alice의 공개키로 암호화 → Alice의 개인키로만 복호화 가능(비밀성 제공)
- **Authentication 용도** *(p.24)*: Bob이 **자신의 개인키**로 암호화 → 누구나 Bob의 공개키로 복호화하며 "Bob만 만들 수 있었다"는 것을 검증 (인증 제공, 단 비밀성은 없음 — 공개키를 아는 누구나 복호화 가능)
- **Secrecy + Authentication 결합** *(p.26)*: A가 자신의 개인키(PRa)로 먼저 암호화한 뒤 B의 공개키(PUb)로 다시 암호화 → B는 자신의 개인키(PRb)로 복호화한 뒤 A의 공개키(PUa)로 다시 복호화하여 원본 X 복원. 이렇게 하면 인증과 비밀성을 동시에 만족

### 응용 분야 *(p.27)*
- **Encryption/decryption**(비밀성 제공), **Digital signatures**(인증 제공), **Key exchange**(세션키 교환)
- 알고리즘마다 지원 범위가 다름: RSA/Elliptic Curve는 세 가지 모두 지원, Diffie-Hellman은 key exchange만, DSS는 digital signature만

### Requirements for Public-Key Cryptography *(p.28~32)*
Diffie와 Hellman이 제시한 조건들 (A가 B에게 메시지를 보낼 때):
1. B가 공개키/개인키 쌍을 쉽게 생성할 수 있어야 함
2. A가 B의 공개키로 `C = E_KUb(M)`을 쉽게 계산할 수 있어야 함
3. B가 자신의 개인키로 `M = D_KRb(C) = D_KRb[E_KUb(M)]`을 쉽게 계산할 수 있어야 함
4. 공격자가 공개키 `KUb`만 알고서는 개인키 `KRb`를 알아내는 것이 **infeasible**해야 함
5. 공격자가 공개키 `KUb`와 ciphertext `C`만 알고서는 원본 `M`을 복원하는 것이 **infeasible**해야 함
6. (선택) 암복호화 함수를 어느 순서로 적용해도 동일: `M = E_KUb[D_KRb(M)] = D_KUb[E_KRb(M)]`

- 이 요구사항들이 까다로워서 실제로 널리 쓰이는 건 **RSA**와 **elliptic curve cryptography** 정도뿐 *(p.30)*
- 이런 요구사항을 만족하려면 **trap-door one-way function**이 필요:
  - **one-way function**: 순방향 계산(`Y=f(X)`)은 쉽지만 역방향(`X=f⁻¹(Y)`) 계산은 불가능(infeasible)에 가까움. 여기서 "easy"=다항 시간에 풀림, "infeasible"=거의 모든 입력에 대해 역산이 어려움(최악의 경우나 평균적인 경우가 아니라) *(p.31)*
  - **trap-door one-way function**: 한 방향은 쉽고 반대 방향도 **추가 정보(trapdoor, k)를 알면** 쉽지만, 그 정보를 모르면 infeasible *(p.32)*:
    ```
    Y = f_k(X)     : k와 X를 알면 쉬움
    X = f_k⁻¹(Y)   : k와 Y를 알면 쉬움
    X = f_k⁻¹(Y)   : Y만 알고 k를 모르면 infeasible
    ```
  - 실용적인 public-key 스킴의 개발은 결국 적합한 trap-door one-way function을 찾는 문제로 귀결됨

### Public-Key Cryptanalysis *(p.33~34)*
- **Brute-force attack (개인키 대상)**: 대응책은 큰 키 사용 — 무차별 대입을 비현실적으로 만들면서도 실용적인 암복호화가 가능한 크기여야 함
- **공개키로부터 개인키를 직접 계산**: 아직 이 공격으로부터 안전함이 증명된 알고리즘은 없음
- **Probable-message attack**: 메시지가 (예: 56bit DES 키처럼) 후보가 제한적인 값이라면, 공격자가 가능한 모든 후보를 공개키로 암호화해서 ciphertext와 대조해 알아낼 수 있음. 대응책: 큰 키 크기, 메시지에 임의 비트를 덧붙이기

### The RSA Algorithm *(p.35~49)*
- 1977년 MIT의 Rivest, Shamir, Adleman이 개발
- **block cipher**로, plaintext/ciphertext는 `0`부터 `n-1` 사이의 정수. 일반적인 n 크기는 1024bit(309 십진자리), `n = pq` *(p.35)*
- 블록 크기는 `k`bit (`2^k < n ≤ 2^(k+1)`) *(p.36)*
- **암복호화 공식** *(p.37)*:
  ```
  C = M^e mod n
  M = C^d mod n = (M^e)^d mod n = M^(ed) mod n
  ```
  공개키 = `{e,n}`, 개인키 = `{d,n}`
- RSA에 대한 Diffie-Hellman 요구사항 대응 *(p.38)*: e,d,n을 쉽게 찾을 수 있어야 함 / `M^e` 계산이 쉬워야 함 / `C^d` 계산이 쉬워야 함 / e,n만으로 d를 찾는 게 infeasible해야 함
- **첫 번째 요구사항**: 모든 `M<n`에 대해 `M^(ed) = M mod n`을 만족하는 e,d,n을 쉽게 찾을 수 있어야 함 *(p.39)*
- **Euler's theorem의 따름정리**: 소수 p,q, `n=pq`, `0<m<n`, 임의의 정수 k에 대해 *(p.40)*
  ```
  m^(kφ(n)+1) ≡ m mod n
  m^(k(p-1)(q-1)+1) ≡ m mod n
  ```
  여기서 `Φ(n)`은 오일러 totient 함수(n보다 작고 n과 서로소인 양의 정수의 개수)
- e,d를 `ed = kΦ(n)+1`을 만족하도록 고르면 `M^(ed)=M mod n`을 만족함. 이는 `ed ≡ 1 mod Φ(n)`, 즉 `d ≡ e⁻¹ mod Φ(n)`과 동치 — 이것이 성립하려면 **e(따라서 d)가 Φ(n)과 서로소**여야 함 (`gcd(Φ(n),e)=1`) *(p.41)*
- **RSA의 재료** *(p.42)*:
  - `p, q` (두 소수) — private, 직접 선택
  - `n = pq` — public, 계산됨
  - `e` (`gcd(Φ(n),e)=1`, `1<e<Φ(n)`) — public, 선택됨
  - `d ≡ e⁻¹ mod Φ(n)` — private, 계산됨
  - 공개키 = `{e,n}`, 개인키 = `{d,n}`
- **RSA 스킴 동작** *(p.43)*: B가 A에게 메시지 M을 보내려 할 때, A의 공개키 `KU={e,n}`으로 B가 `C=M^e mod n`을 계산해 전송 → A는 개인키 `KR={d,n}`으로 `M=C^d mod n` 복호화
- **수치 예시** *(p.44~45)*:
  ```
  p=17, q=11 → n=pq=187
  Φ(n)=(p-1)(q-1)=16×10=160
  e=7 (Φ(n)과 서로소)
  de=1 mod 160을 만족하는 d=23 (extended Euclid's algorithm)

  암호화: plaintext 88 → 88^7 mod 187 = 11 (ciphertext)
    88^1 mod187=88, 88^2 mod187=77, 88^4 mod187=132
    88^7 mod187 = (88×77×132) mod187 = 894,432 mod187 = 11
  복호화: 11^23 mod187 = 88 (원문 복원)
    11^1=11, 11^2=121, 11^4=55, 11^8=33
    11^23 mod187 = (11×121×55×33×33) mod187 = 79,720,243 mod187 = 88
  ```

### The Security of RSA *(p.46~49)*
공격 방식 3가지: **Brute force**, **Mathematical attacks**, **Timing attacks**
- **Brute force**: 가능한 모든 개인키를 시도 — 대응책은 큰 키 공간 사용
- **Mathematical attacks** *(p.47)*: 세 가지 접근이 사실상 동등한 난이도
  1. `n`을 두 소인수로 분해(factoring) → `Φ(n)`과 `d` 계산 가능
  2. `p,q`를 거치지 않고 `Φ(n)`을 직접 알아냄 (이는 n을 factoring하는 것과 동등)
  3. `Φ(n)`을 거치지 않고 `d`를 직접 알아냄 (현재 알려진 알고리즘으로는 factoring 문제만큼 시간이 걸림)
- **소인수분해 기록** *(p.48)*: 자릿수가 늘수록 필요한 계산량(MIPS-years)이 기하급수적으로 증가 (예: 100자리(1991)→7 MIPS-years, 200자리(2005)→Lattice sieve로 해결). 이 추세 때문에 RSA는 시간이 지날수록 더 큰 키를 요구
- **p, q 선택 시 제약사항** *(p.49)*: `n`이 쉽게 소인수분해되지 않도록
  - p와 q는 자릿수가 몇 자리 이상 차이나면 안 됨(너무 가까워도, 너무 멀어도 안 됨 — 비슷한 길이 유지)
  - `(p-1)`과 `(q-1)` 모두 큰 소인수를 포함해야 함
  - `gcd(p-1, q-1)`은 작아야 함
  - 추가로, `e<n`이고 `d<n^(1/4)`이면 d를 쉽게 알아낼 수 있음이 증명되어 있음 → d가 너무 작으면 안 됨

---

## 4. One-way Hash Functions (simplified) *(슬라이드 p.50~55)*

### 개념 *(p.51)*
- 임의 길이의 메시지를 **고정 크기로 압축(condense)**: `h = H(M)`
- 예: `SHA1("The quick brown fox jumps over the lazy cog") = 0xde9f2c7f...`
- 보통 hash function은 **public이고 keyed되어 있지 않다고 가정** (cf. MAC은 keyed)
- 메시지 변경 탐지에 hash를 활용한 것이 **HMAC**
- 다양한 용도: 비밀번호 저장, 고유 file_id 생성, 그리고 가장 흔하게는 **디지털 서명 생성**

### One-way Hash Function의 요구사항 *(p.52)*
1. 임의 크기의 메시지 M에 적용 가능
2. 고정 길이 출력 h 생성
3. 임의의 M에 대해 `h=H(M)` 계산이 쉬워야 함(easy to compute)
4. 주어진 h에 대해 `H(x)=h`를 만족하는 x를 찾는 것이 infeasible — **one-way property**
5. 주어진 x에 대해 `H(y)=H(x)`인 y를 찾는 것이 infeasible — **weak collision resistance**
6. 임의의 `x,y`쌍으로 `H(y)=H(x)`를 찾는 것이 infeasible — **strong collision resistance**

### 응용 *(p.53)*
Message Authentication Code(MAC), 비밀번호 저장, Digital Signature

### 표준 해시함수와 Birthday Attack *(p.54~55)*
- 표준 암호학적 해시함수: MD5, SHA-1, SHA-256/384/512, RIPEMD160 등 (세부 알고리즘은 생략)
- **Birthday Attack**: 64bit 해시가 안전해 보여도, **Birthday Paradox** 때문에 실제로는 그렇지 않음
  - 공격자가 유효한 메시지의 변형 `2^(m/2)`개, 사기용(fraudulent) 메시지의 변형 `2^(m/2)`개를 각각 생성
  - 두 집합을 비교해 **같은 해시값**을 갖는 쌍을 찾음(birthday paradox에 의해 확률 > 0.5)
  - 정상 메시지에 서명을 받은 뒤, 같은 해시를 가진 위조 메시지로 바꿔치기 → 위조 메시지도 유효한 서명을 갖게 됨
  - **결론**: 이런 공격을 막으려면 **더 큰 MAC/hash**를 써야 함

---

## 5. Digital Signatures (simplified) *(슬라이드 p.56~59)*

### 목적 *(p.57)*
디지털 서명은 인증(authentication)에 더해 다음 능력을 제공:
- 메시지 내용 인증(authenticate message contents)
- 서명자와 서명 일시 검증(verify author, date & time)
- **제3자가 검증하여 분쟁을 해결**할 수 있음 (일반 MAC과의 핵심 차이)

### 디지털 서명이 가져야 할 성질 *(p.58~59)*
- 서명은 **서명 대상 메시지에 의존하는 bit pattern**이어야 함
- **서명자에게 고유한 정보**를 사용해야 함 — 위조(forgery)와 부인(denial) 모두 방지
- 서명 생성이 비교적 쉬워야 함
- 서명의 인식/검증이 비교적 쉬워야 함
- 서명 사본을 저장해두는 것이 실용적이어야 함
- **계산적으로 위조가 불가능**해야 함 — 기존 서명에 대해 새 메시지를 만들거나, 주어진 메시지에 대해 사기 서명을 만드는 것 모두 불가능해야 함

### Direct Digital Signature *(p.61)*
- **가정**: 송신자와 수신자만 관여, 수신자가 송신자의 공개키를 가지고 있음
- **서명 방법**: 메시지 전체를 개인키로 암호화 / 또는 해시를 계산한 뒤 해시값을 개인키로 암호화 / 또는 전용 서명 생성 알고리즘 사용
- **문제점**: 위 가정을 어떻게 현실적으로 만족시킬지, 송신자가 개인키를 분실하면 어떻게 되는지 — (자세한 내용은 Chapter 14에서 다룸, 여기서는 스킵)

### RSA Digital Signature Algorithm *(p.62)*
- 단순 암호화(위 다이어그램의 위쪽): `E_KRa(M)` — 메시지 전체를 A의 개인키로 암호화, B가 A의 공개키로 복호화
- 해시 기반 서명(아래쪽, 실용적 방식): A가 메시지 M을 해시(`H(M)`)한 뒤 **해시값만 개인키로 암호화**하여 **Digital Signature**(`E_KRa[H(M)]`)를 만듦 → 원본 메시지 M과 함께 전송
  - B는 받은 M을 다시 해시하고, 서명을 A의 공개키로 복호화한 값과 **비교(Compare)**하여 검증
- **3단계 흐름**: ① Digital Signature Creation (원본 메시지 + 발신자 개인키로 서명 생성) → ② Send Message (원본 메시지 + 서명 함께 전송) → ③ Digital Signature Verification (발신자 공개키로 서명 검증, valid/invalid 판정)

---

## 핵심 요약

- **Block cipher mode**: 같은 블록 암호(예: AES, DES)라도 여러 블록을 어떻게 연결하느냐로 안전성이 갈림 — ECB는 단순하지만 패턴이 드러나고, CTR은 병렬화/랜덤 접근이 가능하며 암호화 함수만으로 암복호화 가능
- **AES**: non-Feistel, 128bit 블록, 10/12/14 라운드, byte substitution/shift rows/mix columns/add round key의 반복
- **Public-key cryptography**는 symmetric 암호의 키 분배·서명 문제를 해결하기 위해 등장, **trap-door one-way function**(공개키/개인키 비대칭성)을 기반으로 함
- **RSA**: `n=pq`, `Φ(n)=(p-1)(q-1)`, `ed≡1 mod Φ(n)`을 만족하는 (e,n)=공개키, (d,n)=개인키로 `C=M^e mod n`, `M=C^d mod n` — 안전성은 사실상 **n의 소인수분해 난이도**에 의존
- **One-way hash function**은 임의 길이 메시지를 고정 길이로 압축하며 one-way성과 (약/강) collision resistance를 만족해야 함 — 해시 크기가 작으면 **birthday attack**에 취약
- **Digital signature**는 해시값을 개인키로 암호화하는 방식(RSA 기반)으로 구현되어, 인증뿐 아니라 부인방지(non-repudiation)까지 제공
