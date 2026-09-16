# Chapter 2-2: Modern Cryptography

*Lecture Notes (from J. Katz, S. Goldwasser 등)*

> 이 자료는 슬라이드에 쪽번호가 인쇄되어 있지 않아서, 아래 `p.N`은 PDF 파일 자체의 페이지 순서(1부터 시작)를 가리킨다.

## 1. Modern Cryptography란 *(p.3~7)*

### 배경 *(p.3~4)*
- 지금까지는 **heuristic construction**(build → break → repeat 반복)에 의존해왔음 — 만족스럽지 않은 방식
- 질문: 어떤 암호 스킴이 안전하다는 것을 **증명**할 수 있을까? → 먼저 "안전하다"는 게 뭔지 **정의**부터 필요
- 역사적으로 cryptography는 **art**(경험적 설계/분석)였지만, 1980년대 초부터 **science**로 발전

### Modern crypto의 3대 원칙 *(p.5~7)*
1. **Formal definitions**: "안전하다"는 것이 무엇을 뜻하는지 정밀한 수학적 모델/정의로 규정
2. **Assumptions**: 가정은 명시적이고 모호하지 않게 서술. 대부분의 암호학은 (P≠NP를 증명해도 충분하지 않을 정도로) **계산적 가정(computational assumptions)**에 의존함
3. **Proofs of security**: 특정 가정 하에서 구성이 정의를 만족함을 엄밀히 증명 — design-break-patch 사이클에서 벗어남. 다만 이 증명은 어디까지나 채택한 **정의와 가정**에 상대적인 보장(iron-clad guarantee *relative to* definition/assumptions)

---

## 2. Defining Secure Encryption *(p.9~18)*

### Crypto 정의의 일반 형태 *(p.9)*
- **Security guarantee/goal**: 우리가 달성하려는 것(또는 공격자가 달성 못하게 막으려는 것)
- **Threat model**: 공격자가 가진 것으로 가정하는 (현실적인) 능력

### Private(-key) encryption의 형식적 정의 *(p.10~11)*
Message space `M`과 알고리즘 (Gen, Enc, Dec)으로 정의:
- **Gen** (key-generation): 키 `k`를 생성
- **Enc** (encryption): 키 `k`와 메시지 `m ∈ M`을 입력받아 ciphertext `c ← Enc_k(m)` 출력
- **Dec** (decryption): 키 `k`와 ciphertext `c`를 입력받아 `m := Dec_k(c)` 출력

```
sender: m --[c ← Enc_k(m)]--> ciphertext c --(전송)--> receiver: m := Dec_k(c)
        (양쪽이 같은 키 k를 공유)
```

### Threat model 4단계 *(p.12)*
Ciphertext-only(하나 vs 여럿?) < Known-plaintext < Chosen-plaintext < Chosen-ciphertext attack — [[chapter-2-classical-encryption]]의 분류와 동일한 축.

### "안전하다"의 정의를 찾아가는 과정 — 각 후보의 문제점 *(p.13~17)*
- 후보 1: "공격자가 키를 알아내는 게 불가능" *(p.13~14)*
  - 문제: 키는 목적(means to an end)이지 목적 그 자체가 아님. 필요조건이지 충분조건이 아님. 키를 완전히 숨기면서도 안전하지 않은 스킴을 설계하기는 쉬움
- 후보 2: "공격자가 ciphertext로부터 plaintext를 알아내는 게 불가능" *(p.15)*
  - 문제: 공격자가 plaintext의 90%를 알아낸다면?
- 후보 3: "공격자가 plaintext의 어떤 글자도 알아내는 게 불가능" *(p.16)*
  - 문제: 공격자가 salary가 $75K보다 크다는 등 **부분 정보(partial information)**를 알아낸다면? 혹은 글자를 우연히 맞추거나 이미 알고 있었다면?
- **The right definition** *(p.17)*: "공격자가 plaintext에 대해 가진 **사전 정보(prior information)**가 무엇이든 상관없이, ciphertext는 plaintext에 대한 **추가 정보(additional information)**를 전혀 누설하지 않아야 한다" → 이를 어떻게 formalize할지가 다음 절의 주제

---

## 3. Perfect Secrecy *(p.19~51)*

