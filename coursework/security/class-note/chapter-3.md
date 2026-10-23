# Chapter 3 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*(수업일: 2026-10-23, 참조 노트: `notes/chapter-3.md`)*

## 1. User Authentication 개념 *(p.3~4)*

**User authentication**: 시스템 엔티티가 주장하는(혹은 누군가 그 엔티티를 대신해 주장하는) 신원이 진짜인지 검증하는 과정 (RFC 4949).

"내가 누구라고 말하는 것"(identification)과 "그게 사실인지 확인하는 것"(authentication)은 달라. ID 입력은 주장이고, password 같은 걸 확인하는 게 검증이야.

| 범주 | 예시 |
|---|---|
| Something you **know** | password, PIN |
| Something you **possess** | key, token, smartcard |
| Something you **are** (static biometrics) | fingerprint, retina |
| Something you **do** (dynamic biometrics) | voice, signature |

단독으로도 조합해서도 쓰고, 넷 다 각각 문제점이 있어.

**Q&A**
- ATM에서 카드 + PIN → possess + know의 조합.
- static vs dynamic: static은 몸 자체의 물리적 특징(지문, 망막), dynamic은 행동 패턴(서명할 때의 필압·속도, 말할 때의 음성 특성). 슬라이드는 voice도 dynamic으로 분류.

---

## 2. Password Authentication *(p.5~19)*

**Password authentication**: 사용자가 name과 password를 제시하면, 시스템이 저장해 둔 password 정보와 비교해서 신원을 확인하는 가장 널리 쓰이는 방식. 결과로 접근 권한 여부와 privilege를 결정하고 discretionary access control에도 쓰여 *(p.5)*.

### 2-1. UNIX 구현 *(p.6~8)*

**등록(Loading)**
1. password(최대 8글자)로 56-bit key를 만든다.
2. 시스템이 12-bit **salt**를 붙인다.
3. DES를 one-way hash처럼 써서 0 값을 25번 반복 암호화한다.
4. 결과를 11글자로 변환해 password file에 `(User id, salt, 결과)`로 저장한다.

**로그인(Verifying)**
1. User id로 password file에서 salt를 찾는다.
2. 입력된 password와 그 salt로 똑같이 계산한다.
3. 저장된 값과 비교한다.

지금 기준으로는 매우 취약(슈퍼컴퓨터로 5천만 번 시도에 80분)해서 호환성 목적으로만 남아 있어. 개선판 MD5는 48-bit salt, password 길이 무제한, 내부 loop 1000회, 128-bit 출력 *(p.8)*.

### Salt

**Salt**: password를 해시하기 전에 함께 섞어 넣는, 사용자마다 다르게 정해지는 임의의 값. 비밀이 아니고, 같은 password라도 결과가 달라지게 만드는 게 목적.

- **salt는 암호화된 게 아니라 평문으로 저장돼.** 로그인 때 시스템이 꺼내 써야 하니까. 또 여기서 목적은 복호화가 아니야. password 자체가 key 역할을 하는 단방향 변환이고, 공격자는 "추측 → 같은 방식으로 계산 → 대조"로 공격해.
- **salt가 없을 때**: A, B가 같은 `abc123`을 쓰면 파일에 똑같은 해시가 저장돼 같은 password라는 게 드러나고, `password → 해시` 대응표(rainbow table)로 찾기만 하면 돼 (p.9의 "1.4GB 테이블로 99.9%를 13.8초").
- **salt가 있을 때**: `hash(password + salt)`라서 같은 password도 해시가 달라. 12-bit salt면 같은 password에 4096가지 해시가 나올 수 있어서 공격자는 salt마다 표를 따로 만들어야 하고, salt가 클수록 사전 계산이 비현실적이 돼 ("salt 값이 크면 rainbow table은 not feasible").
- salt가 막는 건 "해시를 되돌리는 것"이 아니라 "미리 계산한 표의 재사용"과 "동일 password 식별". 한 줄로: **공격자의 사전계산을 무력화하는 장치**.

