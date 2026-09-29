# Chapter 2-1 수업노트

*(수업일: 2026-09-29, 참조 노트: `notes/chapter-2-1-classical-encryption.md`)*

## 1. Symmetric Cipher Model + 용어

용어 정리:
- **Plaintext**: 전달할 내용(원본 메시지)
- **Ciphertext**: 암호화된 문장
- **Key**: 암호화할 때 쓰는 입력
- **Encipher (encrypt)**: plaintext → ciphertext로 바꾸는 동작
- **Decipher (decrypt)**: ciphertext → plaintext로 되돌리는 동작

세 단어의 어원:
- **Cryptography** = crypto(숨겨진) + graphy(쓰기) → 암호를 "만드는" 연구
- **Cryptanalysis** = crypto(숨겨진) + analysis(분석) → 암호를 "깨는" 연구
- **Cryptology** = 위 둘을 합친 전체 분야

전체 흐름:
```
Plaintext --[Encryption + Key]--> Ciphertext --[Decryption + Key]--> Plaintext
```

Symmetric cipher(대칭키 암호)가 안전하려면 두 가지 조건이 필요해:
1. **암호화 알고리즘 자체가 강해야 함**
2. **비밀키는 송수신자만 알아야 함**

1번 조건 관련 — "상대가 암호화 알고리즘을 알고 있어도 key 없이는 못 깬다"는 뜻이라, key만 비밀이면 되니까 알고리즘은 공개해도 안전성엔 문제 없어. 공개했을 때 실용적인 이유도 있어: 많은 cryptanalyst들이 검증해도 안 깨지면 신뢰도가 올라가고, 알고리즘을 비밀로 할 필요가 없으니까 **널리 쓰이기 편해짐**(표준화, 여러 시스템에서 같은 알고리즘 재사용 가능).

---

## 2. Cryptography 분류 기준

암호 기법을 분류하는 두 가지 축:

**첫 번째 축 — 암호화 연산의 종류**:
- **Substitution**: plaintext의 각 원소를 다른 원소로 "매핑"
- **Transposition**: plaintext의 원소들을 "재배열"

**두 번째 축 — plaintext 처리 방식**:
- **Block cipher**: 입력을 블록 단위로 한 번에 처리
- **Stream cipher**: 입력을 하나씩(비트/문자 단위) 연속 처리

`A→C, B→F, ...`처럼 각 글자를 다른 글자로 바꾸는 건 substitution — 각 원소를 다른 원소로 매핑하는 것이기 때문.

---

## 3. Cryptanalysis

### 공격 유형

공격자가 얼마나 많은 정보를 가지고 있는가를 기준으로 4단계, 아래로 갈수록 더 많은 정보를 가지고 있어서 공격이 쉬워짐:
- **Ciphertext only**: 암호화 알고리즘 + ciphertext만 앎
- **Known plaintext**: 위 + plaintext-ciphertext 쌍을 하나 이상 앎
- **Chosen plaintext**: 위 + 공격자가 plaintext를 직접 골라서 대응 ciphertext를 얻을 수 있음
- **Chosen ciphertext**: 위 + plaintext든 ciphertext든 어느 쪽이든 골라서 대응 쌍을 얻을 수 있음

### 안전성의 두 기준 (Stinson)

- **Unconditionally secure**: ciphertext가 plaintext를 유일하게 결정할 정보를 아예 담고 있지 않음 → 원리적으로 깰 수 없음
- **Computationally secure**: 깨는 데 드는 비용이 정보의 가치를 초과하거나, 깨는 데 드는 시간이 정보의 유효 수명을 초과하면 "충분히 안전"

### Brute-force attack

가능한 모든 키를 하나씩 대입. 평균적으로 키 공간의 **절반**만 시도하면 성공한다는 게 포인트 — 여기서 "절반"은 비트 수(예: 32)의 절반이 아니라, 가능한 키의 **개수**(2^32)의 절반, 즉 2^31이라는 뜻. 키 길이가 조금만 늘어나도 brute-force 난이도는 기하급수적으로 폭증해:

