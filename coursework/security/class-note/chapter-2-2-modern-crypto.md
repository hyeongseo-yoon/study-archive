# Chapter 2-2 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*(수업일: 2026-10-22, 참조 노트: `notes/chapter-2-2-modern-crypto.md`)*

수업 목표: "안전한 암호"가 뭔지 수학적으로 정의하고, 왜 Perfect Secrecy(OTP)에서 Computational Secrecy로 넘어갈 수밖에 없었는지 자기 말로 설명할 수 있게 되기.

## 1. Modern Cryptography란 *(p.3~7)*

**Modern Cryptography**: 암호를 "만들고 → 깨지면 고치는" 경험적 기술(art)이 아니라, 안전성을 **정의하고, 가정을 명시하고, 증명**하는 과학(science)으로 다루는 접근.

- 고전 암호(Caesar, Vigenère, Enigma...)는 전부 **build → break → repeat**였음
- 질문이 바뀜: "이 암호가 안전하다는 걸 **증명**할 수 있을까?" → 증명하려면 먼저 "안전하다"의 **정의**가 필요
- 1980년대 초부터 art에서 science로 전환

3대 원칙:
1. **Formal definitions**: "안전하다"를 정밀한 수학적 모델로 규정
2. **Assumptions**: 가정을 명시적이고 모호하지 않게 서술. 대부분 계산적 가정(예: 소인수분해는 어렵다)에 의존하며, P≠NP를 증명해도 부족할 정도로 더 강한 가정
3. **Proofs of security**: 그 가정 하에서 구성이 정의를 만족함을 엄밀히 증명. 단 **채택한 정의와 가정에 상대적인** 보장

Q&A — 증명했는데도 "절대 안 깨진다"고 말할 수 없는 이유:
- 증명은 **"정의 + 가정 ⇒ 안전"**이라는 조건부 명제. 둘 중 하나가 어긋나면 결론이 무너짐
- **정의가 현실보다 좁은 경우**: "도청만 하는 공격자"로 정의했다면 ciphertext 변조, 전력 소비 측정(side-channel)은 보장 밖
- **가정이 깨진 경우**: "소인수분해는 어렵다"가 무너지면(예: 양자컴퓨터) 그 위의 증명도 같이 무너짐
- 그래도 가치가 큰 이유: 무엇을 믿고(가정) 무엇을 막는지(정의)가 명시되어 검토·반박이 가능. 어디를 의심해야 하는지 처음부터 알 수 있음

---

## 2. Defining Secure Encryption *(p.9~18)*

**Secure encryption의 정의**: 공격자가 plaintext에 대해 이미 가진 사전 정보가 무엇이든, ciphertext가 추가 정보를 전혀 알려주지 않는 암호화.

### 정의의 두 요소 *(p.9)*
- **Security guarantee**: 공격자가 못 하게 막으려는 것
- **Threat model**: 공격자가 할 수 있다고 가정하는 현실적 능력 (ciphertext-only < known-plaintext < chosen-plaintext < chosen-ciphertext, 2-1장의 4단계와 같은 축)

### Private-key encryption의 형식적 정의 *(p.10~11)*
message space `M`과 세 알고리즘 (Gen, Enc, Dec):
- **Gen** (Key Generation): 키 `k` 생성
- **Enc** (Encryption): 키 `k`와 `m ∈ M`을 받아 `c ← Enc_k(m)` 출력
- **Dec** (Decryption): 키 `k`와 `c`를 받아 `m := Dec_k(c)` 출력

양쪽이 같은 키 `k`를 공유하니까 "private-key(대칭키)".