**계산 횟수 비교** (사용자 1만 명, 후보 `abc123` 하나, 사전 표 없음)
- salt 없음: `hash(abc123)` 1번 계산 → 1만 개 항목과 대조.
- salt 있음: 사용자마다 salt가 달라 `hash(abc123 + salt_i)`를 각각 → 최대 1만 번.
- 후보가 100만 개면 salt 없을 땐 100만 번, 있으면 최대 100억 번.

### 2-2. Password Cracking *(p.9)*
- **Dictionary attack**: 사전의 단어와 그 변형(`password1`, `P@ssw0rd`)을 하나씩 해시해서 파일의 값과 대조.
- **Rainbow table attack**: 모든 salt에 대한 해시를 미리 계산해 둔 표. salt가 크면 쓸 수 없음.

### 2-3. 사용자 선택의 문제 *(p.10)*
- 너무 짧은 경우: 한 연구에서 3%가 3글자 이하. 시스템이 너무 짧은 선택을 거부하기도 함.
- 추측 가능한 경우: 14000개 분석에서 거의 1/4을 알아맞힘. 모든 변형 계산에 약 1시간이 걸려도, 공격자는 **단 하나만 맞히면** 됨.

**Q&A**: "단 하나만 맞히면 된다"가 왜 비대칭인가 → 공격자는 수많은 시도 중 하나만 얻어걸려도 뚫리고, 방어자는 모든 사용자의 password가 전부 강해야 한다. 그래서 사용자의 선택에만 맡기지 않고 강제하는 장치가 필요.

### 2-4. 공격 유형과 대응 *(p.11~12)*

| 공격 | 의미 |
|---|---|
| offline dictionary attack | 훔친 password file을 가져가 오프라인에서 마음껏 대입 (시도 횟수 제한 없음) |
| specific account attack | 특정 계정 하나를 골라 집중 추측 |
| popular password attack | 흔한 password 목록을 여러 계정에 돌려봄 |
| password guessing against single user | 그 사용자의 정보(생일, 이름 등)를 알아내 추측 |
| workstation hijacking | 자리를 비운 사이 로그인된 워크스테이션을 가로챔 |
| exploiting user mistakes | 포스트잇, 공유, 피싱 등 사용자 실수 악용 |
| exploiting multiple password use | 한 곳에서 유출된 password를 다른 사이트에 재사용 |
| electronic monitoring | 네트워크 sniffing 등으로 전송 중인 password를 엿봄 |

대응책(공격과 짝지어):
- password file 접근 차단 → offline attack
- account lockout → 특정 계정 추측 공격
- 침입탐지 → 비정상 시도 감지
- 추측하기 어려운 password 정책 + 교육/시행 → popular/guessing/사용자 실수
- 자동 workstation logout → hijacking
- 암호화된 네트워크 링크 → electronic monitoring

**Q&A: lockout이 offline dictionary attack에는 왜 소용없나**
- online 공격은 실제 로그인 화면에 시도를 보내서 시스템이 횟수를 세고 N번 틀리면 잠글 수 있음.
- offline 공격은 훔친 파일을 자기 컴퓨터로 가져가 혼자 해시를 계산해 대조함. 시스템과 상호작용이 없어서 시스템은 공격이 일어나는지도 모르고, lockout은 "로그인 시도"를 세는 장치인데 로그인 시도가 아예 없음. 시도 횟수 무제한.
- (여러 계정에 돌려가며 시도하는 건 lockout을 우회하는 popular password attack이고 offline이 안 막히는 이유는 아님.)
- 막으려면 file을 못 훔치게 하거나(2-5) password를 약하지 않게(2-6) 해야 함.

