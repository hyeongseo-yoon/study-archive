# Chapter 2-1: Classical Encryption Techniques

*Hanyang University, Division of Computer Science and Engineering*

## 1. Symmetric/Private Cipher Model *(슬라이드 p.2~5)*

### 용어 정리 *(슬라이드 p.3)*
- **Plaintext**: 원본 메시지
- **Ciphertext**: 암호화된(coded) 메시지
- **Encipher (encrypt)**: plaintext → ciphertext 변환
- **Decipher (decrypt)**: ciphertext → plaintext 복원
- **Key**: 암복호화에 쓰이는 비밀 입력값

```
Plaintext --[Encryption + Key]--> Ciphertext --[Decryption + Key]--> Plaintext
```

### Cryptography / Cryptanalysis / Cryptology *(슬라이드 p.4)*
- **Cryptography**: 암호 방식을 "만드는" 연구
- **Cryptanalysis**: 암호 방식을 "깨는" 연구
- **Cryptology** = Cryptography + Cryptanalysis

### Symmetric cipher의 두 가지 요구사항 *(슬라이드 p.5)*
1. **암호화 알고리즘 자체가 강해야 함**: 상대가 알고리즘을 알아도(공개돼 있어도) key 없이는 못 품 → 알고리즘을 비밀로 할 필요 없음(널리 쓰이기 편함)
2. **비밀키는 송수신자만 알아야 함**: 키가 새면 누구나 복호화 가능

---

## 2. Cryptography 분류 기준 *(슬라이드 p.10~11)*

### 암호화 연산의 종류 *(슬라이드 p.10)*
- **Substitution**: plaintext의 각 원소를 다른 원소로 매핑
- **Transposition**: plaintext의 원소들을 재배열(rearrange)

### Plaintext 처리 방식 *(슬라이드 p.11)*
- **Block cipher**: 입력을 블록 단위로 한 번에 처리, 블록마다 출력 블록 생성
- **Stream cipher**: 입력을 연속적으로 처리, 원소(비트 또는 문자) 하나씩 출력 생성

---

## 3. Cryptanalysis *(슬라이드 p.12~17)*

### 공격 유형 — cryptanalyst가 아는 정보량 기준 *(슬라이드 p.12~14)*
정보량이 많아질수록 공격이 쉬워짐(아래로 갈수록 more information):
- **Ciphertext only**: 암호화 알고리즘 + ciphertext만 앎
- **Known plaintext**: 위 + 한 개 이상의 plaintext-ciphertext 쌍을 앎
- **Chosen plaintext**: 위 + 공격자가 plaintext를 직접 골라 그에 대응하는 ciphertext를 얻을 수 있음
- **Chosen ciphertext**: 위 + 공격자가 plaintext/ciphertext 어느 쪽이든 골라 대응 쌍을 얻을 수 있음

### 안전성의 두 기준 (Stinson) *(슬라이드 p.15~16)*
- **Unconditionally secure**: ciphertext가 plaintext를 유일하게 결정할 만큼의 정보를 담고 있지 않으면, 상대는 원리적으로 복호화가 불가능
- **Computationally secure**: 아래 조건 중 하나를 만족하면 "충분히 안전"하다고 봄
  - 암호를 깨는 **비용**이 암호화된 정보의 **가치**를 초과
  - 암호를 깨는 데 필요한 **시간**이 정보의 **유효 수명**을 초과
  - (다만 이 기준을 엄밀히 만족시키는 건 실제로는 여전히 애매함 — "still vague")

### Brute-force attack *(슬라이드 p.17)*
가능한 모든 키를 하나씩 대입 — 평균적으로 전체 키의 절반만 시도하면 성공.

| Key Size (bit) | 가능한 키 개수 | 시간 (1 encryption/µs) | 시간 (10⁶ encryptions/µs) |
|---|---|---|---|
| 32 | 2³² ≈ 4.3×10⁹ | 2³¹ µs ≈ 35.8분 | 2.15밀리초 |
| 56 (DES) | 2⁵⁶ ≈ 7.2×10¹⁶ | 2⁵⁵ µs ≈ 1142년 | 10.01시간 |
| 128 (AES) | 2¹²⁸ ≈ 3.4×10³⁸ | 2¹²⁷ µs ≈ 5.4×10²⁴년 | 5.4×10¹⁸년 |
| 168 (Triple DES) | 2¹⁶⁸ ≈ 3.7×10⁵⁰ | 2¹⁶⁷ µs ≈ 5.9×10³⁶년 | 5.9×10³⁰년 |
| 26자 순열 | 26! ≈ 4×10²⁶ | 2×10²⁶ µs ≈ 6.4×10¹²년 | 6.4×10⁶년 |

---