### "안전하다"의 후보들 *(p.13~17)*
1. **"키를 알아내는 게 불가능하다"** *(p.13~14)*: 키는 목적이 아니라 수단. 필요조건이지 충분조건이 아님.
   - 반례 1: `Enc_k(m) = m` (키는 절대 안 드러나지만 암호화가 안 됨)
   - 반례 2: `Enc_k(m) = ( m의 앞 절반 || Enc'_k(m의 뒤 절반) )` (`Enc'`는 튼튼하다고 가정). 키는 안 새지만 plaintext 절반이 그대로 공개
   - 핵심: **키가 안 새는 것과 메시지가 안 새는 것은 별개**
2. **"ciphertext에서 plaintext 전체를 알아내는 게 불가능하다"** *(p.15)*: plaintext의 90%를 알아내도 통과
3. **"plaintext의 어떤 글자도 알아내는 게 불가능하다"** *(p.16)*: "salary가 $75K보다 크다" 같은 **부분 정보**는 샐 수 있음. 우연히 맞추거나 이미 알던 글자는 어떻게 판단할지도 애매
4. **올바른 정의** *(p.17)*: 공격자의 **사전 정보(prior information)**가 뭐든, ciphertext가 plaintext에 대한 **추가 정보**를 전혀 누설하지 않아야 함

후보는 키 → 전체 → 글자 → **어떤 정보든**으로 점점 강해짐.

---

## 3. Perfect Secrecy *(p.19~51)*

**Perfect Secrecy**: ciphertext를 관측해도 공격자가 메시지에 대해 가진 확률적 지식(M의 분포)이 전혀 바뀌지 않는 암호화.

### Probability 복습 *(p.20~23)*
- **Random variable**: 확률적으로 값을 취하는 변수
- **Event**: 실험에서의 특정 결과. `Pr[E]`는 사건 E의 확률
- **Conditional probability**: `Pr[A|B] = Pr[A and B] / Pr[B]`
- **Independence**: 모든 x, y에 대해 `Pr[X=x | Y=y] = Pr[X=x]`이면 독립 (Y를 알아도 X에 대한 지식이 안 바뀜)
- **Law of total probability**: `E_1,...,E_n`이 partition이면 `Pr[A] = Σᵢ Pr[A|Eᵢ] · Pr[Eᵢ]`

확인 문제: 주사위에서 A="짝수", B="4 이상". B={4,5,6} 중 짝수는 {4,6}이라 `Pr[A|B] = 2/3`, `Pr[A] = 1/2`이므로 독립이 아님.

### 표기와 확률 설정 *(p.24~28)*
- `K`: key space, `C`: ciphertext space
- **M** (random variable): 보낼 메시지. 분포는 공격자의 사전지식(어떤 메시지가 보내질 가능성이 높은지)을 반영
- **K** (random variable): 키. Gen이 분포를 정하며 보통 uniform이지만 항상 그런 건 아님
- **M과 K는 독립이라고 가정** (메시지를 보고 키를 고르거나 그 반대로 하지 않음)
- 실험: 1) Gen으로 `k` 생성 2) M의 분포대로 `m` 선택 3) `c ← Enc_k(m)`. 이 `c`를 나타내는 random variable이 **C**

### Example 1, 2: Shift cipher로 `Pr[C=c]` 계산 *(p.27~28)*
Shift cipher는 키 26개, `Pr[K=k] = 1/26`.
- **Ex1**: `Pr[M='a']=0.7, Pr[M='z']=0.3`일 때 'b'는 (a,k=1) 또는 (z,k=2). `Pr[C='b'] = 0.7·(1/26) + 0.3·(1/26) = 1/26`
- **Ex2**: `Pr[M='one']=Pr[M='ten']=1/2`일 때 'one'을 3칸 밀면 'rqh', 'ten'은 어떤 shift로도 'rqh'가 안 됨. `Pr[C='rqh'] = (1/26)(1/2) + 0·(1/2) = 1/52`