### 2-5. Password File Access Control *(p.13)*
- 해시된 password 자체를 못 보게 해서 offline guessing을 막음.
- 권한 있는 사용자에게만 공개, 흔히 별도의 **shadow password file** 사용.
- 그래도 남는 취약점: OS 버그 악용, 권한 설정 실수, 다른 시스템에서 같은 password를 쓰는 사용자, 보호 안 된 backup media, 보호 안 된 네트워크 sniffing.
- 접근 통제는 방어 한 겹일 뿐이고, 뚫릴 때를 대비해 password 자체도 강해야 함.

### 2-6. 더 좋은 Password 쓰기 *(p.14)*
목표: 추측 가능한 password는 없애면서 사용자가 기억하기는 쉽게.
1. **User education**
2. **Computer-generated passwords**: 강하지만 사용자가 못 외워서 적어두게 됨.
3. **Reactive password checking**: 시스템이 주기적으로 직접 cracker를 돌려 추측되는 password를 찾아 알려줌. 자원이 많이 들고, 발견 전까지 취약한 채로 남음.
4. **Proactive password checking**: password를 정하는 순간 검사해서 약하면 거부.

**Q&A**: 취약한 기간이 더 짧은 쪽은 proactive. reactive는 일단 들어온 뒤 다음 cracker 실행 때까지 취약하고, proactive는 약한 password가 시스템에 아예 들어오지 못함.

### 2-7. Proactive Password Checking *(p.15~19)*

**Proactive password checking**: 사용자가 password를 새로 정할 때 시스템이 즉시 검사해서, 약하면 거부하고 다시 고르게 하는 방식.

검사 방법 두 갈래 *(p.15)*:
- ① 규칙 강제 + 조언: 8자 이상, 대/소문자·숫자·구두점 포함 등. `Password1!`처럼 규칙은 다 만족해도 흔한 password일 수 있어 충분하지 않을 수 있음.
- ② Cracker처럼 사전과 대조: 시간과 공간 문제(사전이 크면 저장도 검색도 부담). → **Bloom filter**로 가볍게.

**Bloom filter**: 집합에 어떤 원소가 들어 있는지를 작은 bit 배열과 여러 hash function으로 빠르게 확인하는 자료구조. 사전 전체 대신 bit 배열 하나만 보관.

만들기 *(p.16)*:
1. k개의 독립적인 hash function H₁(x),…,Hₖ(x) 준비. 각각 password를 0~N-1 범위의 값으로 변환.
2. N bit짜리 테이블을 전부 0으로 초기화.
3. 잘 알려진 password D개 준비.
4. 각 password마다 k개의 hash 값을 계산해 그 위치의 bit를 1로 (예: Hᵢ(Xⱼ)=67이면 67번째 bit가 1).

예시(p.17): k=3, N=15 bits, 사전 password 3개(X,Y,Z)를 15-bit 테이블에 매핑.

검사 *(p.18)*: 새 password의 k개 hash 위치가 **전부 1이면 거부**, 하나라도 0이면 통과.

False positive(사전에 없는데 우연히 k개 위치가 이미 다 1이라 잘못 거부): `P = (1 − e^(−k/R))^k`, R = N/D. 테이블이 클수록(R↑) 줄어듦. Figure 3.4(p.19)는 R(x축)에 따른 false positive 확률을 hash function 2/4/6개로 비교.

**Q&A**: false negative(사전에 있는 password를 통과시키는 오류)는 없다. 만들 때 bit를 0→1로만 바꾸고 되돌리지 않으니, 사전에 있는 password는 검사 때 같은 k개 위치가 항상 전부 1. 즉 안전한 방향으로만 틀리는 구조: 약한 password를 놓치진 않고, 가끔 멀쩡한 password를 거부할 뿐.

---

## 3. Token Authentication *(p.20~23)*

**Token authentication**: 사용자가 소지(possess)한 물리적 객체로 신원을 인증하는 방식. 대표 예: magnetic stripe card, memory card, smartcard *(p.20)*.

### Magnetic Card *(p.21)*
자기 물질로 된 띠의 미세한 철 입자의 자성을 바꿔 데이터를 저장. 저장 정보: 이름, 카드/계좌 번호, 만료일, service code, CVC 등.

