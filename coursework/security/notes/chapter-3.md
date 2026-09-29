# Chapter 3: User Authentication

*Hanyang University, Division of Computer Science and Engineering*

## 1. User Authentication 개념 *(슬라이드 p.3~4)*

### 정의 (RFC 4949) *(슬라이드 p.3)*
> "The process of verifying an identity claimed by or for a system entity."

### 인증 수단의 4가지 범주 *(슬라이드 p.4)*
사용자 신원을 확인하는 4가지 수단(개인이 알거나/가지거나/이거나/하는 것에 근거):
- **Something the individual knows**: 예 — password, PIN
- **Something the individual possesses**: 예 — key, token, smartcard
- **Something the individual is (static biometrics)**: 예 — fingerprint, retina
- **Something the individual does (dynamic biometrics)**: 예 — voice, sign

단독으로도, 조합해서도 사용 가능. 넷 다 인증을 제공할 수 있지만 각각 문제점(issue)을 가짐.

---

## 2. Password Authentication *(슬라이드 p.5~19)*

### 기본 동작 *(슬라이드 p.5)*
- 가장 널리 쓰이는 사용자 인증 방법
- 사용자가 name/login과 password를 제공 → 시스템이 저장된 password와 비교
- 로그인하는 사용자의 신원을 인증하고, 시스템 접근 권한이 있는지 확인하며, 사용자 권한(privilege)을 결정 → discretionary access control에 사용됨

### UNIX Implementation *(슬라이드 p.6~7)*
- 원본 방식: 8글자 password로 56-bit key 구성, 12-bit salt로 DES 암호화를 one-way hash function으로 변형, 0 값을 25회 반복 암호화, 출력을 11글자 시퀀스로 변환
- 현재는 매우 취약(woefully insecure)하다고 평가됨 — 예: 슈퍼컴퓨터로 5천만 번 시도에 80분
- 호환성 목적으로 여전히 일부 사용됨
- **Hashed Password 사용 흐름** (Figure) *(p.7)*:
  - (a) Loading a new password: salt(12bit)+password(56bit) → crypt(3) → 11 character 출력 → Password File(User id, salt, crypt(3) output)에 저장
  - (b) Verifying a password: User id로 Password File에서 salt 조회 → 입력 password와 salt로 crypt(3) 재계산 → 저장된 encrypted password와 compare

### Improved Implementations *(슬라이드 p.8)*
- 더 강력한 hash/salt variant들이 존재
- 다수 시스템이 현재 MD5 사용: 48-bit salt, password 길이 무제한, 내부 loop 1000회 반복 hash, 128-bit hash 출력

### Password Cracking *(슬라이드 p.9)*
- **Dictionary attacks**: 사전의 단어와 명백한 변형들을 password file의 hash와 하나씩 대조
- **Rainbow table attacks**: 모든 salt에 대한 hash 값 테이블을 미리 계산해둠 — 예: 1.4GB 테이블로 alphanumeric Windows password의 99.9%를 13.8초 만에 crack. salt 값이 크면 사용 불가능(not feasible)

### Password Choices의 문제 *(슬라이드 p.10)*
- 사용자가 짧은 password를 고르는 경우: 예 — 3%가 3글자 이하로 쉽게 추측됨 → 시스템이 너무 짧은 선택을 거부할 수 있음
- 사용자가 추측 가능한(guessable) password를 고르는 경우: crack하는 쪽은 유력 password 목록을 사용 — 예: 14000개 암호화된 password 연구에서 거의 1/4을 알아맞힘. 모든 변형을 계산하는 데 가장 빠른 시스템으로 약 1시간이 걸리지만 단 1번만 맞으면 됨

### Password Vulnerabilities (공격 유형 목록) *(슬라이드 p.11)*
offline dictionary attack, specific account attack, popular password attack, password guessing against single user, workstation hijacking, exploiting user mistakes, exploiting multiple password use, electronic monitoring

### Countermeasures *(슬라이드 p.12)*
password file에 대한 비인가 접근 차단, 침입탐지(intrusion detection) 대책, 계정 잠금(account lockout) 메커니즘, 흔한 password 대신 추측하기 어려운 password를 쓰도록 하는 정책, 정책에 대한 교육 및 시행, 자동 workstation logout, 암호화된 네트워크 링크

### Password File Access Control *(슬라이드 p.13)*
- 암호화된 password에 대한 접근을 거부함으로써 offline guessing 공격을 막을 수 있음
  - 권한 있는 사용자(privileged users)에게만 공개
  - 흔히 별도의 shadow password file을 사용
- 그래도 여전히 취약점 존재: OS 버그 악용, 권한 설정 실수로 읽기 가능해짐, 다른 시스템에서 동일 password를 쓰는 사용자, 보호되지 않은 backup media를 통한 접근, 보호되지 않은 네트워크 트래픽에서 password sniffing