### Perfect Secrecy 정의 *(p.29~31)*
- **Informal**: 사전 정보가 뭐든 ciphertext가 추가 정보를 주면 안 됨. 공격자의 사전 정보 = **M의 분포를 아는 것**이므로, c를 본 뒤에도 M의 분포가 그대로여야 함
- **Formal**: (Gen, Enc, Dec)가 **perfectly secret**하다 = M에 대한 모든 분포, 모든 `m ∈ M`, `Pr[C=c] > 0`인 모든 `c ∈ C`에 대해
  ```
  Pr[M=m | C=c] = Pr[M=m]
  ```
- 좌변은 사후(c를 본 뒤), 우변은 사전. 같다는 건 M과 C가 **독립**이라는 뜻 (독립의 정의와 같은 모양)

### Example 3, 4: Shift cipher는 perfectly secret이 아님 *(p.32~38)*
- **Ex3**: `Pr[M='one']=Pr[M='ten']=1/2`, `c='rqh'` 관측. 'ten'은 'rqh'가 못 되므로 `Pr[M='ten' | C='rqh'] = 0 ≠ 1/2`. 공격자가 "'ten'은 아니구나" 하고 정보를 얻음
- **Bayes 정리**: `Pr[A|B] = Pr[B|A] · Pr[A] / Pr[B]`
- **Ex4**: `Pr[M='hi']=0.3, Pr[M='no']=0.2, Pr[M='in']=0.5`, `c='xy'` 관측. 'in'은 'xy'가 될 수 없음
  - `Pr[C='xy'] = (1/26)·0.3 + (1/26)·0.2 + 0·0.5 = 1/52`
  - `Pr[M='hi' | C='xy'] = (1/26 · 0.3) / (1/52) = 0.6`
  - 사전 0.3 → 사후 0.6으로 올라 정보가 샘
- **결론**: Shift cipher는 (최소 2글자 메시지에서) perfectly secret이 아님. 원인은 "키가 26개뿐이라 어떤 메시지는 어떤 ciphertext로 갈 수 없다"는 점

Q&A — perfectly secret이 되려면 키가 최소 몇 개?: 메시지가 n개면 최소 n개. 고정된 `c`에 대해 모든 메시지가 `c`가 될 가능성이 남아야 하고, 서로 다른 메시지가 같은 키로 같은 `c`가 되면 복호화가 모호해지므로 메시지마다 **다른 키**가 필요. 즉 `|K| ≥ |M|`.

### One-Time Pad *(p.38~46)*
**One-Time Pad(OTP)**: 메시지와 같은 길이의 완전 무작위 키를 XOR해서 암호화하고, 그 키를 딱 한 번만 쓰는 암호.

- 1917년 Vernam이 특허, 1949년 Shannon이 perfect secrecy를 증명 (역사적으로는 그보다 최소 35년 전에 이미 발명되었다는 연구도 있음)
- 정의: `M = {0,1}^n`, Gen은 `k ∈ {0,1}^n`을 균등하게 선택
  ```
  Enc_k(m) = k ⊕ m
  Dec_k(c) = k ⊕ c
  ```
- **Correctness**: `Dec_k(Enc_k(m)) = k⊕(k⊕m) = (k⊕k)⊕m = 0⊕m = m`
- 실사용 예: 워싱턴-모스크바 "red phone". 키 관리가 힘들어서 지금은 거의 안 씀

### OTP의 Perfect Secrecy 증명 *(p.41~44)*
직관: ciphertext `c`와 임의의 메시지 `m'`에 대해 `k = m' ⊕ c`인 키가 **정확히 하나** 존재. 키가 균등하니 모든 메시지가 똑같이 가능성이 남아서 c를 봐도 배울 게 없음.

M의 분포가 임의일 때:
```
Pr[C=c] = Σ_m' Pr[C=c | M=m'] · Pr[M=m']
        = Σ_m' Pr[K=m'⊕c] · Pr[M=m']     (M, K 독립)
        = Σ_m' 2^-n · Pr[M=m']
        = 2^-n
```
Bayes로:
```
Pr[M=m | C=c] = Pr[C=c | M=m] · Pr[M=m] / Pr[C=c]
              = 2^-n · Pr[M=m] / 2^-n
              = Pr[M=m]
```
사후 = 사전이므로 정의를 정확히 만족.