### Memory Card *(p.22)*
- 전자식(EEPROM/Flash) 메모리에 데이터를 저장만 하고 처리(process)는 하지 않음. magnetic stripe 은행카드도 memory card로 봄.
- 물리적 접근에는 단독으로, 컴퓨터 사용에는 password/PIN과 함께 (ATM).
- 단점: 전용 reader 필요, 분실 문제, 사용자 불만. 보안 수준 medium, 저장만 하므로 **복제(clone) 가능**.

### Smartcard *(p.23)*
**Smartcard**: 카드 안에 자체 processor, memory, I/O port를 갖고 인증 프로토콜을 직접 실행하는 카드.
- 외형은 신용카드와 비슷, RAM/EEPROM/ROM/CPU가 들어 있고 crypto co-processor까지 있는 경우도 있음.
- reader/컴퓨터와 유선 또는 무선으로 통신.
- 강점: 통신이 암호화됨, 메모리가 하드웨어 레벨에서 보호됨, private key를 안전하게 저장하고 메시지에 서명 가능.

**Q&A: memory card는 복제되는데 smartcard는 왜 어려운가**
- "컴퓨터까지 복사해야 해서"가 아니라 **복사할 대상을 읽어낼 수 없어서**가 핵심.
- memory card: 데이터가 카드에 그대로 있고 reader가 읽어 감 → 읽을 수 있으면 복사 가능, 같은 데이터를 다른 카드에 쓰면 끝.
- smartcard: private key가 하드웨어로 보호된 메모리 안에 있고 카드 밖으로 나오지 않음. reader가 "서명해 줘"라고 요청하면 카드 안의 CPU가 서명해서 결과만 내보냄. 키를 읽어낼 인터페이스 자체가 없어서 복제하려면 카드를 뜯어 보호된 메모리를 공격해야 함.
- 한 줄: memory card는 비밀을 **보여주는** 카드, smartcard는 비밀을 **쓰기만 하고 보여주지 않는** 카드.

---

## 4. Biometric Authentication *(p.24~27)*

**Biometric authentication**: 사용자의 고유한 신체적·행동적 특징을 측정해서 신원을 인증하는 방식 *(p.24)*.

비용·정확도(p.24 그림): Hand/Signature/Face/Voice는 저비용·저정확도, Retina/Finger는 중간, **Iris**가 가장 비싸고 가장 정확.

### 3가지 동작 모드 *(p.25)*
공통: User interface(Name/PIN) → Biometric sensor → Feature extractor.

| 모드 | 하는 일 |
|---|---|
| **Enrollment** | 추출한 특징을 DB에 template으로 저장 |
| **Verification** | Name/PIN을 입력받고 DB에서 그 사람의 template 하나와 비교 → true/false (**1:1**) |
| **Identification** | Name/PIN 없이 DB의 N개 template 전부와 비교 → "누구다" 또는 "unidentified" (**1:N**) |

**Q&A**
- 스마트폰 지문 잠금 해제 → verification. "나는 이 폰 주인이다"라는 주장이 이미 있고 주인의 template 하나와 비교.
- 범죄 현장 지문으로 용의자 찾기 → identification. 주장하는 사람이 없어 DB 전체와 비교. 1:N은 비교 대상이 많은 만큼 오인 기회도 많다.

### Biometric Accuracy *(p.26~27)*
- 같은 사람이 같은 손가락을 대도 센서 값이 매번 조금씩 달라서 template과 **완전히 똑같이 나오는 일은 없음**. 그래서 "얼마나 비슷하면 같은 사람으로 볼까"를 정하는 **decision threshold(t)** 가 필요하고, 오류가 두 종류 생김.
- **False match**: 다른 사람(imposter)인데 같은 사람으로 판정해 통과시킴 → 보안 사고.
- **False nonmatch**: 진짜 사용자(genuine)인데 다른 사람으로 판정해 거부 → 불편.
- p.26 그림: imposter와 genuine의 matching score 분포가 겹치고, threshold를 어디에 긋든 겹치는 구간에서 한쪽은 틀림.
- Trade-off: threshold를 엄격하게 하면 false match↓ false nonmatch↑, 느슨하게 하면 false nonmatch↓ false match↑. 둘을 동시에 0으로 만들 수 없음.
- Figure 3.11(p.27): false match rate(x)와 false nonmatch rate(y)를 log-log로 그린 그래프. 원점에 가까울수록 좋음 → **Iris가 가장 낮은 오류율**, **Face가 상대적으로 높은 오류율**.

