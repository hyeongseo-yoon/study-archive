# Chapter 2: Application Layer

*Computer Networking: A Top-Down Approach, 8th ed. (Kurose & Ross)*

> 이 자료는 슬라이드 우측 하단에 "Application Layer: 2-N" 형식의 쪽번호가 있어, 아래 `p.N`은 그 N을 그대로 가리킨다.

## 1. Network Application의 기본 원칙 *(p.2~16)*

### 목표와 학습 방식 *(p.2~3)*
- 이 장의 목표: application-layer protocol의 **개념적 측면과 구현적 측면**을 모두 배움 — transport-layer service model, client-server/P2P paradigm
- HTTP, SMTP/IMAP, DNS, 비디오 스트리밍/CDN 같은 실제 프로토콜을 examining하며 배우고, socket API로 네트워크 프로그래밍도 배움

### Creating a Network App *(p.5)*
- (서로 다른) end system에서 동작하며 네트워크로 통신하는 프로그램을 작성 — 예: web server 소프트웨어가 browser 소프트웨어와 통신
- **network-core 장치를 위한 소프트웨어는 작성할 필요 없음** — network-core 장치는 user application을 실행하지 않으며, application이 end system에 있다는 사실이 빠른 앱 개발/전파를 가능케 함

### Client-Server Paradigm *(p.6)*
- **server**: 항상 켜져 있는 host, 영구적인 IP address, 확장을 위해 주로 data center에 위치
- **client**: server에 접속/통신, 간헐적으로 연결될 수 있고 IP가 동적일 수 있음, **client끼리는 직접 통신하지 않음**
- 예: HTTP, IMAP, FTP

### Peer-to-Peer (P2P) Architecture *(p.7)*
- 항상 켜져 있는 서버가 **없음**, 임의의 end system끼리 직접 통신
- peer가 다른 peer로부터 서비스를 요청하고, 다른 peer에게 서비스를 제공 — **self scalability**(새 peer가 새 서비스 용량과 새 서비스 수요를 함께 가져옴)
- peer는 간헐적으로 연결되고 IP가 바뀜 → 관리가 복잡함
- 예: P2P file sharing(BitTorrent), streaming(KanKan), VoIP(Skype)

### Processes Communicating *(p.8~10)*
- **process**: host 안에서 실행 중인 프로그램. 같은 host 안 두 프로세스는 OS가 정의하는 **inter-process communication**으로 통신, 다른 host의 프로세스는 **message**를 주고받으며 통신
- **client process**: 통신을 시작하는 프로세스 / **server process**: 접속을 기다리는 프로세스 (P2P 앱도 client·server process를 모두 가짐)
- **Socket**: process가 메시지를 보내고 받는 통로 — "문(door)"에 비유. 두 socket이 관여(양쪽 각각 하나씩). socket은 app 개발자가 통제하는 application layer와, OS가 통제하는 transport layer 사이의 경계
- **Addressing processes**: 메시지를 받으려면 process가 **identifier**(IP address + port number)를 가져야 함 — host의 IP만으로는 process를 식별할 수 없음(한 host에 여러 프로세스가 동시에 실행되므로). 예: HTTP server 포트 80, mail server 포트 25

### Application-Layer Protocol이 정의하는 것 *(p.11)*
교환되는 **메시지 종류**(request/response), **메시지 문법**(필드와 구분 방식), **메시지 의미론**(필드 정보의 의미), 메시지를 언제/어떻게 주고받을지의 **규칙**
- **open protocol**: RFC로 정의, 누구나 접근 가능, 상호운용성(interoperability) 보장 — 예: HTTP, SMTP
- **proprietary protocol**: 예 — Skype, Zoom

### Transport Service 요구사항 *(p.12~15)*
- **data integrity**: 파일전송·웹거래는 100% 신뢰성 필요, audio 등은 일부 loss 허용
- **timing**: 인터넷전화·인터랙티브게임은 낮은 delay가 필요
- **throughput**: 멀티미디어는 최소 throughput 필요("elastic app"은 주어지는 대로 사용)
- **security**: 암호화, 데이터 무결성 등
- Table(p.13): file transfer/e-mail/Web은 no loss·elastic·not time sensitive / real-time audio·video는 loss-tolerant·시간에 민감 / interactive games는 loss-tolerant·Kbps+·시간에 민감 / text messaging은 no loss·elastic·경우에 따라 다름
- **TCP service**: reliable transport, flow control(수신자를 압도하지 않음), congestion control(네트워크 과부하 시 sender를 조절), connection-oriented, timing·최소 throughput·보안은 제공 안 함
- **UDP service**: unreliable data transfer, reliability·flow control·congestion control·timing·throughput 보장·보안·connection setup 중 어느 것도 제공 안 함 — 그럼에도 존재하는 이유는 후속 강의(전송계층)에서 다룸
- Table(p.15): file transfer(FTP)/e-mail(SMTP)/Web(HTTP)은 TCP, 인터넷전화(SIP/RTP)는 TCP or UDP, streaming(HTTP/DASH)는 TCP, interactive games는 UDP or TCP