### Using Better Passwords *(슬라이드 p.14)*
- 목표: 추측 가능한 password는 없애면서 사용자가 기억하기는 쉽게
- 기법: user education, computer-generated passwords, reactive password checking, proactive password checking

### Proactive Password Checking *(슬라이드 p.15~19)*
- 규칙 강제(rule enforcement) + 사용자 조언 — 예: 8자 이상, 대/소문자·숫자·구두점 포함 (그래도 충분하지 않을 수 있음) *(p.15)*
- password cracker 방식: 시간과 공간(time and space) 이슈 존재 *(p.15)*
- **Bloom Filter**를 이용해 사전 기반 해시 테이블을 만들고, 원하는 password를 이 테이블과 대조 *(p.15~19)*:
  1. Bloom filter of order k: k개의 독립적인 hash function H₁(x),…,Hₖ(x). 각 함수는 password를 0~N-1 범위의 hash 값으로 매핑 *(p.16)*
  2. N bit짜리 hash table을 0으로 초기화 *(p.16)*
  3. D개의 잘 알려진(well-known) password 준비 *(p.16)*
  4. 각 password마다 k개의 hash 값을 계산해서 테이블의 해당 bit를 1로 뒤집음 — 예: Hᵢ(Xⱼ)=67이면 테이블의 67번째 bit가 1 *(p.16)*
  5. 예시: k=3 hash function, N=15 bits, D=3개 password(X,Y,Z)를 15-bit 테이블에 매핑하는 그림 *(p.17)*
  6. 새 password가 checker에 제시되면 k개의 hash 값을 계산하고, 그 k개 bit가 모두 1이면 해당 password를 거부(reject) *(p.18)*
  7. False positive 확률: `P = (1 − e^(−k/R))^k`, 여기서 R = N/D *(p.18)*
  8. Figure 3.4: hash table size와 dictionary size의 비율(x축)에 따른 false positive 확률(y축, log scale)을 2/4/6개 hash function 각각에 대해 비교한 그래프 — hash function 개수와 비율에 따라 false positive율이 달라짐 *(p.19)*

---

## 3. Token Authentication *(슬라이드 p.20~23)*

사용자가 소지(possess)한 객체로 인증하는 방식 *(p.20)*: magnetic stripe card, memory card, smartcard

### Magnetic Card *(슬라이드 p.21)*
자기 물질(magnetic material) 밴드 위 미세한 철 입자의 자성을 변경해 데이터를 저장하는 카드. 저장 정보: Name, Credit card #/Account #, Exp date, Service code, CVC 등

### Memory Card *(슬라이드 p.22)*
- 전자 memory card(EEPROM/Flash memory) — 데이터를 저장만 하고 처리(process)는 하지 않음
- magnetic stripe card(예: 은행카드)도 memory card로 볼 수 있음
- 물리적 접근에는 단독으로, 컴퓨터 사용에는 password/PIN과 함께 사용
- 단점: 전용 reader 필요, 분실 시 문제, 사용자 불만, (medium 수준 보안 제공 — 카드가 복제(clone)될 수 있음)

### Smartcard *(슬라이드 p.23)*
- 외형은 신용카드와 유사, 자체 processor·memory·I/O port 보유 (RAM/EEPROM/ROM/CPU, crypto co-processor 포함 가능)
- reader/computer와 유선 또는 무선으로 접근, 인증 프로토콜을 실행
- 강점: 통신이 암호화됨, 메모리가 H/W 레벨에서 보호됨, private key를 안전하게 저장하고 메시지에 서명 가능

---

## 4. Biometric Authentication *(슬라이드 p.24~27)*

### 개요 *(슬라이드 p.24)*
사용자의 신체적 특징(physical characteristics) 중 하나에 근거해 인증. Cost(y축) vs Accuracy(x축) 좌표에 Hand/Signature/Face/Voice(저비용·저정확도)부터 Retina/Finger, 그리고 가장 비싸고 정확한 Iris까지 배치한 그림.

### Biometric System의 3가지 동작 모드 (Figure) *(슬라이드 p.25)*
공통 구성: User interface(Name/PIN 입력) → Biometric sensor → Feature extractor
- **(a) Enrollment**: feature extractor의 출력을 DB에 template으로 저장
- **(b) Verification**: feature extractor 출력을 DB의 **One template**과 Feature matcher가 비교 → true/false 반환 (1:1 비교)
- **(c) Identification**: Name/PIN 없이, feature matcher가 DB의 **N templates** 전체와 비교 → user's identity 또는 "user unidentified" 반환 (1:N 비교)