| Key Size | 평균 시도 시간 (1μs/회) |
|---|---|
| 32bit | 약 35.8분 |
| 56bit (DES) | 약 1142년 |
| 128bit (AES) | 약 5.4×10²⁴년 |

56비트에서 128비트로 72비트 늘었을 뿐인데 현실적으로 뚫을 수 없는 수준이 됨.

---

## 4. Substitution / Transposition 개요

- **Substitution**: plaintext의 글자를 다른 글자로 치환 (예: A→C, B→F, …) — 순서는 그대로, 알파벳 정체성이 바뀜
- **Transposition**: plaintext 안의 글자 순서를 뒤바꿈 (예: message → essgeam) — 알파벳 자체는 안 바뀌고 순서만 섞임

---

## 5. Shift Cipher (Caesar Cipher)

규칙: key `k`만큼 알파벳을 오른쪽으로 원형 이동(circular shift)시켜서 치환. 예: k=3일 때 `hi` → `kl` (h+3=k, i+3=l).

일반화한 공식 (a=0, b=1, ..., z=25):
```
암호화: C = (P + k) mod 26
복호화: P = (C - k) mod 26
```

mod 26이 필요한 이유: k=4일 때 `y`(24)를 암호화하면 24+4=28, 28 mod 26 = 2 = `c`. 25를 넘어가면 다시 처음(a)으로 돌아오는 wraparound 때문에 mod 연산이 필요함.

### Brute-force cryptanalysis가 성립하는 3가지 조건

1. **암복호화 알고리즘을 알고 있음** — 키를 대입해보려면 애초에 "어떤 알고리즘에 어떻게 대입하는지"부터 알아야 함
2. **시도할 키가 적음(25개뿐)** — 키 공간이 작아야 현실적인 시간 안에 다 해볼 수 있음
3. **plaintext의 언어를 알고 있고, 나왔을 때 쉽게 알아볼 수 있음** — 26개 후보 중 어떤 게 "진짜 평문"인지 판별할 수 있어야 공격이 완성됨

결국 brute-force를 막는 가장 확실한 방법은 **키 공간을 크게 만드는 것**(2번 조건을 깨는 것).

---

## 6. Monoalphabetic Cipher

Caesar cipher는 "26가지 순열 중 하나"만 쓸 수 있다는 제한이 있었음. Monoalphabetic cipher는 그 제한을 풀어서 26개 알파벳을 아무렇게나 재배열한 순열을 키로 씀. 키 공간은 26! ≈ 4×10²⁶개라 brute-force는 완전히 불가능.

### 핵심 아이디어 — 왜 그래도 깨지는가

Substitution을 해도 절대 안 바뀌고 보존되는 성질이 있음: 각 글자가 나오는 **빈도(frequency)**. `e`가 영어에서 12.7%로 제일 흔한 글자라면, 그게 `P`로 치환됐어도 ciphertext에서 `P`는 여전히 제일 흔하게 나옴 — 라벨만 바뀌고 빈도 패턴은 그대로 보존되기 때문.

### 공격 절차 (frequency analysis)

1. Ciphertext에서 각 글자의 빈도를 계산
2. 영어 표준 빈도 분포와 비교: **e(12.7%), t(9.1%)**가 압도적으로 흔함
3. Ciphertext에서 가장 빈도 높은 글자를 `e`, `t`에 대응시켜 추정
4. 애매하면 **digram(2글자 조합)** 활용 — 영어에서 가장 흔한 digram은 `th`
5. **trigram(3글자 조합)**도 활용 — `the`가 가장 흔한 trigram
6. 추정한 글자들을 단서로 나머지를 패턴으로 좁혀가며 전체 평문 복원

이 공격이 통하려면 ciphertext가 어느 정도 길어야 함(보통 수백 글자) — 통계적 패턴은 표본이 충분해야 신뢰할 수 있기 때문에, 짧은 ciphertext로는 어떤 글자가 진짜 자주 나오는 건지 우연인지 구별이 안 됨.

---

## 7. Playfair Cipher

