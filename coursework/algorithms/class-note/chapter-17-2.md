# Chapter 17-2 수업노트: Amortized Analysis (Accounting method, Potential method)

*정리 노트: `notes/chapter-17-2.md` / 수업일: 2026-11-23*

## 0. 선수 개념 확인 (17-1 복습)
- **amortized cost**: 전체 연산 비용을 연산 개수로 나눈 값. worst case 상황에서 sequence 전체를 놓고 tight하게 구한 연산당 평균 비용.
- MULTIPOP이 한 번에 O(n)이어도 총 O(n)인 이유: MULTIPOP을 POP 여러 개로 풀어 쓰면 전체 POP 수 ≤ PUSH 수 ≤ n이라 PUSH + POP ≤ 2n.
- binary counter INCREMENT의 비용은 bit flip 횟수에 비례. n번 동안 A[0]은 n번, A[1]은 n/2번, A[2]는 n/4번 flip.
- aggregate analysis에서는 연산 종류가 여러 개여도 모든 연산에 같은 amortized cost를 적용.

## 1. Accounting method 정의 *(p.20~21)*

**Accounting method**: 연산마다 실제 비용과 다른 금액(amortized cost)을 청구하고, 실제보다 더 청구한 차액을 자료구조 안의 객체에 credit으로 저장해 뒀다가, 실제보다 덜 청구한 나중 연산의 비용을 그 credit으로 대신 내는 분석 기법.

- 17-1의 aggregate는 총합을 구해서 n으로 나누는 방식, accounting은 연산마다 가격표를 따로 붙이는 방식.
- `c_i`: i번째 연산의 실제 비용, `ĉ_i`: i번째 연산의 amortized cost(청구 금액)
- 조건: n개 연산의 모든 sequence에서 `Σ ĉ_i ≥ Σ c_i`
- 저장된 총 credit = `Σ ĉ_i − Σ c_i`
- 이 조건이 성립하면 `Σ ĉ_i`가 실제 총 비용의 upper bound. `ĉ_i`를 O(1)로 잡으면 총 비용이 O(n).
- 비유: 선불 교통카드. 충전(더 청구)해 두면 나중에 탈 때 잔액(credit)에서 빠지고, 잔액이 마이너스가 되면 안 된다.

### credit이 음수가 되면? (수업 중 Q&A)
- credit이 음수 = `Σ ĉ_i < Σ c_i`
- 그러면 `Σ ĉ_i`가 실제 총 비용의 upper bound가 아니게 돼서 "총 비용 O(n)" 결론을 낼 수 없다.
- 이건 tight 여부의 문제가 아니라, 계산으로 내놓는 `Σ ĉ_i`가 실제 비용 위에 있어야 실제 비용을 보장할 수 있다는 문제.
- 그래서 **credit은 항상 0 이상**이어야 한다.

## 2. Accounting: stack operation *(p.22~29)*

| 연산 | 실제 비용 | amortized cost |
|---|---|---|
| PUSH | 1 | 2 |
| POP | 1 | 0 |
| MULTIPOP | min(k, s) | 0 |

- **PUSH**: 실제 비용 1을 내고, 추가로 낸 1을 방금 쌓은 원소 위에 credit 1로 붙여 둔다. 청구액 1 + 1 = 2.
- **POP**: 꺼내는 원소에 붙은 credit 1로 실제 비용 1을 낸다. 새로 청구하는 건 0.
- **MULTIPOP**: k'개를 꺼내면 원소마다 붙은 credit k'개로 실제 비용 k'를 낸다. 청구 0.
- 예시 (크기 4 stack): PUSH 3번 → credit 3, MULTIPOP(S, 2) → 원소 2개의 credit 사용 → credit 1 남음. 남은 credit = stack에 남은 원소 수.
- **credit은 항상 stack의 원소 수와 같다.** 원소 하나당 credit 1이 붙고, 그 원소가 나갈 때만 쓰인다. 원소 수는 음수가 될 수 없으므로 credit도 음수가 되지 않는다. MULTIPOP도 min(k, s)개만 꺼내니 가진 credit 이상은 쓰지 않는다.
- 따라서 `Σĉ_i ≥ Σc_i`. 총 amortized cost 최대 2n = O(n)이 실제 총 비용의 upper bound.

## 3. Accounting: incrementing binary counter *(p.30~40)*