### Securing TCP — TLS *(p.16)*
- vanilla TCP/UDP socket은 암호화가 없어 평문 비밀번호가 그대로 인터넷을 통과함
- **TLS(Transport Layer Security)**: 암호화된 TCP 연결, 데이터 무결성, 종단점 인증(end-point authentication)을 제공하며 **application layer에서** 구현됨 — app이 TLS 라이브러리를 사용하고, 그 라이브러리가 다시 TCP를 사용

---

## 2. Web and HTTP *(p.18~54)*

### 복습: Web 객체와 URL *(p.18)*
Web page는 여러 **object**(HTML 파일, JPEG, Java applet, audio 등)로 구성 — base HTML 파일이 여러 referenced object를 포함하고, 각 object는 URL(host name + path name)로 주소를 가짐

### HTTP 개요 *(p.19~20)*
- **HTTP(HyperText Transfer Protocol)**: Web의 application-layer protocol, client-server 모델 — client(브라우저)가 요청·수신·"표시", server가 요청에 응답해 객체를 전송
- **HTTP는 TCP를 사용**: client가 server(포트 80)에 TCP connection(socket) 생성 → server가 접속 수락 → HTTP 메시지 교환 → TCP 연결 종료
- **HTTP는 "stateless"**: server가 과거 client 요청에 대한 정보를 유지하지 않음. state를 유지하는 프로토콜은 복잡함(과거 이력을 유지해야 하고, 서버/클라이언트가 crash하면 view가 불일치해 조정이 필요)

### HTTP Connection의 두 유형 *(p.21~25)*
- **Non-persistent HTTP**: TCP connection open → 최대 1개 object 전송 → connection close. 여러 object를 받으려면 여러 connection이 필요 *(p.21~23)*
- **response time**: `RTT(연결 개시) + RTT(요청+응답 첫 바이트) + 전송시간` = **2RTT + file transmission time** *(p.24)*
- **Persistent HTTP (HTTP 1.1)**: server가 응답 후에도 connection을 열어둠, 같은 client-server 간 후속 HTTP 메시지가 그 connection을 재사용, client는 참조된 object를 발견하는 즉시 요청 전송 → 이론상 모든 객체에 **1 RTT**로 충분(response time 절반으로 단축) *(p.25)*
- Non-persistent의 문제: object당 2 RTT, 매 TCP connection마다 OS 오버헤드, 브라우저가 병렬 connection을 여러 개 열어 우회하기도 함 *(p.25)*

### HTTP 메시지 형식 *(p.26~30)*
- **Request message**: ASCII(사람이 읽을 수 있는 형식). request line(**method** + URL + version) + header line들(각 줄 끝은 carriage-return/line-feed) + 헤더 끝을 알리는 빈 줄 + body *(p.26~27)*
- **Methods**: **GET**(URL의 `?` 뒤에 데이터를 붙여 서버로 전송), **POST**(폼 입력을 entity body에 담아 전송), **HEAD**(GET 했을 때 반환될 헤더만 요청), **PUT**(지정 URL의 파일을 entity body 내용으로 완전히 교체·업로드) *(p.28)*
- **Response message**: status line(protocol + status code + status phrase, 예 `HTTP/1.1 200 OK`) *(p.29)*
- **Status code**: `200 OK`(성공) / `301 Moved Permanently`(Location: 필드에 새 위치) / `400 Bad Request`(요청을 이해 못함) / `404 Not Found`(문서 없음) / `505 HTTP Version Not Supported` *(p.30)*
- 직접 체험: `nc`로 웹서버 80번 포트에 접속해 GET 요청을 직접 타이핑해볼 수 있음(또는 Wireshark로 캡처) *(p.31)*