Monoalphabetic cipher의 근본 문제는 "한 글자=한 글자"로 치환하기 때문에 언어의 빈도 패턴이 고스란히 남는다는 것. Playfair는 한 글자가 아니라 **두 글자(digram)씩 묶어서** 치환.

키워드(예: `MONARCHY`)로 5×5 행렬을 만듦: 키워드 글자를 중복 없이 왼→오, 위→아래로 채우고, 남은 칸은 알파벳 순서로 채움. **I와 J는 한 칸을 공유**.

```
M O N A R
C H Y B D
E F G I/J K
L P Q S T
U V W X Z
```

암호화 규칙:
1. **같은 행**에 있으면 → 각자 오른쪽 글자로 치환 (행 끝이면 원형으로 맨 왼쪽)
2. **같은 열**에 있으면 → 각자 아래쪽 글자로 치환 (열 끝이면 원형으로 맨 위)
3. **행/열이 다르면** → 자기 행 + 상대 열이 만나는 글자로 치환

예: `a`와 `r`은 같은 행(M O N A R)에 있음 → 각자 오른쪽으로: a의 오른쪽은 r, r의 오른쪽은 행 끝이라 원형으로 맨 왼쪽인 m → `ar`→`RM`. 같은 방식으로 `mu`(같은 열)→`CM`, `hs`(행/열 다름)→`BP`.

같은 글자가 연속되는 경우(예: `balloon`)는 필러 문자를 끼워 분리: `ba lx lo on`.

### 강도와 약점

26×26=676개의 digram이 있어서 monoalphabetic보다 빈도분석이 훨씬 어려워 한동안 unbreakable로 여겨짐. 하지만 여전히 상대적으로 쉽게 깨짐 — monoalphabetic이 단일 글자 빈도를 보존했던 것과 같은 원리로, Playfair도 digram을 치환하는 것뿐이라 **digram별 등장 빈도가 그대로 보존됨**. `th`가 `ZW`로 바뀌었으면 `ZW`는 원래 `th`가 나왔을 만큼 자주 나타남. 그래서 digram 빈도표로 같은 방식의 통계적 공격이 통함. 그래프 비교로 보면 Plaintext > Playfair > Random polyalphabetic 순으로 평탄해지는데(뒤로 갈수록 안전), Playfair는 완전히 무작위만큼 평탄하진 않아서 ciphertext 수백 글자만 있으면 분석 가능.

---

## 8. Hill Cipher

수학자 Lester Hill이 1929년에 고안한 또 다른 multiple-letter cipher. **행렬 연산**으로 plaintext 문자 m개를 한번에 ciphertext 문자 m개로 치환하고, 행렬이 클수록(m이 클수록) 더 많은 글자 단위의 빈도 정보를 숨길 수 있음.

Hill cipher는 **ciphertext-only 공격엔 강하지만, known-plaintext 공격엔 쉽게 깨짐** — Ciphertext = Key행렬 × Plaintext (mod 26) 구조라서, plaintext-ciphertext 쌍을 행렬 크기만큼 확보하면 선형대수로 역행렬을 구해 key 행렬 자체를 풀어낼 수 있기 때문.

---

## 9. Polyalphabetic Cipher — Vigenère Cipher

지금까지는 한 글자(또는 digram)가 항상 같은 걸로 치환되는 방식이었음. Vigenère는 **여러 개의 Caesar cipher를 섞어서 쓴다**는 접근. Shift 0~25에 해당하는 26개의 Caesar cipher 집합이고, 각각은 key letter 하나로 식별됨(예: key='d' → shift 3). 메시지 길이만큼 긴 키가 필요한데, 보통 반복되는 키워드를 씀.

```
Key:        deceptivedeceptivedeceptive
Plaintext:  wearediscoveredsaveyourself
Ciphertext: ZICVTWQNGRZGVTWAVZHCQYGLMGJ
```

예: `w`(22)에 key `d`(shift 3)를 적용 → 22+3=25=Z.

### 강점과 한계

- 강점: 같은 plaintext 글자라도 key가 바뀌면서 서로 다른 ciphertext 글자로 대응 → 빈도 정보가 흐려짐
- 한계: 키가 결국 **반복**되므로 plaintext 구조 정보가 완전히 사라지진 않음

