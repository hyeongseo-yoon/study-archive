# Chapter 17-2: Amortized Analysis (Accounting method, Potential method)

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Slides from Heejin Park, Hanyang Univ. / 파일: `17_Amortized Analysis2.pdf` (슬라이드 p.20~57)*

## 0. 개요 *(슬라이드 p.41)*
- Contents: Aggregate analysis(17-1), **Accounting method**, **Potential method**, Dynamic Table(별도 PDF)
- 이 PDF(2편)는 Accounting method와 Potential method를 다룬다. 예시는 둘 다 stack operation과 incrementing binary counter.

## 1. Accounting method *(p.20~40)*

### 정의 *(p.20)*
- 연산마다 **다른 금액(charge)** 을 매긴다. 어떤 연산은 실제 비용보다 더 많이, 어떤 연산은 더 적게 charge한다.
- **Amortized cost**: charge한 금액
- **Credit**: 실제 비용과 charge의 차이를 자료구조 안의 **특정 객체**에 배정해 둔 것. 실제 비용이 amortized cost보다 큰 나중 연산의 비용을 대신 낸다.

### 조건 *(p.21)*
- `c_i`: i번째 연산의 actual cost, `ĉ_i`: i번째 연산의 amortized cost
- n개 연산의 모든 sequence에 대해 `Σ ĉ_i ≥ Σ c_i`
- 자료구조에 저장된 총 credit = `Σ ĉ_i − Σ c_i` (항상 음수가 아니어야 한다)

### 예시 1: Stack operation *(p.22~29)*
- Actual cost: PUSH 1, POP 1, MULTIPOP `min(k, s)`
- Amortized cost: **PUSH 2, POP 0, MULTIPOP 0**

| 연산 | 처리 | 슬라이드 |
|---|---|---|
| PUSH | actual cost 1 + 미리 낸 credit 1 → amortized cost = actual + credit = 2. 쌓인 원소 위에 credit 1이 붙는다 | p.24~26, 28 |
| POP / MULTIPOP | 원소마다 붙어 있는 credit 1을 써서 지불 → amortized cost = actual − credit = 0 | p.27 |

- 슬라이드 그림: index 1~4짜리 stack에 PUSH를 할 때마다 해당 칸 아래 credit 1이 생기고(p.24~26), POP하면 그 칸의 credit이 사라진다(p.27, credit 0).
- POP, MULTIPOP은 반드시 PUSH 이후에만 실행된다 → PUSH를 조금 더 charge(= credit)해 두면 POP/MULTIPOP의 실제 비용을 credit이 낸다 *(p.29)*
- **credit은 항상 음수가 아니다**: stack의 원소 수가 음수일 수 없기 때문. 따라서 총 amortized cost는 총 actual cost의 upper bound.
- Total amortized cost: `O(n)`, Total actual cost: `O(n)`

### 예시 2: Incrementing binary counter *(p.30~39)*
- Actual cost: bit set(0→1) 1, bit reset(1→0) 1
- Amortized cost: **bit set 2, bit reset 0** *(p.30)*
- 슬라이드 예시 (A[3]~A[0], 0001부터 증가) *(p.31~38)*:
  - 0001 → 0010: A[0] reset(cost 1), A[1] set(cost 1) → credit이 A[1]에 1 *(p.31~33)*
  - 0010 → 0011: A[0] set → credit이 A[0], A[1]에 1씩 *(p.34)*
  - 0011 → 0100: A[0], A[1] reset(credit으로 지불) → A[2] set → credit이 A[2]에 1 *(p.35~37)*
  - 0100 → 0101: A[0] set → credit이 A[0], A[2]에 1씩 *(p.38)*
  - 즉 **1인 비트마다 credit 1**이 붙어 있다.
- bit reset은 항상 bit set 이후에만 일어난다 → set할 때 credit을 미리 charge해 두면 reset의 실제 비용을 credit이 낸다 *(p.39)*
- **credit은 항상 음수가 아니다**: counter 안의 1의 개수는 음수가 될 수 없기 때문. 총 amortized cost는 총 actual cost의 upper bound.
- Total amortized cost: `O(n)`, Total actual cost: `O(n)`

### 요약 *(p.40)*
- Amortized cost: 총 `O(n)`
- Running time: 총 `O(n)`

## 2. Potential method *(p.42~57)*

### 정의 *(p.42~46)*
- Accounting method와 비슷하지만 **credit → "potential energy"(potential)** 로 부른다.
- potential을 자료구조 안의 특정 객체가 아니라 **자료구조 전체**에 연결한다.
- 슬라이드 그림 (binary counter): accounting의 credit은 비트별로 붙어 있었는데(p.43~46의 `credit` 줄), potential은 **counter 전체에 하나의 값**으로 본다. 예: 0001 → potential 1, 0010 → 1, 0011 → 2.