### OTP의 한계 *(p.47~50)*
1. **키가 메시지만큼 길어야 함**: 주고받을 모든 메시지 길이의 합만큼 키를 미리 안전하게 공유해야 해서 비현실적
2. **키는 딱 한 번만 써야 함**: 재사용하면 `c1 = k⊕m1`, `c2 = k⊕m2`에서
   - 공격자가 `m1`을 알면: `k = c1⊕m1` → `m2 = c2⊕k` (known-plaintext에 완전히 뚫림)
   - `m1`을 몰라도: `c1⊕c2 = m1⊕m2`가 되어 키가 소거되고 두 평문의 관계가 샘
3. 이 한계는 OTP만의 문제가 아니라 **perfect secrecy를 달성하는 모든 스킴의 본질적 한계**

Q&A — `c1⊕c2 = m1⊕m2`로 뭘 할 수 있나:
- **Crib dragging**: 평문에 들어갈 법한 단어(예: " the ", "Dear ")를 추측해 `m1⊕m2`의 각 위치에 XOR. 맞으면 그 자리에서 `m2`의 읽을 수 있는 영어 조각이 나오고, 틀리면 쓰레기 문자. 한 조각이 맞으면 `k = c1⊕m1`도 얻어 다른 부분도 풀림
- 자연어 평문은 빈도·구조가 뻔해서 잘 먹힘 (2-1장 Monoalphabetic 빈도분석과 같은 계열)
- 실제 사례: 2차대전 소련 외교 통신(VENONA)이 pad를 재사용해 일부가 해독됨
- 요점: 키가 직접 안 새도, 키가 소거된 순간 평문의 통계적 구조가 노출되어 깨짐

### OTP의 최적성 *(p.51)*
**정리**: (Gen, Enc, Dec)가 message space `M`에서 perfectly secret이면 `|K| ≥ |M|` (슬라이드는 증명 생략). 키 길이를 줄일 여지가 없으므로 OTP는 이미 최적.

---

## 4. Computational Secrecy *(p.52~73)*

**Computational Secrecy**: 무한한 계산 능력의 공격자가 아니라 **현실적인(효율적인) 공격자**만 막으면 되고, 아주 작은 확률의 실패는 허용하는 완화된 안전성.

Perfect secrecy는 "무한한 계산 능력을 가진 도청자에게조차" 안전해야 한다는 불필요하게 강한 요구라서 정의를 **완화**해야 함.

### 완화의 두 방향 *(p.54~57)*
1. 아주 작은 확률로 안전성이 실패하는 것을 허용
2. "효율적인" 공격자로 한정

숫자 감각:
- 실패 확률 `2^-60`: 송수신자가 내년에 벼락 맞을 확률보다 낮고, 초당 시도 시 약 1000억 년에 한 번
- 공격자 계산력: 데스크탑 ≈ `2^57` keys/year, 슈퍼컴퓨터 ≈ `2^80` keys/year, 빅뱅 이후 슈퍼컴퓨터로도 ≈ `2^112` keys. 현대 키 공간은 `2^128` 이상이므로 공격자를 `2^112`번 시도 정도로 제한해도 합리적

### Perfect Indistinguishability *(p.58~62)*
perfect secrecy를 **게임**으로 재정의. 실험 `PrivK_{A,Π}`:
1. 공격자 A가 `m0, m1 ∈ M`을 고름
2. `k ← Gen`, 무작위 비트 `b`, `c ← Enc_k(m_b)` (challenge ciphertext)를 A에게 줌
3. A가 `b'`를 출력, `b = b'`이면 A의 승리(실험 값 1)

모든 A에 대해 `Pr[PrivK_{A,Π} = 1] = 1/2`이면 **perfectly indistinguishable**. 이는 perfect secrecy와 **동치**.

