# Chapter 17-1: Amortized Analysis (Aggregate analysis)

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*Slides from Heejin Park, Hanyang Univ. / 파일: `17_Amortized Analysis_1.pdf`*

## 0. 개요 *(슬라이드 p.2)*
- Contents: **Aggregate analysis**, Accounting method, Potential method, Dynamic Table
- 이 PDF(1편)는 **Aggregate analysis**만 다룬다. 예시는 stack operation과 incrementing binary counter 두 개.

## 1. Aggregate analysis 정의 *(p.3)*
- n개 연산의 sequence가 **worst-case** 총 시간 `T(n)`이 걸린다.
- 연산 하나당 평균 비용은 worst case에서 `T(n)/n` = **amortized cost**
- amortized cost는 **모든 연산에 똑같이** 적용된다.
  - sequence 안에 연산 종류가 여러 개여도 마찬가지

## 2. 예시 1: Stack operation *(p.4~8)*

### 연산 정의 *(p.4)*
- `PUSH(S, x)`, `POP(S)`, `MULTIPOP(S, k)`
- PUSH, POP은 `O(1)` → 각각 비용 1
- n개 연산(PUSH/POP만)의 실제 실행 시간은 `Θ(n)`, 총 비용 n

### MULTIPOP *(p.5~6)*
```
MULTIPOP(S, k)
1  while not STACK-EMPTY(S) and k > 0
2      POP(S)          ← T(1) * k
3      k = k - 1
```
- 실제 실행 시간은 **실제로 실행된 POP 횟수에 선형**
- 따라서 MULTIPOP(S, k)의 비용은 `O(k)`
- stack 위에서 k개를 제거한다. stack의 원소가 k개보다 적으면 있는 것을 전부 제거해서 stack이 빈다.
- 슬라이드 예시: 6칸 stack이 가득 찬 상태 → MULTIPOP(S, 2) 후 top이 index 4 → MULTIPOP(S, 6) 후 empty

### 직관적 분석 (틀린 방식 = 느슨한 bound) *(p.7)*
- 빈 stack에서 시작해 PUSH, POP, MULTIPOP n개 sequence를 분석
- MULTIPOP 한 번의 worst-case: `O(n)`, stack 크기는 최대 n
- → 총 비용 `O(n²)`. **이 bound는 tight하지 않다.**

### Aggregate analysis 적용 *(p.8)*
- sequence 전체에 대해 더 좋은 upper bound를 얻을 수 있다.
- 예: `[push, push, pop, push, push, push, multipop(2), …]` = `[push, push, pop, push, push, push, {pop, pop}, …]` (multipop을 pop들로 풀어 씀)
- `n ≥ #(push) ≥ #(pop)`
- `2n ≥ #(push) + #(pop)`
- → 총 비용 `O(n)`, **amortized cost = O(n)/n = O(1)**

## 3. 예시 2: Incrementing binary counter *(p.9~18)*

### 설정 *(p.9)*
- 0부터 위로 세는 **k-bit binary counter**를 구현
- 비트 배열 `A[0..k-1]` 사용 (`A[0]`이 최하위 비트, `A[k-1]`이 최상위)

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
- INCREMENT의 비용은 **bit flip 횟수에 비례**

### 동작 예시 (k=5, A[4]~A[0]) *(p.11~14)*

| Counter value | A[4] A[3] A[2] A[1] A[0] | cost | Total cost |
|---|---|---|---|
| 0 | 0 0 0 0 0 | 0 | 0 |
| 1 | 0 0 0 0 1 | 1 | 1 |
| 2 | 0 0 0 1 0 | 2 | 3 |
| 3 | 0 0 0 1 1 | 1 | 4 |
| 4 | 0 0 1 0 0 | 3 | 7 |

### 느슨한 분석 *(p.15)*
- INCREMENT 한 번의 worst case는 `Θ(k)`: 배열이 전부 1일 때 (`11…1` → `00…0`, cost k)
- 따라서 빈(0) counter에서 n번 INCREMENT하는 sequence는 worst case `O(nk)`

### Aggregate analysis로 조이기 *(p.16~17)*
- **매번 모든 비트가 뒤집히는 것은 아니라는 점**을 관찰하면 n번 INCREMENT의 worst-case를 `O(n)`으로 조일 수 있다.
- 비트별 flip 횟수 (n번 INCREMENT 동안):
  - `A[0]`: 매번 flip → **n**번
  - `A[1]`: 두 번에 한 번 → **n/2**번
  - `A[2]`: 네 번에 한 번 → **n/4**번
  - `A[3]`: **n/8**번 (슬라이드 예시 1~8 표에서 확인)
- 총 flip 수: `Σ_{i=0}^{k-1} ⌊n/2^i⌋ < Σ_{i=0}^{∞} n/2^i = 2n`
- → 총 비용 `O(n)`, **amortized cost = O(n)/n = O(1)**

### 요약 *(p.18)*
- Running time: 총 `O(n)`
- Amortized cost: `O(n)/n = O(1)`

---

## 수업에서 다룬 섹션
1. Aggregate analysis 정의 (p.3)
2. 예시 1: Stack operation — PUSH/POP/MULTIPOP, 느슨한 O(n²) 분석 vs aggregate 분석 O(n) (p.4~8)
3. 예시 2: Incrementing binary counter — INCREMENT, 느슨한 O(nk) 분석 vs 비트별 flip 횟수 분석 O(n) (p.9~18)