## 4. Substitution / Transposition Techniques 개요 *(슬라이드 p.19)*
- **Substitution**: plaintext의 글자를 다른 글자로 치환 (예: A→C, B→F, …)
- **Transposition**: plaintext 안의 글자 순서를 뒤바꿈 (예: message → essgeam)

---

## 5. Shift Cipher (Caesar Cipher) *(슬라이드 p.20~22)*

### 규칙 *(슬라이드 p.20)*
key `k`만큼 알파벳을 오른쪽으로 원형 이동(circular right shift).
- k=4일 때: A→E, B→F, … X→B, Y→C, Z→D
- 예: plaintext `baby`, k=4로 암호화

### 복호화와 Cryptanalysis *(슬라이드 p.21~22)*
- 복호화는 암호화의 역연산
- **Brute-force**로 깨기 쉬움: 키 공간이 26개뿐이라 0~25 전부 시도하면 됨
  - 예: ciphertext `JBCRCLQRWCRVNBJENBWRWN`을 각 shift값으로 다 풀어보면 shift=9에서 `astitchintimesavesnine`(평문)이 나옴
- Brute-force cryptanalysis가 성립하는 **3가지 조건** *(p.22)*:
  1. 암복호화 알고리즘을 알고 있음
  2. 시도할 키가 25개뿐임 (적음)
  3. plaintext의 언어를 알고 있고 쉽게 알아볼 수 있음
  - → brute-force를 비현실적으로 만드는 건 결국 **키 개수가 많은 알고리즘**을 쓰는 것

---

## 6. Monoalphabetic Cipher *(슬라이드 p.23~31)*

### 암복호화 *(슬라이드 p.23~24)*
- **암호화**: plaintext의 각 문자를 하나의 순열(permutation)로 치환 (예: a→X, b→N, c→Y, …)
- **복호화**: ciphertext를 역순열로 치환
- Shift cipher는 monoalphabetic cipher의 특수한 경우(26가지 순열 중 하나로 제한된 형태)

### Brute-force는 불가능 *(슬라이드 p.25)*
26! ≈ 4×10²⁶개의 순열이 가능 → 키 공간이 너무 커서 무차별 대입 불가능.

### 대신 언어의 통계적 특성(빈도 분석)으로 공격 *(슬라이드 p.26~31)*
1. Ciphertext 내 글자들의 상대 빈도를 계산하고, 영어의 표준 빈도 분포와 비교 *(p.26~27)*
2. **English Letter Frequencies**: e(12.7%), t(9.1%) 등이 가장 흔함 — 표/막대그래프로 제공 *(p.28)*
3. Ciphertext에서 가장 빈도 높은 글자(P, Z)를 e, t에 대응시켜 추정, 나머지(S, U, O, M, H)는 {a,h,i,n,o,r,s} 후보군에 대응 *(p.29)*
4. **Digram(2글자 조합)** 빈도 활용: 영어에서 가장 흔한 digram은 `th` → ciphertext에서 가장 흔한 digram(ZW)을 `th`로 추정 *(p.30)*
5. **Trigram(3글자 조합)** 활용: `ZWP`가 `the`에 대응한다고 추정
6. 이런 식으로 패턴(`th_t` 형태의 `ZWSZ` → S=a)을 계속 좁혀가며 최종 평문 복원: *(p.31)*
   > "it was disclosed yesterday that several informal but direct contacts have been made with political representatives of the viet cong in moscow"

---

## 7. Playfair Cipher *(슬라이드 p.33~40)*

### 목적 *(슬라이드 p.33)*
Monoalphabetic cipher는 언어의 구조(빈도)가 ciphertext에 그대로 남아 취약함. 이를 줄이는 두 방법:
- 여러 글자를 한 번에 암호화 (Playfair, Hill)
- 여러 개의 cipher alphabet을 사용 (polyalphabetic)

### 규칙 — 5×5 행렬 만들기 *(슬라이드 p.34)*
- 대표적인 multiple-letter cipher. **diagram(2글자)** 단위로 처리
- Key(예: MONARCHY)의 글자를 중복 제거하며 왼→오, 위→아래로 채움
- 남은 칸은 알파벳 순서로 나머지 글자 채움
- **I와 J는 한 칸(같은 글자 취급)**

```
M O N A R
C H Y B D
E F G I/J K
L P Q S T
U V W X Z
```

### 암호화 규칙 *(슬라이드 p.35)*
- 같은 글자가 반복되는 diagram은 필러 문자로 분리 (예: balloon → ba lx lo on)
- **같은 행**에 있으면 → 각 글자의 오른쪽 글자로 치환 (원형, 예: ar → RM)
- **같은 열**에 있으면 → 각 글자의 아래쪽 글자로 치환 (원형, 예: mu → CM)
- **행/열이 다르면** → 자신의 행 + 상대의 열에 해당하는 글자로 치환 (예: hs → BP, ea → IM or JM)