### Concrete 버전: (t, ε)-indistinguishability *(p.63~66)*
시간 `≤ t`로 동작하는 모든 A에 대해 `Pr[PrivK_{A,Π} = 1] ≤ 1/2 + ε`. `(∞, 0)`이면 perfect와 같음.
- 단점: 계산 모델에 민감하고, 한 스킴이 여러 `(t, ε)`에 대해 성립해서 깔끔한 이론이 안 됨

### Asymptotic 버전 *(p.67~73)*
**Security parameter n**(지금은 키 길이로 생각)을 도입. 당사자들이 원하는 보안 수준으로 정하고 공격자도 n을 앎. 실행 시간과 성공 확률을 **n의 함수**로 측정.

- **Polynomial**: 어떤 c가 있어 `f(n) < n^c`
- **Negligible**: 모든 다항식 p에 대해 충분히 큰 n에서 `f(n) < 1/p(n)`. 전형적 예는 `poly(n)·2^-cn`
- **효율적 = PPT**(probabilistic polynomial-time), **안전 실패 = negligible**. 임의적 선택이지만 닫힘 성질이 편함:
  - poly × poly = poly (PPT가 PPT를 호출해도 PPT)
  - poly × negligible = negligible (다항 번 호출해도 실패 확률은 negligible)

**재정의된 스킴**: 세 PPT 알고리즘 (Gen, Enc, Dec)
- Gen: `1^n`을 받아 `k` 출력, `|k| ≥ n`
- Enc: `k`, `m ∈ {0,1}*`를 받아 `c ← Enc_k(m)` 출력
- Dec: `k`, `c`를 받아 `m` 또는 "error" 출력

**PrivK_{A,Π}(n)** 실험: 1) `A(1^n)`이 같은 길이의 `m0, m1 ∈ {0,1}*` 출력 2) `k ← Gen(1^n), b ← {0,1}, c ← Enc_k(m_b)` 3) `b' ← A(c)`, `b = b'`이면 성공.

**EAV-secure 정의** (eavesdropper = 도청자): 모든 PPT 공격자 A에 대해 negligible한 `ε`가 있어
```
Pr[PrivK_{A,Π}(n) = 1] ≤ 1/2 + ε(n)
```
이것이 computational indistinguishability.

Q&A — perfect secrecy 대비 풀어준 것:
- 공격자를 무한 계산력 → **PPT**로 제한
- 공격자의 advantage가 0이 아니라 **negligible**이면 허용
- 결과: `|K| ≥ |M|` 정리는 perfect secrecy에서만 성립하므로 **짧은 키로 긴 메시지** 암호화가 가능해짐 (짧은 키를 PRG로 늘려 OTP처럼 사용)

---

## 5. Constructing Primitives, Worlds in Crypto *(p.74~82)*

**Primitive**: 더 큰 암호 시스템을 짓는 데 쓰는 기본 빌딩 블록(OWF, PRG, PRF 등).

### 프리미티브와 환원 *(p.75~76)*
- 기본 프리미티브: OWF, PRG, PRF, PRP, Hashing, Digital signature, Secret-key encryption, Bit-commitment, Zero-knowledge proof
- **Foundational methodology**: 복잡한 걸 더 단순한 프리미티브로 **환원**해서 구성
  ```
  OWF → Hashing
  OWF → PRG → PRF → (Secret-key encryption)
  OWF → Digital Signatures
  ```
- 맨 밑바닥 OWF는 "well-studied, average-case hard" 문제(소인수분해, discrete log 등)에서 얻음

### Worlds in Crypto: Minicrypt vs Cryptomania *(p.77~78)*
- **Minicrypt**: OWF만 있으면 갈 수 있는 세계. hashing, PRG, PRF, PRP, secret-key encryption, digital signature 등
- **Cryptomania**: OWF만으론 부족하고 더 강한 가정(discrete-log, factoring 기반)이 필요한 세계. **Public-key encryption** 등
- 즉 대칭키 암호는 OWF만으로 되지만 공개키 암호는 더 강한 가정이 필요