### Probability 복습 *(p.20~23)*
- **Random variable**: 특정 확률로 (이산적) 값을 취하는 변수
- **Probability distribution**: 각 값에 대한 확률(0~1 사이, 합은 1)
- **Event**: 실험에서의 특정 발생. `Pr[E]` = 사건 E의 확률
- **Conditional probability**: `Pr[A|B] = Pr[A and B]/Pr[B]`
- **Independence**: 모든 x,y에 대해 `Pr[X=x|Y=y] = Pr[X=x]`이면 X,Y는 독립
- **Law of total probability**: `E_1,...,E_n`이 전체 경우의 partition이면, 모든 A에 대해 `Pr[A] = Σᵢ Pr[A and Eᵢ] = Σᵢ Pr[A|Eᵢ]·Pr[Eᵢ]`

### Notation과 확률분포 설정 *(p.24~28)*
- `K` (key space) = 가능한 모든 키의 집합, `C` (ciphertext space) = 가능한 모든 ciphertext의 집합
- `M` = 메시지 값을 나타내는 random variable(M의 분포는 문맥에 따라 다름, 공격자의 사전지식이 반영된 "메시지가 보내질 가능성")
- `K` = 키 값을 나타내는 random variable. Gen이 K의 분포를 정의 (`Pr[K=k] = Pr[Gen outputs key k]`, 보통 uniform이지만 항상 그런 건 아님)
- **M과 K는 독립이라고 가정** (당사자들이 메시지에 따라 키를 고르거나 그 반대로 하지 않음). 일반적으로 성립하는 가정이며, 성립하지 않으면 문제가 생길 수 있음
- 암호화 스킴 (Gen,Enc,Dec)과 M의 분포를 고정하면: 1) Gen으로 k 생성 2) 주어진 분포로 m 선택 3) `c ← Enc_k(m)` 계산 — 이 실험이 ciphertext에 대한 분포를 정의함. 이 값을 나타내는 random variable을 `C`라 함

### Example 1, 2 — Shift cipher로 Pr[C=c] 계산 *(p.27~28)*
- Shift cipher: `Pr[K=k]=1/26` (모든 k∈{0,...,25})
- Ex1: `Pr[M='a']=0.7, Pr[M='z']=0.3`일 때 `Pr[C='b'] = Pr[M='a']·Pr[K=1] + Pr[M='z']·Pr[K=2] = 0.7·(1/26)+0.3·(1/26) = 1/26`
- Ex2: `Pr[M='one']=Pr[M='ten']=1/2`일 때 `Pr[C='rqh'] = Pr[C='rqh'|M='one']·1/2 + Pr[C='rqh'|M='ten']·1/2 = 1/26·1/2 + 0·1/2 = 1/52`

### Perfect Secrecy (informal → formal) *(p.29~31)*
- **Informal**: "공격자가 plaintext에 대해 가진 사전 정보와 무관하게, ciphertext는 plaintext에 대한 추가 정보를 누설하지 않아야 한다"
- 공격자의 사전 정보 = **M의 분포**를 아는 것. Perfect secrecy = ciphertext를 관찰해도 공격자의 M의 분포에 대한 지식이 바뀌지 않아야 함
- **Formal 정의**: 암호화 스킴 (Gen,Enc,Dec)이 message space `M`, ciphertext space `C`에서 **perfectly secret**하다는 것은, `M`에 대한 모든 분포, 모든 `m∈M`, `Pr[C=c]>0`인 모든 `c∈C`에 대해
  ```
  Pr[M=m | C=c] = Pr[M=m]
  ```
  즉 ciphertext를 관측해도 M의 분포가 전혀 바뀌지 않음을 의미

### Example 3, 4 — Shift cipher는 perfectly secret이 아님 *(p.32~38)*
- Ex3: `Pr[M='one']=Pr[M='ten']=1/2`, m='ten', c='rqh'일 때 `Pr[M='ten'|C='rqh'] = 0 ≠ Pr[M='ten']` → shift cipher는 perfectly secret이 아님
- **Bayes's theorem**: `Pr[A|B] = Pr[B|A]·Pr[A]/Pr[B]`
- Ex4: `Pr[M='hi']=0.3, Pr[M='no']=0.2, Pr[M='in']=0.5`일 때 Bayes 정리로 `Pr[M='hi'|C='xy']` 계산 → `Pr[C='xy'|M='hi']=1/26`, `Pr[C='xy']=(1/26)·0.3+(1/26)·0.2+0·0.5=1/52`, 결국 `Pr[M='hi'|C='xy'] = (1/26·0.3)/(1/52) = 0.6 ≠ Pr[M='hi']=0.3`
- **결론**: shift cipher는 (적어도 2글자 메시지에 대해) perfectly secret이 아니다. 그럼 perfectly secret한 스킴을 어떻게 만들 수 있을까?