**Q&A: threshold 설정**
- 핵시설 출입문 → 엄격하게. false match 한 번의 피해가 치명적이라 정당한 직원의 재시도 불편을 감수.
- 도서관 출입 게이트 → 느슨하게. false match 피해가 작고 false nonmatch로 줄 서는 불편이 더 큼.
- 어느 오류가 더 비싼지를 보고 정한다.

---

## 5. Remote User Authentication *(p.28~34)*

**Remote user authentication**: 네트워크·인터넷 같은 통신 링크를 통해 떨어진 곳에서 하는 인증 *(p.28)*.

추가 위협: **eavesdropping**(엿듣기), **password capture**(전송 중 가로채기), **replay**(관찰한 인증 과정을 그대로 재전송). 대응으로 보통 **challenge-response protocol**을 씀: 서버가 매번 다른 도전값(challenge)을 보내고 클라이언트가 그에 맞는 응답을 계산해 보냄. 응답이 매번 달라서 가로채서 재전송해도 통하지 않음.

### Key Distribution Center (KDC) *(p.29~30)*
- Alice가 Bob과 안전하게 통신하려면 공유 세션키 **K_AB**가 필요. 모든 쌍이 미리 키를 나눠 갖기 어려우니, 모두가 신뢰하는 **KDC**가 세션키를 만들어 나눠줌. 각 사용자는 KDC와만 키를 공유(K_Alice, K_Bob).
- KDC가 K_AB를 만들어 Alice에게는 K_Alice로 암호화해 보내고, Bob에게 전달할 **ticket**은 K_Bob으로 암호화.
- **Ticket for Bob** := K_Bob{ Use K_AB for Alice }. Alice는 K_Bob이 없어서 열어볼 수 없고 그대로 Bob에게 전달만 함. Bob이 열면 "Alice와 K_AB로 통신하라"는 내용이 있어 KDC가 보증한 신원임을 알 수 있음 *(p.29)*.
- **Needham-Schroeder**: KDC의 키 배포와 인증을 합친 프로토콜. replay 방지에 timestamp 대신 **nonce**(한 번만 쓰는 수)를 씀 *(p.30)*.

**Q&A: nonce가 replay를 막는 방식**
- Alice가 요청마다 새 nonce N₁을 만들어 같이 보냄 → KDC가 응답 안에 N₁을 넣어 암호화해 돌려줌 → Alice가 받은 응답의 N₁이 방금 자기가 보낸 것과 같은지 확인.
- 어제 캡처한 응답에는 어제의 nonce가 들어 있어 오늘의 N₁과 달라 걸러짐. 응답이 K_Alice로 암호화되어 있어 공격자가 nonce만 바꿔치기할 수도 없음. timestamp와 달리 시계를 맞출 필요가 없는 것도 장점.

### Needham-Schroeder Protocol *(p.31~32)*
Ticket = K_Bob{ K_AB, Alice } 일 때 (insecure version, p.31):
1. Alice → KDC: `N₁, Alice, Bob`
2. KDC → Alice: `K_Alice{ N₁, Bob, K_AB, Ticket }`
3. Alice → Bob: `Ticket, K_AB{ N₂ }`
4. Bob → Alice: `K_AB{ N₂−1, N₃ }` (N₂−1은 "나는 K_AB를 안다"는 증명 + Bob의 도전)
5. Alice → Bob: `K_AB{ N₃−1 }`

