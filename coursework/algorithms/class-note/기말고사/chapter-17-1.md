# Chapter 17-1 수업노트: Amortized Analysis (Aggregate analysis)

*정리 노트: `notes/기말고사/chapter-17-1.md` / 수업일: 2026-11-23*

## 1. Aggregate analysis 정의 *(p.3)*

**Aggregate analysis**: 연산 n개짜리 sequence 전체의 worst-case 총 시간 T(n)을 구한 뒤, 그걸 n으로 나눈 T(n)/n을 연산 하나당 비용(**amortized cost**)으로 보는 분석 방법.

- "평균"이라고 해도 확률 평균이 아니다. 입력이 최악이어도 **sequence 전체**를 놓고 나눈 값이라서 worst-case 보장이 유지된다.
- sequence 안에 연산 종류가 섞여 있어도 모든 연산에 **같은 amortized cost**를 매긴다. (accounting/potential method는 연산마다 다르게 매길 수 있다.)

### tight의 의미
- **tight한 upper bound**: 실제 worst case가 그 bound에 (상수배 안에서) 실제로 도달할 수 있는 상한.
- 도달하지 못하면 틀린 건 아니지만 **느슨한(loose) 상한**이다.
- 예: "이 함수는 O(n²)이다"는 실제로 n에 비례하는 시간만 걸려도 참이지만 tight하지 않다.

## 2. 예시 1: Stack operation *(p.4~8)*

### 연산 *(p.4~6)*
- `PUSH(S, x)`: 원소 x를 올림, O(1)
- `POP(S)`: top 제거, O(1)
- `MULTIPOP(S, k)`: top에서 k개 제거. stack에 k개보다 적으면 있는 만큼만 제거해서 비워버림.

```
MULTIPOP(S, k)
1  while not STACK-EMPTY(S) and k > 0
2      POP(S)
3      k = k - 1
```
- while이 한 바퀴 돌 때마다 POP이 1번 → 비용은 O(k) (정확히는 `min(k, stack 크기)`).
- 슬라이드 예시: 6칸 stack이 가득 참 → MULTIPOP(S, 2) 후 top이 index 4 → MULTIPOP(S, 6) 후 empty

### 느슨한 분석 *(p.7)*
- 빈 stack에서 PUSH/POP/MULTIPOP n개를 실행.
- MULTIPOP 하나의 worst case는 O(n) (stack이 최대 n개까지 쌓일 수 있음), 연산이 n개 → 총 O(n·n) = **O(n²)**
- 이 bound는 **tight하지 않다.**

### 왜 tight하지 않은가 (수업 중 Q&A)
- MULTIPOP이 O(n)을 쓰려면 stack에 원소가 Θ(n)개 있어야 하고, 그러려면 PUSH가 Θ(n)번 먼저 필요하다. 그 MULTIPOP이 끝나면 stack은 빈다.
- 연산이 총 n개뿐이라는 게 핵심: n−1번 PUSH하고 MULTIPOP으로 다 빼는 게 큰 MULTIPOP의 최대 경우이고, MULTIPOP 여러 개가 각각 O(n)일 수는 없다. 다 합쳐도 O(n)을 넘지 않는 구조.
- MULTIPOP 하나가 O(n)인 건 원래 맞다. 새로 알게 된 것은 **"전부 합쳐도 O(n)"**.

### Aggregate analysis 적용 *(p.8)*
- 예: `[push, push, pop, push, push, push, multipop(2), …]` = `[push, push, pop, push, push, push, {pop, pop}, …]` (multipop을 pop들로 풀어 씀)
- 원소는 PUSH로 들어간 만큼만 나올 수 있다 (MULTIPOP도 결국 POP 여러 번).
- `n ≥ #(push) ≥ #(pop)`
- `2n ≥ #(push) + #(pop)`
- → 총 비용 `O(n)`, **amortized cost = O(n)/n = O(1)**. MULTIPOP 한 번이 비싸 보여도 연산당 평균은 상수.

### 확인 문제
sequence: `push, push, push, pop, push, multipop(5), push`

| 연산 | 연산 후 stack 크기 | 실제 비용 |
|---|---|---|
| push | 1 | 1 |
| push | 2 | 1 |
| push | 3 | 1 |
| pop | 2 | 1 |
| push | 3 | 1 |
| multipop(5) | 0 | 3 |
| push | 1 | 1 |