### Cookies — 상태 유지 *(p.32~41)*
- HTTP GET/response는 **stateless** — client/server가 multi-step exchange의 "state"를 추적할 필요가 없고, 모든 요청이 서로 독립적이며, 부분 완료된 트랜잭션을 "recover"할 필요도 없음 *(p.32)*
- **cookie의 4가지 구성요소**: (1) HTTP response의 cookie header line, (2) 다음 HTTP request의 cookie header line, (3) 사용자 host에 브라우저가 관리하는 cookie file, (4) 웹사이트의 backend database *(p.33)*
- 동작: 사이트가 최초 방문 시 고유 ID(=cookie)를 발급하고 backend DB에 저장 → 이후 요청마다 그 cookie 값이 동봉되어 사이트가 사용자를 "식별" *(p.33~34)*
- 용도: authorization, 장바구니, 추천, 사용자 세션 상태(웹메일) 등 *(p.35)*
- **First-party cookie**: 사용자가 실제로 방문하기로 선택한 사이트가 발급 / **Third-party cookie**: 사용자가 방문을 선택하지 않은 사이트(광고업체 등)가 발급 — 여러 사이트에 걸친 사용자 행태 추적에 사용되며, 사용자에게 보이지 않을 수 있음(광고 없이 invisible link로도 가능) *(p.37~40)*
- 예: nytimes.com이 자체 쿠키(1634)를 발급하고, 페이지에 삽입된 AdX.com 광고 요청 시 AdX가 별도 third-party 쿠키(7493)를 발급 → 이후 socks.com 등 다른 AdX 광고가 있는 사이트를 방문해도 동일 AdX 쿠키(7493)가 전달되어, AdX가 사용자의 교차 사이트 방문 이력을 축적하고 타겟 광고(양말 광고)를 반환할 수 있게 됨 *(p.37~40)*
- Firefox/Safari는 기본적으로 third-party cookie 추적을 비활성화, Chrome도 2023년부터 비활성화 예정 *(p.41)*
- **GDPR과 쿠키**: 쿠키가 개인을 식별할 수 있으면 개인정보로 간주되어 GDPR 규제 대상이 되며, 사용자가 쿠키 허용 여부를 명시적으로 통제할 수 있어야 함 *(p.42)*

### Web Cache (Proxy Server) *(p.43~48)*
- 목적: origin server를 거치지 않고 client 요청을 만족시킴 — 브라우저가 cache를 가리키도록 설정 → object가 cache에 있으면 즉시 반환, 없으면 origin에서 가져와 캐싱 후 반환 *(p.43)*
- cache는 client에게는 server, origin에게는 client 역할을 겸함. origin server는 응답 헤더(`Cache-Control: max-age=<seconds>` 또는 `no-cache`)로 캐싱 가능 여부를 알림 *(p.44)*
- 이유: client 요청의 응답시간 단축(cache가 더 가까움), 기관 access link의 트래픽 감소, 인터넷 전반에 cache가 밀집해 "가난한" content provider도 효과적으로 콘텐츠 전달 가능 *(p.44)*
- **비교 예시**: access link 1.54Mbps, 평균 요청률 15/sec, object 100Kb인 상황에서 access link utilization이 .97까지 치솟아 **queueing delay가 분 단위**로 폭증 *(p.45)*. **Option 1**(링크를 100배 증설)은 비용이 크지만 효과적 *(p.46)*. **Option 2**(local web cache 설치)는 저렴하며, cache hit rate 0.4 가정 시 평균 end-end delay가 **~1.2초**로 더 빠른 링크보다도 낮아짐(그리고 더 저렴함) *(p.47~48)*

### Conditional GET *(p.49)*
- 목표: 브라우저가 이미 최신 버전을 캐시하고 있으면 object를 다시 보내지 않음 — 전송 지연/네트워크 자원 낭비 방지
- client: 요청에 `If-modified-since: <date>` 헤더로 캐시본의 날짜를 명시 → server: 그 날짜 이후 수정 안 됐으면 `HTTP/1.0 304 Not Modified`(데이터 없이) 응답, 수정됐으면 `200 OK`와 함께 데이터 반환

### HTTP/2, HTTP/3 *(p.50~54)*
- **HTTP 1.1**: 하나의 TCP connection 위에서 여러 GET을 pipelining — server는 **FCFS(선착순)**로 응답하는데, 작은 object가 큰 object 뒤에서 대기하는 **HOL(Head-of-Line) blocking**이 발생하고, loss 복구(재전송)가 전체 object 전송을 정체시킴 *(p.50)*
- **HTTP/2** [RFC 7540, 2015]: methods/status code/대부분의 헤더는 HTTP 1.1과 동일. **client가 지정한 우선순위**에 따라 전송 순서를 정함(FCFS 아님), 요청 없는 object를 서버가 **push**할 수 있음, object를 여러 **frame**으로 나눠 인터리빙 전송해 HOL blocking을 완화 *(p.51~53)*
- **HTTP/2→3**: HTTP/2도 단일 TCP connection이므로 packet loss 복구가 여전히 모든 object 전송을 정체시킴(그래서 브라우저는 여전히 병렬 TCP connection을 여러 개 열려는 유인이 있음), vanilla TCP 연결 자체엔 보안이 없음. **HTTP/3**은 **UDP 위에서** object별 error/congestion control(더 많은 pipelining)과 보안을 추가함 *(p.54)*