키워드 길이가 7글자라면, plaintext의 1,8,15,22...번째 글자들은 전부 같은 key 글자로 shift됨 → 이 위치들만 모으면 사실상 하나의 Caesar cipher와 똑같음. 그래서 공격자가 키 길이를 알아내면:
1. Ciphertext를 키 길이만큼 그룹으로 쪼갬
2. 각 그룹은 Caesar cipher이므로 빈도 분석을 그룹별로 적용해 shift 값을 알아냄
3. 모든 shift를 알아내면 키 전체를 알아낸 것

즉 "키가 반복된다" = "긴 메시지를 여러 개의 짧은 Caesar cipher로 쪼갤 수 있다"는 뜻이라, 결국 이미 배운 취약점(빈도 분석)으로 환원됨.

---

## 10. One-Time Pad (Vernam Cipher)

Vigenère의 약점(키 반복)을 근본적으로 없애는 방법. 키를 plaintext만큼 길게, 절대 반복하지 않으며, 통계적으로 plaintext와 아무 관련이 없게 만듦. Gilbert Vernam이 1918년 고안, binary 데이터에서 동작.

```
암호화: c_i = p_i ⊕ k_i
복호화: p_i = c_i ⊕ k_i
```

복호화 공식이 성립하는 증명:
```
c_i ⊕ k_i = (p_i ⊕ k_i) ⊕ k_i     [c_i를 정의대로 풀어씀]
          = p_i ⊕ (k_i ⊕ k_i)     [XOR은 결합법칙 성립]
          = p_i ⊕ 0               [같은 비트끼리 XOR하면 0]
          = p_i                   [어떤 값에 0을 XOR해도 그대로]
```
XOR이 자기 자신의 역연산(self-inverse)이라는 성질 덕분에 같은 키로 XOR을 한 번 더 해주면 원래 plaintext가 복원됨.

원래는 "반복되는 테이프 루프"를 키로 제안했는데, 이 경우 결국 키가 반복되므로 Vigenère와 똑같은 약점으로 깨질 수 있음. **진짜 One-Time Pad는 키를 절대 재사용하지 않아야** 안전함.

---

## 11. Transposition Techniques — Rail Fence

지금까지는 전부 substitution 계열이었고, Rail Fence는 가장 단순한 transposition 기법. Plaintext를 지그재그(대각선) 방향으로 depth만큼 써내려간 다음, 행 순서대로 읽어서 ciphertext를 만듦.

`meet me after the toga party`를 depth 2로:
```
m e m a t r h t g p r y
 e t e f e t e o a a t
```
행 순서대로 읽으면: `mematrhtgpryetefeteoaat`

Transposition은 substitution 계열들과 근본적으로 다름 — 글자 자체를 안 바꾸고 순서만 섞으니까, ciphertext의 글자별 빈도는 plaintext랑 **완전히 동일**(substitution처럼 "패턴이 보존"되는 정도가 아니라 아예 똑같은 숫자). 그래서 빈도 분석 자체로는 못 깨지만, 대신 "애너그램을 어떻게 재배열했는가"를 찾는 방식으로 공격 가능.

---

## 12. Rotor Machine (Enigma)

WWII 때 독일이 쓴 타자기 형태의 암호 기계. 핵심 아이디어는 **substitution과 transposition을 기계적으로 반복 적용**해서 거대한 키 공간을 만드는 것.

구조: 독립적으로 회전하는 실린더(cylinder) 여러 개, 각 실린더는 26개의 입/출력 핀을 가짐. **실린더 하나 = monoalphabetic substitution 하나**. 키를 누를 때마다 실린더가 한 칸 회전 → 내부 연결이 바뀌면서 다음 글자는 다른 substitution이 적용됨. 실린더가 26글자를 다 돌면 원위치 복귀 → 주기 26의 **polyalphabetic** 순열이 됨.