### One-Time Pad *(p.38~46)*
- 1917년 Vernam이 특허 (역사적으로는 그보다 최소 35년 전에 이미 발명되었다는 연구도 있음), 1949년 Shannon이 **perfectly secret임을 증명**
- 정의: `M = {0,1}^n`, Gen은 균등하게 `k ∈ {0,1}^n` 선택
  ```
  Enc_k(m) = k ⊕ m
  Dec_k(c) = k ⊕ c
  ```
- **Correctness**: `Dec_k(Enc_k(m)) = k⊕(k⊕m) = (k⊕k)⊕m = m`
- **역사적 실사용 예**: 워싱턴DC-모스크바 "red phone". 다만 키 관리 문제 때문에 현재는 실사용되지 않음

### One-Time Pad의 Perfect Secrecy 증명 *(p.41~44)*
- 임의의 관측된 ciphertext는 **임의의** 메시지에 대응될 수 있음(전제조건이지 충분조건은 아님)
- `M={0,1}^n`에 대한 임의의 분포, 임의의 `m,c∈{0,1}^n`에 대해:
  ```
  Pr[C=c] = Σ_m' Pr[C=c|M=m']·Pr[M=m']
          = Σ_m' Pr[K=m'⊕c|M=m']·Pr[M=m']
          = Σ_m' 2^-n · Pr[M=m']
          = 2^-n
  ```
  → `Pr[M=m|C=c] = Pr[C=c|M=m]·Pr[M=m]/Pr[C=c] = Pr[K=m⊕c|M=m]·Pr[M=m]/2^-n = 2^-n·Pr[M=m]/2^-n = Pr[M=m]` ✓ (perfect secrecy 정의를 정확히 만족)

### One-Time Pad의 한계 *(p.47~50)*
- **키가 메시지만큼 길어야 함**, **키를 단 한 번만 써야 안전함** → 주고받을 수 있는 모든 메시지 길이의 총합만큼 키를 미리 공유해야 함(비현실적)
- **같은 키를 두 번 쓰면 known-plaintext attack에 완전히 취약**:
  - `c1 = k⊕m1, c2 = k⊕m2`이고 공격자가 `m1`을 알면 → `k := c1⊕m1` 계산 가능 → `m2 := c2⊕k` 복원 가능
  - `m1`을 몰라도 `c1⊕c2 = (k⊕m1)⊕(k⊕m2) = m1⊕m2` → m1, m2에 대한 정보가 누설됨
- **이 한계들은 perfect secrecy를 달성하는 스킴 전반에 내재된 것**이지 OTP만의 문제가 아님

### One-Time Pad의 최적성 *(p.51)*
- **정리**: (Gen,Enc,Dec)가 message space `M`에서 perfectly secret이면 `|K| ≥ |M|` (증명 생략)
- → 키 길이를 줄일 수 있는 여지가 없다는 뜻: OTP는 이미 최적

---

## 4. Computational Secrecy *(p.52~73)*

### 지금까지의 상황 정리 *(p.53)*
Perfect secrecy를 정의했고, OTP가 이를 달성하며 최적임을 증명함. 하지만 끝난 게 아님 — **정의를 완화(relax)**해서 더 실용적인 스킴을 만들 필요가 있음(단, 의미 있는 방식으로).

### Perfect secrecy의 한계 *(p.54~57)*
- Perfect secrecy는 "**무한한 계산 능력**을 가진 도청자에게조차 plaintext에 대한 정보를 절대 누설하지 않을 것"을 요구 — 불필요하게 강한 조건
- **완화 방향**: 
  1. 아주 작은 확률로 안전성이 "실패"하는 것을 허용
  2. "효율적인(efficient)" 공격자로 관심을 제한
- 실패 확률 `2^-60`이면 문제 없음 — 그 정도 확률이면 송수신자가 내년에 벼락 맞을 확률보다도 낮음, `2^-60`/초 확률의 사건은 1000억 년에 한 번꼴로 발생
- **Bounded attacker 예시**: 데스크탑 컴퓨터 ≈ `2^57` keys/year, 슈퍼컴퓨터 ≈ `2^80` keys/year, 빅뱅 이후 시간 동안 슈퍼컴퓨터로도 ≈ `2^112` keys → `2^112`개 키를 시도하는 공격자로 제한해도 무방. 현대 키 공간은 `2^128`개 이상