### 형식화 *(p.47)*
- n개 연산을 수행한다.
- `D_0`: 초기 자료구조
- `D_i`: i번째 연산을 `D_{i-1}`에 적용한 결과 자료구조
- `Φ(D_i)`: `D_i`에 연결된 potential
- Potential difference `Φ(D_i) − Φ(D_{i-1})`
  - **양수**: 자료구조의 potential이 증가 (credit 저축)
  - **음수**: potential 감소분이 연산의 actual cost를 지불

### Amortized cost 정의 *(p.48)*
- `ĉ_i = c_i + Φ(D_i) − Φ(D_{i-1})`
- n개 연산의 총 amortized cost (telescoping):
  - `Σ ĉ_i = Σ (c_i + Φ(D_i) − Φ(D_{i-1})) = Σ c_i + Φ(D_n) − Φ(D_0)`
- 모든 i에 대해 `Φ(D_i) ≥ Φ(D_0)`를 요구한다.
  - 그러면 모든 `1 ≤ k ≤ n`에 대해 `Σ ĉ_i ≥ Σ c_i`

### 예시 1: Stack operation *(p.49~52)*
- Potential function `Φ` = **stack에 들어 있는 객체 수**
- `Φ(D_0) = 0` (빈 stack에서 시작), 모든 i에 `Φ(D_i) ≥ 0 = Φ(D_0)` *(p.49)*
- 연산별 amortized cost *(p.50~51)*, s개 원소가 든 stack에서 i번째 연산:

| 연산 | Φ 차이 | amortized cost |
|---|---|---|
| PUSH | `(s+1) − s = 1` | `1 + 1 = 2` |
| POP | `(s−1) − s = −1` | `1 − 1 = 0` |
| MULTIPOP(S, k) | `k' = min(k, s)`, 차이 `= −k'` | `k' − k' = 0` |

- 결과: amortized cost `O(1)`, total amortized cost `O(n)`, total actual cost `O(n)` *(p.52)*

### 예시 2: Incrementing binary counter *(p.53~57)*
- Potential function `Φ` = **배열 안의 1의 개수**
- `b_i`: i번째 INCREMENT 후 counter의 1의 개수
- `t_i`: i번째 INCREMENT에서 reset된 비트 수
- i번째 연산의 actual cost *(p.53)*: `c_i ≤ t_i + 1`
  - t_i개를 reset하고 추가로 **최대 한 비트**를 1로 set하기 때문
- `b_i`와 `b_{i-1}`의 관계 *(p.54)*:
  - `b_i = 0`인 경우: i번째 연산이 k비트를 전부 reset → `b_{i-1} = t_i = k` (예: 1111 → 0000, `b_{i-1} = k`, `b_i = 0`)
  - `b_i > 0`인 경우: `b_i = b_{i-1} − t_i + 1` (예: 0111 → 1000, `b_{i-1} = k−1`, `b_i = 1`)
  - 두 경우 모두 `b_i ≤ b_{i-1} − t_i + 1`
- Potential difference *(p.55)*:
  - `Φ(D_i) − Φ(D_{i-1}) = b_i − b_{i-1} ≤ (b_{i-1} − t_i + 1) − b_{i-1} = 1 − t_i`
- Amortized cost *(p.55)*:
  - `ĉ_i = c_i + Φ(D_i) − Φ(D_{i-1}) ≤ (t_i + 1) + (1 − t_i) = 2` → `O(1)`
- **counter가 0에서 시작하면** `Φ(D_0) = 0`이고 모든 i에 `Φ(D_i) ≥ 0` → n번 INCREMENT의 총 amortized cost가 총 actual cost의 upper bound, worst-case 비용 `O(n)` *(p.56)*
- **0에서 시작하지 않는 경우** *(p.57)*:
  - `0 ≤ b_0, b_n ≤ k` (k: counter의 비트 수)
  - `Σ c_i = Σ ĉ_i − Φ(D_n) + Φ(D_0)` (모든 i에 `ĉ_i ≤ 2`)
  - `≤ Σ 2 − b_n + b_0` (`Φ(D_n) = b_n`, `Φ(D_0) = b_0`)
  - `= 2n − b_n + b_0`
  - 총 actual cost는 `O(n)` (**k = O(n)** 이면, `b_0, b_n ≤ k`이므로)

---

## 수업에서 다룬 섹션
1. Accounting method 정의 — charge, amortized cost, credit, 조건 `Σĉ_i ≥ Σc_i` (p.20~21)
2. Accounting: stack operation — PUSH 2 / POP 0 / MULTIPOP 0 (p.22~29)
3. Accounting: incrementing binary counter — bit set 2 / reset 0 (p.30~40)
4. Potential method 정의 — Φ, potential difference (p.42~47)
5. Amortized cost 식 `ĉ_i = c_i + Φ(D_i) − Φ(D_{i-1})`, telescoping, `Φ(D_i) ≥ Φ(D_0)` 조건 (p.48)
6. Potential: stack operation — Φ = 객체 수 (p.49~52)
7. Potential: incrementing binary counter — Φ = 1의 개수, `c_i ≤ t_i+1`, `ĉ_i ≤ 2`, 0에서 시작하지 않는 경우 (p.53~57)