- 실제 비용: bit set(0→1) 1, bit reset(1→0) 1
- amortized cost: **bit set 2, bit reset 0**
- 비트를 1로 set할 때 실제 비용 1과 함께 1을 더 내서 그 비트 위에 credit 1을 붙여 둔다. 나중에 그 비트를 reset할 때 그 credit으로 실제 비용을 낸다.

### 0000 → 0100까지 직접 따라가기 (k=4)

| 변화 | set | reset | credit이 붙은 비트 |
|---|---|---|---|
| 0000 → 0001 | A[0] | 없음 | A[0] |
| 0001 → 0010 | A[1] | A[0] | A[1] |
| 0010 → 0011 | A[0] | 없음 | A[0], A[1] |
| 0011 → 0100 | A[2] | A[0], A[1] | A[2] |

- credit 총량은 0 → 1 → 1 → 2 → 1. 마지막 0100에서 credit 1.
- **credit은 현재 1인 비트마다 1개씩** 붙어 있다. 즉 credit 개수 = counter 안의 1의 개수. stack에서 credit = 원소 수였던 것과 같은 구조.

### 왜 O(n)인가
- reset은 항상 그 비트가 먼저 set된 뒤에만 일어나서, 붙어 있는 credit으로 실제 비용을 낼 수 있다. reset의 amortized cost는 0.
- credit = 1의 개수라 음수가 안 된다. `Σĉ_i ≥ Σc_i` 성립.
- INCREMENT 한 번은 최대 한 비트만 set하니 amortized cost 최대 2. n번이면 총 amortized cost 최대 2n = O(n)이 실제 총 비용의 upper bound.
- 17-1 aggregate 결과(O(n), amortized O(1))와 같은 답을 다른 방법으로 증명.

### 반대 케이스 (수업 중 Q&A)
- bit set을 amortized cost 1(실제와 같게), reset을 0으로 청구하면 set에서 credit이 안 쌓이는데 reset은 실제 비용 1을 내야 하므로 첫 reset에서 credit이 −1이 되어 분석이 깨진다.
- Accounting의 핵심: credit이 항상 0 이상이 되게 미리 충분히 청구해 두는 것. 그러면 amortized cost의 합이 실제 비용의 upper bound.

## 4. Potential method 정의 *(p.42~47)*

**Potential method**: accounting의 credit을 특정 객체가 아니라 자료구조 전체의 상태에 대한 함수 Φ(potential)로 바꿔서, 연산 전후의 potential 변화로 amortized cost를 정의하는 분석 기법.

- accounting: 비트별로 credit이 붙어 있다 (A[0]에 1, A[1]에 1 ...)
- potential: 상태 전체에 값 하나. 예를 들어 binary counter 0011이면 potential은 2(1의 개수)이고 비트별 위치는 따로 안 본다.
- 기호
  - `D_0`: 초기 자료구조
  - `D_i`: i번째 연산을 `D_{i-1}`에 적용한 결과
  - `Φ(D_i)`: `D_i`의 potential
  - potential difference `Φ(D_i) − Φ(D_{i-1})`
    - 양수: potential 증가 = credit 저축
    - 음수: potential 감소분이 그 연산의 실제 비용을 지불

## 5. Amortized cost 식과 조건 *(p.48)*

- `ĉ_i = c_i + Φ(D_i) − Φ(D_{i-1})` (실제 비용 + potential 변화량)
- 1부터 n까지 더하면 telescoping: `Σ ĉ_i = Σ c_i + Φ(D_n) − Φ(D_0)`
  - `Φ(D_i)`는 i번째 항에서 `+`, (i+1)번째 항에서 `−`로 나와서 서로 지워진다. 맨 처음 `−Φ(D_0)`와 맨 끝 `+Φ(D_n)`만 남는다.
- `Σ ĉ_i ≥ Σ c_i`가 되려면 `Φ(D_n) − Φ(D_0) ≥ 0`이 필요. 슬라이드는 모든 i에 대해 `Φ(D_i) ≥ Φ(D_0)`를 요구 (어느 k에서 끊어도 성립하도록).
- accounting의 "credit ≥ 0" ↔ potential의 "`Φ(D_i) ≥ Φ(D_0)`" (보통 `Φ(D_0) = 0`, `Φ(D_i) ≥ 0`).

## 6. Potential: stack operation *(p.49~52)*