---

## 3. E-mail: SMTP, IMAP *(p.56~63)*

### E-mail의 3대 구성요소 *(p.56~57)*
- **user agent** ("mail reader", 예: Outlook, iPhone mail client) — 메시지 작성/편집/읽기, 송수신 메시지는 서버에 저장
- **mail server** — **mailbox**(수신 메시지 보관), **message queue**(발신 대기 메시지)
- **SMTP(Simple Mail Transfer Protocol)** — mail server 간에 이메일 메시지를 전송하는 프로토콜, client(발신 서버)~server(수신 서버) 구조

### SMTP RFC(5321) *(p.58~61)*
- **TCP**로 신뢰성 있게 전송, 포트 25, 발신 서버가 client 역할로 직접 수신 서버에 전송(direct transfer)
- 3단계: handshaking(greeting) → 메시지 전송 → 종료(closure)
- HTTP처럼 command/response 상호작용(명령은 ASCII, 응답은 status code+phrase)
- 예시 시나리오: Alice가 UA로 메시지 작성 → 자신의 mail server에 SMTP로 전송(message queue에 적재) → 그 서버가 Bob의 mail server와 TCP connection을 열어 SMTP client 역할로 전송 → Bob의 서버가 mailbox에 저장 → Bob이 UA로 읽음
- **SMTP observations**: HTTP는 client pull, SMTP는 **client push**. 둘 다 ASCII command/response와 status code를 가짐. HTTP는 각 object를 별도 response message로 캡슐화하지만, **SMTP는 여러 object를 하나의 multipart message로 전송**. SMTP는 persistent connection 사용, 메시지(헤더+본문)는 **7-bit ASCII**여야 하며, server는 **CRLF.CRLF**로 메시지 끝을 판단

### Mail Message Format *(p.62)*
- **SMTP**는 메시지를 주고받는 프로토콜(RFC 5321, HTTP를 RFC 7231이 정의하는 것과 유사), **RFC 2822**는 메시지 자체의 문법(HTML을 정의하는 것과 유사)을 정의
- header(To:/From:/Subject: 등, 본문 내에서 SMTP의 MAIL FROM/RCPT TO 커맨드와는 별개) + 빈 줄 + body(ASCII 문자만)

### Mail Access Protocol *(p.63)*
- SMTP는 수신자 서버까지의 **전달/저장**만 담당, 실제 **조회(retrieval)**는 별도의 mail access protocol이 필요
- **IMAP**(Internet Mail Access Protocol, RFC 3501): 메시지를 서버에 저장한 채로 조회·삭제·폴더 관리를 제공
- **HTTP**: gmail, Hotmail, Yahoo!Mail 등이 SMTP(발신) + IMAP 또는 POP(수신) 위에 web 기반 인터페이스를 제공

---

## 4. DNS (Domain Name System) *(p.65~80)*