### Perfect Indistinguishability — 재정의 *(p.58~62)*
- 실험 `PrivK_{A,Π}`: 1) 공격자 A가 `m0, m1 ∈ M`을 출력 2) `k←Gen, b←{0,1}, c←Enc_k(m_b)` (challenge ciphertext) 3) `b' ← A(c)`. A가 `b=b'`이면 성공(실험 값=1)
- `Π`가 **perfectly indistinguishable**하다 = 모든 공격자 A에 대해 `Pr[PrivK_{A,Π}=1] = 1/2` (1/2보다 잘 맞추는 게 불가능)
- **Claim**: perfectly indistinguishable ⟺ perfectly secret — 서로 동치인 정의

### Computational Indistinguishability — Concrete 버전 *(p.63~66)*
- 완화된 정의로 relax: `(t, ε)-indistinguishability` — 시간 `≤t`로 동작하는 모든 공격자 A에 대해 `Pr[PrivK_{A,Π}=1] ≤ 1/2 + ε`
- `(∞, 0)`-indistinguishability = perfect indistinguishability (즉 `t<∞, ε>0`로 완화한 것)
- **단점**: 정확한 계산 모델에 민감하고, 하나의 `Π`가 여러 `(t,ε)` 조합에 대해 성립할 수 있어 깔끔한 이론으로 이어지지 않음. 사용자가 원하는 대로 보안 수준을 조절할 수 있는 스킴이 필요

### Computational Indistinguishability — Asymptotic 버전 *(p.67~73)*
- **Security parameter `n`** 도입: 지금은 key length로 생각하면 됨. 정직한 당사자들이 키를 생성/공유할 때 선택(보안 수준을 원하는 대로 조절 가능), 공격자도 이 값을 앎
- 모든 당사자의 실행시간과 공격자의 성공 확률을 **n의 함수**로 측정
- **정의**: 함수 `f: Z⁺→Z⁺`가 **polynomial**하다 = 어떤 c가 존재해 `f(n) < n^c`. 함수 `f: Z⁺→[0,1]`가 **negligible**하다 = 모든 다항식 p에 대해 충분히 큰 n에서 `f(n) < 1/p(n)` (즉 어떤 역다항식보다도 빠르게 감소, 전형적 예: `f(n)=poly(n)·2^-cn`)
- 이 선택("efficient"="PPT(probabilistic polynomial-time)", "안전 실패 확률=negligible")은 다소 임의적이지만, **편리한 닫힘 성질**을 가짐: `poly * poly = poly`(PPT 알고리즘이 PPT 서브루틴을 호출해도 여전히 PPT), `poly * negligible = negligible`(negligible한 확률로 실패하는 서브루틴을 다항 번 호출해도 전체 실패 확률은 여전히 negligible)
- **(재)정의된 private-key encryption scheme**: 세 개의 PPT 알고리즘 (Gen, Enc, Dec)
  - Gen: `1^n`을 입력받아 `k` 출력 (`|k|≥n` 가정)
  - Enc: 키 `k`와 메시지 `m∈{0,1}*`를 입력받아 `c←Enc_k(m)` 출력
  - Dec: 키 `k`와 ciphertext `c`를 입력받아 메시지 `m` 또는 "error" 출력
- **PrivK_{A,Π}(n)** 실험: 1) `A(1^n)`이 같은 길이의 `m0,m1∈{0,1}*` 출력 2) `k←Gen(1^n), b←{0,1}, c←Enc_k(m_b)` 3) `b'←A(c)`. `b=b'`이면 성공
- **정의 (EAV-secure)**: `Π`가 computationally indistinguishable하다(= EAV-secure)는 것은, 모든 PPT 공격자 A에 대해 negligible한 함수 `ε`가 존재해 `Pr[PrivK_{A,Π}(n)=1] ≤ 1/2 + ε(n)`

---

## 5. Constructing Primitives, Worlds in Crypto *(p.74~82)*