### 현대 암호시스템의 계층 *(p.79)*
```
Basic Mathematical Facts (정보이론, 대수, 정수론, 확률론)
 → Cryptographic Primitives (OWF, Hashing)
 → Cryptographic Algorithms (PRG, PRF, PRP)
 → Cryptographic Schemes (대칭/공개키 암호, 서명, 비밀 공유)
 → Cryptographic Protocols
 → Cryptographic Systems (보안 서비스)
 → Information Security System
```

### One-way Function *(p.80~81)*
**One-way Function(OWF)**: 계산하기는 쉽지만 역으로 입력을 찾기는 (효율적으로) 어려운 함수.

형식 정의: 함수족 `{F_n}` (`F_n: {0,1}^n → {0,1}^{m(n)}`)가 one-way하다 = 모든 PPT 공격자 A에 대해 negligible한 `μ`가 있어
```
Pr[x ← {0,1}^n; y = F_n(x); A(1^n, y) = x' : y = F_n(x')] ≤ μ(n)
```
A는 원래 `x`가 아니라 `F_n(x') = y`인 **아무 역상**을 찾으면 성공. 무제한 시간이면 항상 찾을 수 있지만 PPT로는 어려워야 함.

알려진 사실:
- P=NP이면 OWF는 존재하지 않음
- OWF가 존재하면 P≠NP
- 역은 성립하지 않음 (P≠NP라고 OWF가 존재하는 건 아님)
- PRG가 존재하는 것은 OWF(와 hard-core predicate)가 존재하는 것과 동치

### Well-studied, average-case hard 문제 *(p.82)*
- NP-hard/complete 문제(3-colorability, TSP, knapsack 등)는 암호 가정으로 부적합 — **worst-case** 어려움이지 average-case 어려움이 아니라서 나중에 깨지는 경우가 많음
- 실제로 쓰이는 것: **DLP**(군 `G`에서 `b^k = a`인 `k` 찾기), **소인수분해**

Q&A — 왜 소인수분해/DLP가 선호되나:
- **Worst-case 어려움**: 가장 나쁜 입력 하나가 어려우면 성립. 대부분의 입력이 쉬워도 상관없음
- 암호는 키를 무작위로 뽑으므로 **평균적(typical) 입력에서 항상 어려워야** 함. 키가 우연히 쉬운 인스턴스가 되면 그 키로 쓴 암호가 뚫림 → 필요한 건 **average-case hardness**
- NP-complete 문제는 worst-case만 보장해서 무작위 인스턴스가 쉬울 수 있고, 실제로 이런 기반 스킴이 깨진 사례가 많음
- 소인수분해와 DLP는 수십 년간 연구됐는데도 무작위 인스턴스에서 효율적 알고리즘이 안 나옴

---

## 핵심 요약

- Modern crypto는 (1) formal definition (2) 명시적 assumption (3) security proof의 3원칙
- "안전한 암호화"의 정의는 "**사전 정보와 무관하게 ciphertext가 추가 정보를 누설하지 않아야 한다**"로 수렴
- 이를 확률론으로 formalize한 것이 **Perfect Secrecy**(`Pr[M=m|C=c]=Pr[M=m]`). Shift cipher는 불만족, **OTP**는 만족하며 `|K|≥|M|`이라 **최적**
- OTP는 키 길이/재사용 제약이 비현실적 → **Computational Secrecy**로 완화: **PPT 공격자**, **negligible 실패확률** (**EAV-security**)
- OWF를 기초로 PRG→PRF→PRP→secret-key encryption 등을 구성. OWF만으로 되는 **Minicrypt**와 더 강한 가정이 필요한 **Cryptomania**(public-key encryption)로 세계가 나뉨