- Φ(D_i) = stack에 들어 있는 객체 수. `Φ(D_0) = 0`, 모든 i에 `Φ(D_i) ≥ 0`이므로 조건 만족.
- s개 원소가 든 stack에서 i번째 연산 (`ĉ_i = c_i + ΔΦ`):

| 연산 | c_i | ΔΦ | ĉ_i |
|---|---|---|---|
| PUSH | 1 | (s+1) − s = +1 | 2 |
| POP | 1 | (s−1) − s = −1 | 0 |
| MULTIPOP(S, k) | k' = min(k, s) | −k' | 0 |

- 주의: MULTIPOP의 `c_i`는 1이 아니라 `k'`.
- accounting에서 청구한 값(2, 0, 0)과 완전히 같다. Φ를 원소 수로 잡으면 accounting에서 원소마다 붙은 credit의 총합을 처음부터 하나의 함수로 잡은 것이기 때문.
- amortized cost 연산당 O(1), 총 O(n). `Φ(D_0)=0`, `Φ(D_i)≥0`이라 실제 총 비용 O(n)의 upper bound.

## 7. Potential: incrementing binary counter *(p.53~57)*

- Φ = 배열 안의 **1의 개수**
- `b_i`: i번째 INCREMENT 후 1의 개수 (`Φ(D_i) = b_i`)
- `t_i`: i번째 INCREMENT에서 reset된 비트 수

### 실제 비용
- reset이 `t_i`번, set은 최대 1번 → **`c_i ≤ t_i + 1`**. (k비트가 전부 1이면 set이 없어서 `c_i = t_i`. 그래서 `≤`.)

### 예 (k=4)
- 예 A: 0111 → 1000. reset A[0], A[1], A[2] → `t_i = 3`, `b_{i-1} = 3`, `b_i = 1`. `b_i = b_{i-1} − t_i + 1`.
- 예 B: 1111 → 0000. `t_i = 4`, set 없음, `b_{i-1} = 4`, `b_i = 0`. `b_{i-1} = t_i = k`.
- 일반적인 경우는 `b_i = b_{i-1} − t_i + 1`, set이 없으면 `b_i = b_{i-1} − t_i`. 합치면 항상 **`b_i ≤ b_{i-1} − t_i + 1`**.

### amortized cost
- `Φ(D_i) − Φ(D_{i-1}) = b_i − b_{i-1} ≤ (b_{i-1} − t_i + 1) − b_{i-1} = 1 − t_i`
- `ĉ_i = c_i + ΔΦ ≤ (t_i + 1) + (1 − t_i) = 2` → **O(1)**
- `t_i`가 지워지는 이유: reset은 1을 0으로 바꿔서 1의 개수(Φ)를 `t_i`만큼 줄이고, set은 최대 1개 늘린다. 그래서 ΔΦ ≤ 1 − t_i. reset이 많을수록 실제 비용이 커지지만 Φ도 그만큼 떨어져서 상쇄되고, 남는 건 set 1번분의 상수 2. accounting에서 "set 때 2를 청구해서 credit 1을 붙여두면 reset은 공짜"였던 것과 같은 얘기.
- 계산 확인
  - 예 A: `c_i = 4`, `ΔΦ = 1 − 3 = −2` → `ĉ_i = 2`
  - 예 B: `c_i = 4`, `ΔΦ = 0 − 4 = −4` → `ĉ_i = 0`. 최악의 INCREMENT인데 amortized cost가 0인 이유는 쌓아둔 potential(1의 개수 4)을 전부 써서 냈기 때문.

### 총 비용 *(p.56~57)*
- counter가 **0에서 시작**: `Φ(D_0) = 0`, `Φ(D_i) ≥ 0` → 총 amortized cost 최대 2n이 실제 총 비용의 upper bound, worst-case O(n).
- **0에서 시작하지 않는 경우**: `Φ(D_0) = b_0 ≠ 0`
  - `Σ c_i = Σ ĉ_i − Φ(D_n) + Φ(D_0) ≤ 2n − b_n + b_0`
  - `b_0, b_n ≤ k`이므로 **k = O(n)** 이면 총 실제 비용 O(n).

## 두 방법 비교 (수업 중 정리)
- credit은 객체 하나하나에 붙고, potential은 자료구조 전체의 단일 값.
- 조건: accounting은 credit이 0 이상, potential은 `Φ(D_i) ≥ Φ(D_0)`.