### 기본 프리미티브 목록 *(p.75, 77)*
- OWF(One-way Function), PRG(Pseudo-Random # Generation), PRF(Pseudo-Random Function), Hashing, Digital signature
- Secret-key encryption, PRP(Pseudo-random Permutation), Bit-commitments, Digital signature, Zero-knowledge proof

### Foundational Methodology — 더 단순한 프리미티브로 환원 *(p.76)*
```
OWF → Hashing
OWF → PRG → PRF → (Secret-key encryption)
OWF → Digital Signatures
```
**"well-studied, average-case hard" 문제들**(예: 소인수분해, discrete-log 등)로부터 OWF 같은 기초 프리미티브가 구성됨.

### Roadmap: Worlds in Crypto — Minicrypt vs Cryptomania *(p.78)*
```
Cryptomania:  Public-key encryption
              -------------------- (경계선)
Minicrypt:    OWF → { Hashing → Digital Signatures
                       PRG → { PRF → PRP
                                PRF → Secret-key encryption }
                       (점선) → Zero-Knowledge proofs → Bit Commitment → Digital Signatures }
```
- **Minicrypt**: OWF(One-Way Function)만 있으면 도달 가능한 세계 — hashing, PRG, PRF, PRP, secret-key encryption, digital signature 등
- **Cryptomania**: OWF만으로는 부족하고 더 강한 가정(예: discrete-log, factoring 기반 문제)이 필요한 세계 — public-key encryption 등

### 현대 암호시스템의 아키텍처 *(p.79)*
Basic Mathematical Facts(정보이론, 대수, 정수론, 확률론 등) → Cryptographic Primitives(OWF, Hashing 등) → Cryptographic Algorithms(PRG, PRF, PRP 등) → Cryptographic Schemes(대칭/공개키 암호, 서명, 비밀 공유 등) → Cryptographic Protocols → Cryptographic Systems(보안 서비스) → Information Security System 순으로 계층을 이룸.

### One-way Function의 정의 *(p.80~81)*
함수족 `{F_n}_{n∈ℕ}` (`F_n: {0,1}^n → {0,1}^{m(n)}`)가 one-way하다는 것은, 모든 PPT 공격자 A에 대해 negligible한 함수 `μ`가 존재해
```
Pr[x←{0,1}^n; y=F_n(x); A(1^n,y)=x': y=F_n(x')] ≤ μ(n)
```
즉, **무제한 시간이면 항상 어떤 역상(inverse)을 찾을 수 있지만**, 확률적 다항 시간 안에는 찾기 어려워야 함.

### OWF에 관한 알려진 사실들 *(p.81)*
- P=NP이면 OWF는 존재하지 않는다
- OWF가 존재하면 P≠NP이다
- (역은 성립하지 않음) P≠NP라고 해서 OWF가 존재하는 것은 아니다
- **PRG ↔ OWF**: pseudorandom generator가 존재하는 것은 one-way function(과 hard-core predicate)이 존재하는 것과 동치

### Well-studied, average-case hard 문제들 *(p.82)*
- NP-hard/NP-complete 문제(3-colorability, TSP, knapsack 등)는 대부분 암호학적 가정으로 쓰기엔 부적합(worst-case 어려움이지 average-case 어려움이 아니라서, 추후 안전성이 깨지는 경우가 많음)
- 대신 실제로 쓰이는 것: **DLP(Discrete-log Problem)** — 군 `G`에서 `b^k=a`를 만족하는 정수 `k`(discrete log)를 찾는 문제, **소인수분해(prime factoring)**

---

## 핵심 요약

- Modern crypto는 (1) formal definition (2) 명시적 assumption (3) security proof의 3원칙 위에서 동작
- "안전한 암호화"의 정의는 여러 시행착오(키 은닉 → plaintext 은닉 → 글자 단위 은닉)를 거쳐 "**사전 정보와 무관하게 ciphertext가 추가 정보를 누설하지 않아야 한다**"로 수렴
- 이를 확률론으로 formalize한 것이 **Perfect Secrecy**(`Pr[M=m|C=c]=Pr[M=m]`) — Shift cipher는 만족 못 하지만, **One-Time Pad**는 만족(Shannon 증명)하며 이론적으로 **최적**(`|K|≥|M|`)
- 하지만 OTP는 키 길이/재사용 제약이 실용적이지 않음 → **Computational Secrecy**로 완화: 무한 계산능력 대신 **PPT 공격자**, 완전한 안전 대신 **negligible 실패확률** 허용 (asymptotic security parameter n 도입)
- 이 완화된 정의(**computational indistinguishability / EAV-security**) 위에서, OWF를 기초로 PRG→PRF→PRP→secret-key encryption 등 더 실용적인 프리미티브들을 단계적으로 구성 (**Minicrypt** vs 더 강한 가정이 필요한 **Cryptomania**로 세계가 나뉨)