여러 실린더를 오도미터처럼 연결: 바깥쪽 실린더가 매 키 입력마다 한 칸씩 돌고, 바깥쪽이 한 바퀴(26글자) 다 돌면 중간 실린더가 한 칸, 중간이 한 바퀴 돌면 안쪽이 한 칸 도는 식. 3단 로터 기준 가능한 조합은 26×26×26 = **17,576**가지 — 각 실린더가 독립적으로 26가지 위치를 가질 수 있으니 곱해서 계산.

이걸로 Enigma는 단일 monoalphabetic보다 훨씬 큰 키 공간 + 매 글자마다 substitution이 바뀌는 polyalphabetic 성질을 동시에 얻음.

---

## 13. Steganography

Cryptography랑 아예 다른 축의 보안 개념:
- **Cryptography**: 메시지 "내용"을 알아볼 수 없게(unintelligible) 만듦
- **Steganography**: 메시지의 **"존재 자체"**를 숨김

통신을 감시하는 입장에서, cryptography로 암호화된 메시지를 보면 "암호화된 통신이 오간다"는 사실 자체는 알 수 있음(내용은 몰라도). Steganography로 숨긴 메시지는 통신하고 있다는 사실 자체를 눈치채지 못함 — 그냥 평범한 노이즈로 보임.

### 예시와 기법

**고전 기법**: character marking(연필로 특정 글자 덧칠), invisible ink(투명 잉크), pin punctures(핀 구멍), typewriter correction ribbon(교정 리본으로 겹쳐 타이핑, 강한 빛 아래서만 보임)

**현대 기법**: 이미지의 **LSB(Least Significant Bit)**를 이용. 예: 2048×3072 픽셀, 픽셀당 24bit RGB인 사진이라면 각 픽셀의 최하위 비트 하나씩만 바꿔도 화질엔 거의 티가 안 남 → 사진 한 장에 2.3MB짜리 메시지를 숨길 수 있음.

### 장단점

- **단점**: 적은 정보 숨기는 데 비해 오버헤드가 큼, 시스템(숨기는 방식)이 발각되면 그 즉시 무용지물이 됨 → 보완책으로 메시지를 먼저 암호화한 뒤 숨기기도 함
- **장점**: 비밀 통신 당사자들이 "통신하고 있다는 사실" 자체를 숨길 수 있음

---

## 전체 흐름 정리

Substitution 계열은 매번 "이전 방식의 약점을 어떻게 메우는가"로 발전:

1. **Shift (Caesar)**: 알파벳을 통째로 k만큼 원형 이동. 키가 26개뿐이라 brute-force로 바로 뚫림.
2. **Monoalphabetic**: 26!개의 임의 순열을 키로 사용 — brute-force는 막았지만, 고정 매핑이라 글자 빈도 패턴이 그대로 남아 frequency analysis에 뚫림.
3. **Playfair / Hill**: 여러 글자(digram, 또는 m개)를 묶어서 치환 — 단일 글자 빈도는 숨겼지만, digram 빈도 자체가 여전히 보존돼서 통계적 공격에 뚫림. Hill은 특히 행렬 구조 때문에 known-plaintext엔 선형대수로 쉽게 깨짐.
4. **Vigenère**: 키워드 길이만큼 여러 개의 Caesar cipher를 번갈아 적용 — 단일 매핑을 없애서 빈도를 흐렸지만, 키가 반복되니까 키 길이를 알아내면 다시 여러 개의 독립적인 Caesar cipher 문제로 쪼개져서 풀림.
5. **One-Time Pad**: Vigenère의 근본 원인(키 반복)을 없앰 — 키를 plaintext만큼 길게, 완전 무작위로, 절대 재사용 안 하면 이론적으로 완벽하게 안전(unconditionally secure)해짐.

별도 축으로 **Transposition**(순서만 재배열, 글자 빈도는 그대로 보존)과, 이를 기계적으로 다단 반복해 거대한 키 공간을 만든 **Enigma**(substitution+transposition 결합), 그리고 완전히 다른 목표(내용 은닉이 아니라 존재 은닉)를 갖는 **Steganography**까지 다룸. 대부분의 개선은 "빈도 정보를 얼마나 잘 숨기느냐" 싸움이었고, 그 싸움의 끝판왕이 One-Time Pad.