### 강도와 약점 *(슬라이드 p.36~40)*
- 단순 monoalphabetic보다 훨씬 발전: 26×26=676개의 diagram이 있어 빈도분석이 훨씬 어려움 → 오랫동안 unbreakable로 여겨짐
- 하지만 **상대적으로 쉽게 깨짐**: plaintext 언어의 구조가 여전히 많이 남아있어서, ciphertext 수백 글자만 있어도 분석 가능
- Plaintext/Playfair/Random polyalphabetic의 정규화된 문자 빈도 분포를 비교한 그래프 *(p.37~40)*: Playfair가 plaintext보다는 평탄(flat)하지만, random polyalphabetic만큼 평탄하지는 않음 → 여전히 구조가 드러남

---

## 8. Hill Cipher *(슬라이드 p.41)*

- 수학자 Lester Hill이 1929년에 고안한 또 다른 multiple-letter cipher
- 연속된 plaintext 문자 m개를 ciphertext 문자 m개로 치환
- **행렬 연산**으로 빈도 정보를 숨김 — 행렬이 클수록 더 많은 빈도 정보를 숨길 수 있음 (예: 3×3 Hill cipher는 1글자뿐 아니라 2글자 빈도 정보까지 숨김)
- **ciphertext-only 공격엔 강하지만, known-plaintext 공격엔 쉽게 깨짐**

---

## 9. Polyalphabetic Cipher — Vigenère Cipher *(슬라이드 p.42~47)*

### 개념 *(슬라이드 p.42)*
- shift 0~25에 해당하는 **26개의 Caesar cipher를 모아놓은 집합**
- 각 cipher는 key letter로 식별 (예: key='d' → shift 3 → 'b'→'E')
- 메시지 길이만큼 긴 key가 필요 → 보통 **반복되는 키워드**를 사용

```
Key:        deceptivedeceptivedeceptive
Plaintext:  wearediscoveredsaveyourself
Ciphertext: ZICVTWQNGRZGVTWAVZHCQYGLMGJ
```

### 강점과 한계 *(슬라이드 p.45~46)*
- 강점: plaintext 글자 하나당 여러 ciphertext 글자가 대응될 수 있어 빈도 정보가 흐려짐(obscured)
- 한계: plaintext 구조 정보가 완전히 사라지진 않음. Playfair보다는 개선됐지만 여전히 상당한 빈도 정보가 남음
- 그래프 비교 *(p.46)*: Plaintext > Playfair ≈ Vigenère > Random polyalphabetic 순으로 평탄해짐(뒤로 갈수록 더 안전)

---

## 10. One-Time Pad (Vernam Cipher) *(슬라이드 p.47~48)*

### 개념 *(슬라이드 p.47)*
- Vigenère의 약점(반복되는 키)을 근본적으로 없애는 방법: **키를 plaintext만큼 길게, 통계적 관련성이 전혀 없게** 만듦
- AT&T 엔지니어 Gilbert Vernam이 1918년 고안, binary 데이터에서 동작

### 암복호화 알고리즘 *(슬라이드 p.48)*
```
암호화: c_i = p_i ⊕ k_i
복호화: p_i = c_i ⊕ k_i
```
- p_i = plaintext의 i번째 binary digit, k_i = key의 i번째 binary digit, c_i = ciphertext의 i번째 binary digit
- ⊕ = XOR (exclusive-or) 연산
- 원래는 "반복되는 테이프 루프"를 키로 제안했으나, 이 경우 결국 키가 반복되므로 충분한 ciphertext + known/probable plaintext로 깨질 수 있음 (→ 진짜 One-Time Pad는 키를 절대 재사용하지 않아야 안전)

---

## 11. Transposition Techniques *(슬라이드 p.52~54)*

### 정의 *(슬라이드 p.52~53)*
plaintext 글자들에 어떤 순열(permutation)을 가하는 것. (Block/Columnar Transposition은 시간 관계상 생략)

### Rail Fence *(슬라이드 p.54)*
가장 단순한 transposition 기법.
- Plaintext: `meet me after the toga party`
- 대각선(지그재그) 방향으로 depth 2로 쓴다:
```
m e m a t r h t g p r y
 e t e f e t e o a a t
```
- 행(row) 순서대로 읽으면 ciphertext: `mematrhtgpryetefeteoaat`

---

## 12. Rotor Machine (Enigma) *(슬라이드 p.55~60)*