- 총 비용 **9**, #(push)=5, #(pop)=4 (pop 1 + multipop 안의 pop 3) → 합 9 = 총 비용. 2n = 14 이하.
- **함정**: MULTIPOP의 실제 비용은 k가 아니라 **실제로 POP된 횟수** = `min(k, stack 크기)`. 위에서 multipop(5)의 비용은 5가 아니라 3. `O(k)`는 상한일 뿐이고, `#(pop) ≤ #(push)` 논증도 이 성질에 기댄다.

## 3. 예시 2: Incrementing binary counter *(p.9~18)*

### 설정 *(p.9)*
- 0부터 위로 세는 **k-bit binary counter**. 비트 배열 `A[0..k-1]`, `A[0]`이 최하위 비트.

### INCREMENT *(p.10)*
```
INCREMENT(A)
1  i = 0
2  while i < A.length and A[i] == 1
3      A[i] = 0        ← bit flip, T(1)
4      i = i + 1
5  if i < A.length
6      A[i] = 1        ← bit flip, T(1)
```
- 비용은 **bit가 뒤집힌 횟수**에 비례.

### 동작 예시 (k=5) *(p.11~14)*

| value | A[4] A[3] A[2] A[1] A[0] | cost | total |
|---|---|---|---|
| 0 | 0 0 0 0 0 | 0 | 0 |
| 1 | 0 0 0 0 1 | 1 | 1 |
| 2 | 0 0 0 1 0 | 2 | 3 |
| 3 | 0 0 0 1 1 | 1 | 4 |
| 4 | 0 0 1 0 0 | 3 | 7 |

수업 중 직접 이어서 채운 부분 (value 5~8):

| value | A[3] A[2] A[1] A[0] | cost | total |
|---|---|---|---|
| 5 | 0 1 0 1 | 1 | 8 |
| 6 | 0 1 1 0 | 2 | 10 |
| 7 | 0 1 1 1 | 1 | 11 |
| 8 | 1 0 0 0 | 4 | 15 |

- n=8에서 총 비용 15 = 2·8 − 1 (≤ 2n). 단, 이건 n=8 한 점일 뿐이라 일반 n에 대한 근거가 따로 필요.

### 느슨한 분석 *(p.15)*
- INCREMENT 하나의 worst case는 `Θ(k)`: 배열이 전부 1일 때 (`11…1` → `00…0`, cost k)
- 빈 counter에서 n번 INCREMENT하면 worst case `O(nk)`. 이것도 tight하지 않다.

### Aggregate analysis로 조이기 *(p.16~17)*
- **매번 모든 비트가 뒤집히는 것은 아니라는 점**을 관찰하면 n번 INCREMENT의 worst-case를 `O(n)`으로 조일 수 있다.
- 행(연산)이 아니라 **열(비트)별로** flip 횟수를 센다. n번 INCREMENT 동안:
  - `A[0]`: n번 (매번)
  - `A[1]`: n/2번
  - `A[2]`: n/4번
  - `A[3]`: n/8번
  - 1~8 구간 확인: A[0] 8번, A[1] 4번, A[2] 2번, A[3] 1번 → 합 15 (표의 총 비용과 일치)
- 일반화: `A[i]`는 **2^i번에 한 번** 뒤집히므로 n번 동안 `⌊n/2^i⌋`번.
- 총 flip 수: `Σ_{i=0}^{k-1} ⌊n/2^i⌋ < Σ_{i=0}^{∞} n/2^i = 2n`
  - 비트가 k개뿐이라 항은 유한하고, 무한 등비급수 `n(1 + 1/2 + 1/4 + …) = 2n`을 **상한으로** 쓴 것.
  - 바닥 함수 때문에 실제 값은 2n보다 조금 작다 (n=8에서 15).
- → 총 비용 `O(n)`, **amortized cost = O(n)/n = O(1)**. k가 얼마든 상관없다.

### 왜 2^i번에 한 번인가 (수업 중 Q&A)
- `A[2]`는 INCREMENT 직전에 하위 비트 `A[1]A[0]`이 `11`일 때(carry가 올라올 때) 뒤집힌다.
- 하위 2비트가 `11`이 되는 건 4번에 한 번 (값 3, 7, 11, …에서 증가할 때) → n번의 INCREMENT 중 n/4번.
- 일반화: `A[i]`는 하위 i비트가 전부 1일 때 뒤집히므로 2^i번에 한 번.

### 요약 *(p.18)*
- Running time: 총 `O(n)`
- Amortized cost: `O(n)/n = O(1)`
- stack과 같은 구조: 어떤 연산 하나가 비싸도(INCREMENT가 k개를 뒤집음) **비싼 연산은 드물게만** 일어나고 그 전에 싼 연산들이 쌓여 있다.