### 개념 *(p.65~67)*
- IP address(32bit, 데이터그램 주소지정용)와 사람이 쓰는 "name"(예: cs.umass.edu) 사이를 매핑하는 문제
- **DNS**: 여러 name server의 계층으로 구현된 **distributed database**이자, 이름을 resolve하기 위해 host와 DNS server가 통신하는 **application-layer protocol** — 인터넷 핵심 기능이지만 application-layer protocol로 구현되어 있고, 복잡도가 네트워크 "edge"에 위치함
- **왜 중앙화하지 않는가**: single point of failure, 트래픽 양, 멀리 떨어진 중앙 DB, 유지보수 문제로 **확장 불가능(doesn't scale)** — Comcast만 해도 하루 6000억 건, Akamai는 하루 2.2조 건의 DNS 쿼리 처리

### 분산·계층적 데이터베이스 *(p.68~74)*
- 계층: **Root → Top-Level Domain(.com/.org/.edu 등) → Authoritative(각 조직 자체 서버)**
- Root name server는 전 세계 **13개의 논리적 서버**(각각 다중 복제, 미국에만 약 200대), ICANN이 root DNS domain을 관리, DNSSEC이 인증·메시지 무결성 등의 보안을 제공
- TLD server: .com/.net은 Network Solutions, .edu는 Educause가 authoritative registry로 관리
- Authoritative DNS server: 조직 자신의 named host에 대한 authoritative 매핑을 제공, 조직이 직접 또는 서비스 제공자를 통해 유지
- **local DNS server**: host가 DNS query를 보내는 곳. ISP마다 있으며 계층에 엄밀히 속하지는 않음(recent 매핑을 로컬 캐시에서 답하거나, 계층으로 요청을 전달)
- **Iterated query**: 접촉한 서버가 "나는 모르지만 이 서버에 물어봐"라며 다음 서버 이름으로 응답 / **Recursive query**: name resolution의 부담을 접촉된 name server 쪽에 지움(상위 계층에 부하 집중)

### 캐싱과 Resource Record *(p.75~76)*
- 한 번 매핑을 학습한 name server는 **caching**해서 이후 쿼리에 즉시 응답 — 응답시간 개선, cache entry는 TTL 후 만료, TLD server는 보통 local name server에 캐싱됨. cache된 정보가 out-of-date일 수 있어 DNS는 **best-effort** 이름-주소 변환
- DNS는 Resource Record(RR)를 저장하는 distributed database — RR format: `(name, value, type, ttl)`
  - **type=A**: name=hostname, value=IP address
  - **type=NS**: name=domain, value=그 domain의 authoritative name server hostname
  - **type=CNAME**: name=alias, value=canonical(real) name — 예: www.ibm.com이 실제로는 servereast.backup2.ibm.com
  - **type=MX**: value=name에 대응하는 SMTP mail server 이름

### DNS 프로토콜 메시지와 등록 *(p.77~80)*
- query/reply 모두 같은 포맷: header(identification 16bit, flags: query/reply·recursion desired·recursion available·reply is authoritative, # questions/answer/authority/additional RRs) + questions + answers + authority + additional info 섹션
- 새 도메인 등록 예(Network Utopia): DNS registrar(예: Network Solutions)에 `networkuptopia.com` 등록, authoritative name server의 이름·IP(주/보조) 제공 → registrar가 `.com` TLD server에 NS·A record를 삽입 → 로컬에 authoritative server를 만들고 `www.networkuptopia.com`용 A record, `networkuptopia.com`용 MX record를 등록
- **DNS 보안**: DDoS 공격(root/TLD server에 트래픽 폭주 — root 대상은 아직 성공한 적 없음, traffic filtering과 local DNS server의 TLD IP 캐싱이 root bypass를 가능케 함; TLD 대상은 잠재적으로 더 위험), **spoofing 공격**(DNS query를 가로채 가짜 응답 반환 — DNS cache poisoning, 대응으로 RFC 4033 DNSSEC 인증 서비스)

---

## 5. P2P 파일 공유: BitTorrent *(p.82~90)*

### File Distribution: Client-Server vs P2P *(p.83~86)*
- 표기: `u_s`=서버 업로드 용량, `d_i`/`u_i`=peer i의 다운로드/업로드 용량, F=파일 크기, N=peer 수
- **Client-server**: 서버가 N개 복사본을 순차 업로드해야 함(`NF/u_s`), 각 client는 `F/d_min` 시간 다운로드 → `D_c-s ≥ max{NF/u_s, F/d_min}` — **N에 비례해 선형 증가** *(p.84)*
- **P2P**: 서버는 최소 1개 복사본만 업로드하면 됨(`F/u_s`), 전체 client가 합쳐서 `NF` bit를 받아야 하는데 이때 가용 최대 업로드율은 `u_s + Σu_i`(각 peer가 서비스 용량을 함께 제공) → `D_P2P ≥ max{F/u_s, F/d_min, NF/(u_s+Σu_i)}` — 분모도 N에 비례해 커지므로 **client-server보다 훨씬 완만하게 증가** *(p.85~86)*

### BitTorrent 동작 *(p.87~90)*
- 파일을 **256Kb chunk**로 분할, **torrent**(파일 chunk를 교환하는 peer 그룹) 내에서 peer들이 chunk를 주고받음, **tracker**가 torrent 참여 peer 목록을 관리 *(p.87)*
- 새로 참여하는 peer는 chunk가 하나도 없는 상태로 시작해 다른 peer로부터 점차 축적, tracker에 등록해 peer 목록을 얻고 일부와 연결("neighbor"). 다운로드 중에도 다른 peer에 업로드, 교환 상대는 수시로 바뀔 수 있음("churn"). 파일을 다 받으면 (이기적으로)torrent를 떠나거나 (이타적으로)남아있을 수 있음 *(p.88)*
- **Requesting chunks**: peer마다 갖고 있는 chunk 부분집합이 다름 — Alice는 주기적으로 각 peer가 가진 chunk 목록을 물어보고, 가장 희귀한(rarest) chunk부터 요청 *(p.89)*
- **Sending chunks (tit-for-tat)**: Alice는 자신에게 **가장 빠른 속도로** chunk를 보내주는 상위 4개 peer에게만 chunk를 보냄(나머지는 choked됨), 10초마다 top 4를 재평가. 30초마다 무작위로 다른 peer 하나를 골라 "optimistically unchoke"하며 전송을 시작 — 이 peer가 top 4에 새로 들어올 수도 있음 *(p.89~90)*
- **상호 관계 형성**: Alice가 Bob을 optimistically unchoke → Alice가 Bob의 top-4 provider가 되어 Bob도 화답(reciprocate) → Bob이 Alice의 top-4 provider가 됨. **업로드율이 높을수록 더 나은 거래 상대를 찾아 파일을 더 빨리 받게 됨** *(p.90)*

---

## 6. Video Streaming과 CDN *(p.92~105)*

### 맥락 *(p.92)*
- 스트리밍 비디오 트래픽은 인터넷 대역폭의 최대 소비자 — Netflix/YouTube/Amazon Prime이 2020년 기준 residential ISP 트래픽의 80%
- 과제: **scale**(~10억 사용자에 도달), **heterogeneity**(유선 vs 모바일, 대역폭 풍부/빈약한 사용자 등 제각각의 능력)
- 해법: **distributed, application-level infrastructure**

### 비디오 인코딩 *(p.93~94)*
- video = 일정 rate로 표시되는 이미지 시퀀스(예: 24 images/sec), 각 이미지는 pixel 배열로 표현
- coding: 이미지 **내부(spatial, 예: 반복되는 픽셀 값을 색상값+반복횟수로 압축)** 및 **이미지 간(temporal, 예: 다음 프레임 전체 대신 이전 프레임과의 차이만 전송)** 중복을 이용해 비트 수를 줄임
- **CBR**(constant bit rate, 인코딩 속도 고정) vs **VBR**(variable bit rate, spatial/temporal coding 양에 따라 속도 변화) — 예: MPEG1(CD-ROM) 1.5Mbps, MPEG2(DVD) 3~6Mbps, MPEG4(인터넷에서 흔히 사용, 64Kbps~12Mbps)

### Streaming Stored Video *(p.95~98)*
- 기본 시나리오: video server(저장된 비디오) → Internet → client. 과제: server-client 대역폭이 (댁내/access/core/서버 등의) 혼잡도에 따라 시간에 따라 변함, packet loss/delay가 playout을 지연시키거나 품질을 저하시킴 *(p.95)*
- streaming: client가 초반부를 재생하는 동안 server는 여전히 후반부를 전송 중인 상태(cumulative data 그래프의 시차) *(p.96)*
- **continuous playout constraint**: 재생 타이밍이 원본 타이밍과 일치해야 하지만, 네트워크 지연은 변동(jitter)이 있으므로 이를 흡수할 **client-side buffer**가 필요 — 그 외 pause/fast-forward/rewind 같은 상호작용, 패킷 손실·재전송도 과제 *(p.97)*
- **playout buffering**: client-side buffering과 playout delay로 네트워크 지연·jitter를 보정 *(p.98)*

### DASH (Dynamic, Adaptive Streaming over HTTP) *(p.99~100)*
- **server**: 비디오 파일을 여러 chunk로 나누고, 각 chunk를 여러 rate로 인코딩해 서로 다른 파일로 저장, CDN 노드들에 복제, **manifest file**로 chunk별 URL을 제공
- **client**: server-client 대역폭을 주기적으로 추정 → manifest를 참고해 한 번에 한 chunk씩, 현재 대역폭에서 지속 가능한 **최대 인코딩 rate**를 골라 요청(시점·서버에 따라 다른 rate 선택 가능)
- client의 "지능": (buffer starvation/overflow가 없도록) **언제** chunk를 요청할지, **어떤 인코딩 rate**를 요청할지, **어디서**(가깝거나 대역폭 여유 있는 서버) 요청할지를 스스로 결정
- Streaming video = encoding + DASH + playout buffering

### Content Distribution Networks (CDN) *(p.101~105)*
- 과제: 수백만 개 비디오 중에서 선택된 콘텐츠를 수십만 동시 사용자에게 어떻게 스트리밍할까
- **Option 1**(단일 거대 "mega-server")은 single point of failure, 혼잡 지점, 먼 client까지의 길고 혼잡할 수 있는 경로 문제로 **확장 불가능** *(p.101)*
- **Option 2 — CDN**: 지리적으로 분산된 여러 사이트에 비디오 복사본을 저장/서빙
  - **enter deep**: CDN 서버를 많은 access network 깊숙이 배치(사용자와 가까움) — 예: Akamai는 120개국 이상 24만 대 서버 배치(2015 기준, 현재는 4200+곳·135개국) *(p.102~103)*
  - **bring home**: access network 근처 POP(Point of Presence)에 상대적으로 적은 수(수십 개)의 큰 클러스터를 둠 — Limelight가 사용 *(p.102)*
- **Netflix 동작 예**: 콘텐츠(예: MADMEN) 복사본을 전 세계 OpenConnect CDN 노드에 저장 → 구독자가 콘텐츠 요청 → 서비스 제공자가 manifest 반환 → client가 manifest로 지원 가능한 최고 rate로 콘텐츠 조회, 경로가 혼잡하면 다른 rate/복사본 선택 가능 *(p.104)*
- **OTT("Over The Top")**: 인터넷 host-host 통신을 서비스로 이용해 콘텐츠를 전달하는 방식 — 과제는 혼잡한 인터넷 "edge"에 대응하는 것: 어떤 콘텐츠를 어느 CDN 노드에 둘지, 어느 CDN 노드에서 어떤 rate로 콘텐츠를 가져올지 *(p.105)*

---

## 7. Socket Programming *(p.106~127)*

### 개요 *(p.107~108)*
- 목표: socket을 이용해 통신하는 client/server application을 만드는 법을 배움. **socket**: application process와 종단간(end-to-end) transport protocol 사이의 문
- 두 가지 socket 유형: **UDP**(unreliable datagram) / **TCP**(reliable, byte stream-oriented)
- 예제 애플리케이션: (1) client가 키보드에서 한 줄을 읽어 서버로 전송 → (2) 서버가 받아서 대문자로 변환 → (3) 서버가 수정된 데이터를 client로 전송 → (4) client가 수정된 데이터를 받아 화면에 표시

### Socket Programming with UDP *(p.109~118)*
- UDP는 client-server 간 "connection"이 없음: 데이터 전송 전 handshaking 없음, sender가 각 패킷에 목적지 IP·port를 명시적으로 붙임, receiver는 받은 패킷에서 sender의 IP·port를 추출. **전송 데이터는 손실되거나 순서가 바뀔 수 있음** — application 입장에서 UDP는 client-server 프로세스 간 바이트 그룹("datagram")의 **비신뢰적** 전송을 제공 *(p.109)*
- Client/server socket 상호작용 흐름: server가 `DatagramSocket()`으로 소켓 생성(port=x) → client도 `DatagramSocket()` 생성 → client가 server IP·port로 datagram을 만들어 전송 → server가 읽고 응답을 write(클라이언트 주소·포트 명시) → client가 읽고 소켓을 닫음 *(p.113)*
- Java 예제 구조: 키보드 입력을 위한 `input stream`, 패킷 송신용 `sendPacket`, 수신용 `receivePacket`이 client UDP socket을 통해 네트워크와 주고받음 *(p.114)*
- **UDPClient**: `BufferedReader`로 입력 스트림 생성 → `DatagramSocket clientSocket = new DatagramSocket()`로 client socket 생성 → `InetAddress.getByName("hostname")`로 **DNS를 이용해** hostname을 IP로 변환 → 문자열을 바이트 배열로 변환 *(p.115)*, `DatagramPacket`(전송할 데이터+길이+IP주소+port 9876)을 만들어 `clientSocket.send()`로 전송, `clientSocket.receive()`로 응답 datagram을 읽고 문자열로 변환해 출력 후 소켓 닫음 *(p.116)*
- **UDPServer**: `DatagramSocket serverSocket = new DatagramSocket(9876)`로 포트 9876에 소켓 생성 → `while(true)` 루프 안에서 수신용 `DatagramPacket` 공간을 만들고 `serverSocket.receive()`로 대기·수신 *(p.117)* → 받은 데이터에서 sender의 IP·port를 추출(`getAddress()`, `getPort()`) → 대문자로 변환 → 그 IP·port로 향하는 `DatagramPacket`을 만들어 `serverSocket.send()`로 응답 후, 루프백해서 다음 datagram을 대기 *(p.118)*

### Socket Programming with TCP *(p.119~127)*
- **Client가 server에 접속**: server process가 먼저 실행 중이어야 하고, client의 접속을 받아들일 socket(문)을 만들어두어야 함. Client는 IP·port를 지정해 TCP socket을 생성하면, **client TCP가 server TCP와 connection을 수립**함 *(p.119)*
- **server 쪽**: client에게 접속받으면 **server TCP가 그 client 전용 새 socket을 생성**해, 여러 client와 동시에 통신 가능하게 함(client source port·IP로 각 client를 구분) *(p.119)*
- application 관점에서 TCP는 client-server process 간 신뢰성 있는 순서 보장 byte-stream 전송("pipe")을 제공 *(p.119)*
- **welcoming socket**과 **connection socket** 구조: client socket이 3-way handshake로 server의 welcoming socket에 접속하면, 그 결과로 양쪽에 실제 데이터가 오가는 socket이 만들어짐(server 쪽은 별도의 connection socket) *(p.120)*
- **Client/server socket 상호작용(TCP)**: server가 `ServerSocket()`(port=x)으로 welcomeSocket 생성 → `welcomeSocket.accept()`로 접속 요청을 대기 → client가 `Socket()`으로 hostid:x에 접속(TCP connection setup, 3-way handshake) → client가 요청 전송 → server가 connectionSocket에서 요청을 읽고 응답을 write → 양쪽이 각자 소켓을 close *(p.121)*
- **Stream 용어**: **stream**은 process를 드나드는 문자의 시퀀스. **input stream**은 키보드나 socket 같은 입력원에, **output stream**은 모니터나 socket 같은 출력원에 연결됨 *(p.122)*
- 예제 앱 흐름: (1) client가 표준입력(`inFromUser`)에서 줄을 읽어 소켓(`outToServer`)으로 서버에 전송 → (2) 서버가 소켓에서 줄을 읽음 → (3) 서버가 대문자로 변환해 되돌려보냄 → (4) client가 소켓(`inFromServer`)에서 수정된 줄을 읽어 출력 *(p.123)*
- **TCPClient**: 입력 스트림 생성(`BufferedReader inFromUser`) → `Socket clientSocket = new Socket("hostname", 6789)`로 client socket 생성 및 서버 접속 → `DataOutputStream outToServer`로 소켓에 연결된 출력 스트림 생성 *(p.124)* → `BufferedReader inFromServer`로 소켓에 연결된 입력 스트림 생성 → 사용자 입력 줄을 읽어 `outToServer.writeBytes()`로 전송 → `inFromServer.readLine()`으로 서버 응답을 읽어 출력, `clientSocket.close()` *(p.125)*
- **TCPServer**: `ServerSocket welcomeSocket = new ServerSocket(6789)`로 포트 6789에 welcoming socket 생성 → `while(true)` 루프에서 `welcomeSocket.accept()`로 client 접속을 대기(반환된 것이 connectionSocket) → 그 소켓에 연결된 입력 스트림(`inFromClient`) 생성 *(p.126)* → 출력 스트림(`outToClient`) 생성 → `inFromClient.readLine()`으로 client 문장을 읽고 대문자로 변환 → `outToClient.writeBytes()`로 되돌려보낸 뒤, 루프백해서 다음 client 접속을 대기 *(p.127)*

---

## 핵심 요약 *(p.131~132)*

- **Application architecture**: client-server vs P2P
- **Application service 요구사항**: reliability, bandwidth, delay
- **Internet transport service model**: connection-oriented·reliable(TCP) vs unreliable·datagram(UDP)
- **구체적 프로토콜**: HTTP(request/response, persistent/non-persistent, cookie, 캐싱, HTTP/2·3), SMTP/IMAP(client push, 7-bit ASCII), DNS(분산 계층 DB), P2P(BitTorrent, tit-for-tat)
- **Video streaming과 CDN**: DASH(client가 rate/시점/서버를 스스로 결정), CDN의 enter-deep vs bring-home 배치 전략
- **Socket programming**: UDP(비신뢰적 datagram) vs TCP(신뢰적 byte stream, welcoming/connection socket 구조)
- **가장 중요한 것은 프로토콜 자체**: 전형적인 request/reply 메시지 교환(클라이언트 요청 → 서버가 데이터+status code로 응답), 메시지 형식(header: 데이터에 대한 정보 필드 / data: 실제 전달되는 payload)
- **중요한 테마들**: centralized vs decentralized, stateless vs stateful, scalability, reliable vs unreliable message transfer, "complexity at network edge"