### 개요 *(슬라이드 p.55)*
- WWII 당시 독일이 사용한 타자기 형태의 암호 기계
- 사용 편의성과 암호학적 강도 면에서 큰 진전
- 로터(rotor)가 오도미터(주행거리계)처럼 회전하며, 메시지의 매 글자마다 새로운 암호 알고리즘을 적용

### 동작 원리 *(슬라이드 p.56~60)*
- 여러 단(stage)의 암호화 — substitution + transposition을 모두 사용
- 독립적으로 회전하는 실린더(cylinder)들의 집합, 각 실린더는 26개의 입/출력 핀을 가짐 *(p.56)*
- **실린더 하나** = 하나의 monoalphabetic substitution *(p.57)*
  - 키를 누를 때마다 실린더가 한 칸 회전 → 내부 연결이 바뀌며 다른 monoalphabetic substitution이 적용됨
- 실린더가 26글자를 다 돌면 원위치로 복귀 → **주기 26의 polyalphabetic 순열** *(p.58)*
- 여러 실린더를 연결(한 실린더의 출력을 다음 실린더의 입력으로): 바깥쪽이 매 키입력마다 한 칸, 그게 한 바퀴 다 돌면 중간 실린더가 한 칸, 중간이 한 바퀴 돌면 안쪽이 한 칸 회전 *(p.59)*
  - 3단 로터 기준 26×26×26 = **17,576**가지 조합
- 로터가 회전함에 따라 실린더 내부 배선(경로)도 함께 바뀌는 예시 그림(초기 상태 vs 한 번 입력 후 상태) *(p.60)*

---

## 13. Steganography *(슬라이드 p.61~65)*

### Cryptography와의 차이 *(슬라이드 p.61)*
- **Steganography**: 메시지의 **존재 자체**를 숨김
- **Cryptography**: 메시지 내용을 알아볼 수 없게(unintelligible) 만듦

### 예시와 고전 기법 *(슬라이드 p.62~63)*
- 간단한 예: 메시지의 각 단어 첫 글자만 이어붙이면 숨겨진 메시지가 되도록 구성, 또는 전체 메시지 중 일부 단어만 골라 숨겨진 뜻을 전달
- 고전 기법: character marking(연필로 특정 글자 덧칠), invisible ink(투명 잉크), pin punctures(핀으로 구멍), typewriter correction ribbon(교정 리본으로 겹쳐 타이핑, 강한 빛 아래서만 보임)

### 현대 기법 *(슬라이드 p.64)*
- 이미지의 **LSB(Least Significant Bit)**를 이용 — 예: 2048×3072 픽셀, 픽셀당 24bit RGB인 Kodak Photo CD에서 각 픽셀의 LSB를 바꿔도 화질에 거의 영향 없음 → 사진 한 장에 2.3MB 메시지 은닉 가능

### 장단점 *(슬라이드 p.65)*
- **단점**: 적은 정보를 숨기는 데 비해 오버헤드가 큼, 시스템이 발각되면 즉시 무용지물이 됨 (→ 메시지를 먼저 암호화한 뒤 숨기는 방식으로 보완 가능)
- **장점**: 비밀 통신 당사자들이 통신하고 있다는 사실 자체를 숨길 수 있음

---

## 핵심 요약

- **분류축**: substitution(치환) vs transposition(순서 재배열), block vs stream 처리 방식
- **Cryptanalysis**: 정보량 기준 4단계 공격(ciphertext only → known → chosen plaintext → chosen ciphertext), 안전성은 unconditionally secure vs computationally secure로 구분
- **Substitution 계열의 발전 과정**: Shift(단일 순열, 키 26개) → Monoalphabetic(임의 순열, 26!개지만 빈도분석에 취약) → Playfair/Hill(다중 글자 단위로 빈도 정보 은폐) → Vigenère(다중 알파벳, 반복 키) → One-Time Pad(완전 무작위 키, 이론적으로 완벽)
- **Transposition**: Rail fence 등으로 글자 순서 자체를 뒤섞음
- **Rotor machine(Enigma)**: substitution+transposition을 기계적으로 반복 적용해 방대한 키 공간을 만든 실용적 구현체
- **Steganography**: 암호화(내용 은닉)와는 다른 축의 보안 — 메시지 존재 자체를 은닉

## 수업 진행 섹션

1. Symmetric Cipher Model + 용어
2. Cryptography 분류 기준
3. Cryptanalysis
4. Substitution / Transposition 개요
5. Shift Cipher (Caesar Cipher)
6. Monoalphabetic Cipher
7. Playfair Cipher
8. Hill Cipher
9. Polyalphabetic Cipher — Vigenère Cipher
10. One-Time Pad (Vernam Cipher)
11. Transposition Techniques — Rail Fence
12. Rotor Machine (Enigma)
13. Steganography