4~5단계가 **상호 인증**: 서로 상대가 K_AB를 아는지 nonce를 변형해 되돌려주며 확인. −1은 받은 값을 그대로 돌려주면 단순 반사 공격이 될 수 있어 가공했다는 것을 보이는 장치.

이 버전이 insecure인 이유: 3단계에서 Bob이 받는 ticket이 새것인지 알 방법이 없음. 공격자가 오래전에 캡처한 ticket(과 어떻게든 알아낸 옛 K_AB)을 재전송하면 Bob은 구분하지 못함.

**Extended Needham-Schroeder** *(p.32)*: Alice가 Bob에게 "I want to talk to you"를 보내면 Bob이 `K_Bob{ N_B }`를 돌려줌. Alice는 이걸 KDC에 넘겨 ticket을 받아오고, 그 ticket 안에 **Bob의 N_B**가 들어감. 이후 Alice↔Bob이 K_AB로 N₂, N₃를 교환해 상호 인증을 마침.

**Q&A: N_B가 왜 옛 ticket 재전송을 막나**
- Bob이 매번 새 N_B를 만들어 Alice에게 주고, Alice가 받아오는 ticket에는 그 N_B가 K_Bob으로 암호화되어 들어 있음. Bob은 ticket을 열어 안의 N_B가 자기가 방금 낸 값과 같은지 확인.
- 옛 ticket에는 옛날 N_B가 있어 Bob이 기다리는 값과 달라 거부됨. N_B를 새 값으로 바꿔치기하려 해도 ticket이 K_Bob으로 암호화되어 있어 못 건드림.
- 기본 버전은 Alice 쪽만 신선도(freshness)를 확인했고 Bob은 못 했던 것이 구멍. extended는 Bob이 직접 자기 쪽 신선도를 확인.

### Kerberos *(p.33)*
**Kerberos**: 분산 네트워크에서 중앙 인증 서버가 사용자와 서비스를 서로 인증해 주는, Needham-Schroeder 기반의 third-party 인증·키 배포 시스템 (MIT 개발).
- 분산 client/server 구조를 가정하고 Kerberos 서버를 하나 이상 둠.
- 사용자가 모든 workstation을 신뢰할 필요 없이 중앙 인증 서버 하나만 신뢰하면 네트워크 전역의 서비스에 접근 가능.
- v4, v5가 쓰이고 세부 프로토콜은 이 수업에서 생략.

### EAP *(p.34)*
**EAP (Extensible Authentication Protocol)**: client-server 인증을 위한 범용 인증 **프레임워크**. 하나의 고정된 방식이 아니라 여러 인증 방식을 끼워 넣을 수 있는 틀 (RFC 5247).
- IEEE 802.3, 802.11(WiFi), 802.16, 802.1x의 인증에 쓰임.
- EAP-MD5, EAP-TLS, EAP-TTLS, EAP-FAST, EAP-PEAP 등 40개 이상의 방식이 있음.
- 슬라이드 제목이 "공개키 기반 상호 인증"이므로 공개키 방식(예: EAP-TLS)으로 상호 인증하는 맥락.

---

## 3강 한 줄 정리

| 범주 | 약점 | 3강의 보완 |
|---|---|---|
| **Password (know)** | 추측·cracking에 취약(dictionary, rainbow table), 사용자가 약한 걸 고름, 훔친 파일을 offline으로 공격 | salt, shadow file, proactive checking(Bloom filter), lockout |
| **Token (possess)** | 분실·도난, memory card는 복제 가능 | 자체 연산과 key 보호가 있는 smartcard, 보통 PIN과 병행 |
| **Biometric (is, does)** | 완전히 같은 값이 안 나와서 false match/nonmatch 발생, 방식마다 정확도·비용 다름 | threshold 조절, 정확도 높은 방식(Iris) 선택 |
| **Remote 인증** | eavesdropping, password capture, replay | challenge-response, KDC + nonce(Needham-Schroeder), Kerberos, EAP |