### Biometric Accuracy *(슬라이드 p.26~27)*
- 두 template이 완전히 동일하게 나오는 경우는 없음(never get identical templates) → false match / false non-match 문제 발생
- Decision threshold(t)를 기준으로, imposter profile과 genuine user profile의 matching score 분포가 겹치는 영역에서 false nonmatch(threshold 왼쪽 겹침)와 false match(threshold 오른쪽 겹침)가 발생 *(p.26)*
- Figure 3.11: Face/Fingerprint/Voice/Hand/Iris 각 생체인식 방식의 실제 측정치를 false match rate(x축) vs false nonmatch rate(y축) log-log 그래프로 비교 — Iris가 가장 낮은 error rate, Face가 상대적으로 높은 error rate를 보임 *(p.27)*

---

## 5. Remote User Authentication *(슬라이드 p.28~34)*

### 개요 *(슬라이드 p.28)*
- 네트워크·인터넷·통신 링크를 통한 인증은 더 복잡함
- 추가적인 보안 위협: eavesdropping, password capture, 관찰된 인증 시퀀스의 재전송(replay)
- 일반적으로 이런 위협에 대응하기 위해 challenge-response protocol에 의존

### Key Distribution Center (KDC) *(슬라이드 p.29~30)*
- Alice가 Bob과 통신하고 싶을 때, KDC가 Alice/Bob 각각의 키(K_Alice, K_Bob)로 암호화된 메시지를 통해 세션키(K_AB)를 배포
- Ticket for Bob := K_Bob{Use K_AB for Alice} 형태로, Alice가 Bob에게 자신을 인증시킬 티켓을 전달 *(p.29)*
- **Needham-Schroeder**: KDC 동작과 인증을 결합. Replay 공격을 막기 위해 timestamp 대신 **nonce**(한 번만 쓰이는 순차적/무작위 수)를 사용 *(p.30)*

### Needham-Schroeder Protocol *(슬라이드 p.31~32)*
- **(Insecure version)** *(p.31)*: Alice → KDC: N₁, Alice, Bob / KDC → Alice: K_Alice{N₁, Bob, K_AB, ticket to Bob} / Alice → Bob: Ticket, K_AB{N₂} / Bob → Alice: K_AB{N₂-1, N₃} / Alice → Bob: K_AB{N₃-1}, 여기서 Ticket = K_Bob{K_AB, Alice}
- **Extended Needham-Schroeder** *(p.32)*: Bob도 자신의 nonce(N_B)를 먼저 제시하도록 확장한 버전 — Alice↔Bob이 "I want to talk to you" / K_Bob{N_B}로 먼저 교환한 뒤, Alice→KDC→Alice로 티켓을 받고, 이후 Alice↔Bob이 K_AB 기반 nonce 교환(N₂, N₃)으로 상호 인증을 완료

### Kerberos *(슬라이드 p.33)*
- MIT에서 개발
- 분산 client/server 구조를 가정, 하나 이상의 Kerberos 서버 사용
- 분산 인증 및 key distribution 시스템 — 분산 네트워크에서 중앙화된 private-key 기반 third-party 인증 제공. 사용자가 모든 workstation을 신뢰할 필요 없이, 중앙 인증 서버 하나만 신뢰하면 네트워크 전역의 서비스에 접근 가능
- v4, v5 두 버전이 사용 중이며, Needham-Schroeder 기반의 인증 프로토콜로 구현됨 (세부 분산 프로토콜 스펙은 생략)

### Mutual Authentication using Public Key Cryptography — EAP *(슬라이드 p.34)*
- **EAP (Extensible Authentication Protocol)**: IEEE 802.3, IEEE 802.11(WiFi), IEEE 802.16, IEEE 802.1x 인증 프레임워크 (RFC 5247)
- client-server 인증을 위한 범용 인증 프레임워크로, EAP-MD5, EAP-TLS, EAP-TTLS, EAP-FAST, EAP-PEAP 등 40개 이상의 EAP 방식이 존재

---

## 핵심 요약

- **인증 4범주**: knows(password) / possesses(token) / is(static biometric) / does(dynamic biometric)
- **Password**: UNIX crypt(3)+salt → MD5 개선 → dictionary/rainbow table 공격에 대응해 access control·proactive checking(Bloom filter)으로 방어
- **Token**: magnetic stripe(단순 저장) → memory card(저장, 별도 reader) → smartcard(자체 연산·암호화 가능, 가장 강력)
- **Biometric**: enrollment/verification(1:1)/identification(1:N) 세 동작 모드, threshold에 따른 false match/false nonmatch trade-off, 방식별 정확도는 Iris > Fingerprint > Hand/Voice > Face 순
- **Remote authentication**: KDC + nonce 기반 challenge-response(Needham-Schroeder) → Kerberos(중앙화된 분산 인증)로 발전, 공개키 기반 상호인증 프레임워크로 EAP 계열 존재
