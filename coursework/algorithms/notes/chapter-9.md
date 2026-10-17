# Chapter 9: Dynamic Programming

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein) / Slides from Heejin Park, Hanyang Univ.*

다루는 문제 4개: **Assembly-line scheduling → Rod cutting → Longest common subsequence(LCS) → Matrix-chain multiplication**. 각 문제마다 "brute force가 왜 안 되는지 → optimal substructure로 점화식 → 표 채우기(bottom-up) → 해 복원(trace) → 공간/시간 복잡도" 순서로 같은 틀을 반복한다.

## 0. 개요 *(슬라이드 p.2)*
- Contents: Assembly-line scheduling, Rod cutting, Longest common subsequence, Matrix-chain multiplication
- 각 문제를 푼 뒤 **Space / Time 복잡도 표**로 요약한다 *(p.30, 44, 78, 91)*

## 1. Assembly-line scheduling *(p.3~29)*

### 문제 정의 *(p.3~6)*
- 조립 라인에 **n개의 station** `S_i`, station i에서의 조립 시간 `a_i`, 진입 시간 `e`, 탈출 시간 `x`
- 문제: **가장 빠른 조립 시간**을 구하라
- 라인이 2개: `S_{1,1}..S_{1,n}` (line 1), `S_{2,1}..S_{2,n}` (line 2). 각각 `a_{i,j}`, 진입 시간 `e_1, e_2`, 탈출 시간 `x_1, x_2`
- 라인 사이를 옮기는 **transfer time** `t_{i,j}` (station j를 마친 뒤 반대 라인으로 이동하는 시간)

### Brute force *(p.7)*
- 가능한 모든 경로를 나열해 가장 빠른 것을 고름
- 경로가 **2^n**개 → 너무 많음

### Optimal substructure *(p.8)*
- `S_{i,j}`까지 가는 가장 빠른 경로는 **`S_{1,j-1}` 또는 `S_{2,j-1}`을 지난다**
  - 같은 라인에서 오면 transfer 없이 `+a_{i,j}`, 다른 라인에서 오면 `+t +a_{i,j}`

### 예시 계산 *(p.9~14, p.19~28)*
- 6개 station 예시 (line 1: a = 7 9 3 4 8 4, line 2: a = 8 5 6 4 5 7, e = 2, 4 / x = 3, 2, transfer time은 두 라인 사이에 각각 2 1 1 3 4 와 2 1 2 2 1)
- 테이블 `s[i][j]` (station j까지 최단 시간)
  - line 1: 9, 18, 20, 24, 32, 35
  - line 2: 12, 16, 22, 25, 30, 37
  - 최종 `s* = min(35+3, 37+2) = 38` (line 1에서 탈출, `l* = 1`)
- 각 칸을 채울 때 "같은 라인 유지 : 다른 라인에서 옮겨 옴"을 비교 (예: `18 : 23`, `21 : 20`, `24 : 28` 처럼 두 후보 중 작은 값을 택함) *(p.9, 20~28)*
- 테이블 `l[i][j]` : station j에서 i번 라인을 택했을 때 **직전 station이 어느 라인이었는지** 기록 *(p.13)*
  - l[1] = - 1 2 1 1 2, l[2] = - 1 2 1 2 2
- 이 `l` 테이블로 경로를 거꾸로 따라가 **fastest way**를 복원 *(p.11~14)*

### 알고리즘 *(p.15)*
`FASTEST-WAY(a, t, e, x, n)`
1. `s[1][1] = e[1] + a[1][1]`, `s[2][1] = e[2] + a[2][1]`
2. `j = 2..n`에 대해
   - `s[1][j-1] ≤ s[2][j-1] + t[2][j-1]`이면 `s[1][j] = s[1][j-1] + a[1][j]`, `l[1][j] = 1`; 아니면 `s[1][j] = s[2][j-1] + t[2][j-1] + a[1][j]`, `l[1][j] = 2`
   - line 2도 대칭으로 계산
3. `s[1][n] + x[1] ≤ s[2][n] + x[2]`이면 `s* = s[1][n] + x[1]`, `l* = 1`; 아니면 `s* = s[2][n] + x[2]`, `l* = 2`

### 경로 출력 *(p.16)*
`PRINT-STATIONS(l, l*, n)`: `i = l*` → "line i, station n" 출력 → `j = n downto 2`에서 `i = l[i][j]`, "line i, station j-1" 출력
- 예시 결과: line 1 st.6 ← line 2 st.5 ← line 2 st.4 ← line 1 st.3 ← line 2 st.2 ← line 1 st.1

### 복잡도 *(p.17~18, 29)*
- **공간**: 테이블 s, l 각각 2n → 합쳐서 Θ(n)
- **시간**: 각 원소 계산 Θ(1) × Θ(n)개 → Θ(n)
- **최단 시간만** 필요하면 `l`이 불필요하고, `s`도 **2n개 → 4개**(직전 열의 2개 + 현재 열의 2개)로 줄어 **Θ(1) 공간** *(p.18, 29)*

## 2. Rod cutting *(p.31~43)*

### 문제 정의 *(p.31)*
- 길이 n인치 막대와 가격표 `p_i` (i = 1..n)가 주어질 때, 막대를 잘라 팔아 얻을 수 있는 **최대 수익 `r_n`**을 구하라
- 예시 가격표: 길이 1~10 → 가격 1, 5, 8, 9, 10, 17, 17, 20, 24, 30

### 자르는 방법 나열 *(p.32)*
- 길이 4 막대: 안 자름(9), 1+3, 2+2(= 5+5 = 10), 1+1+2, 1+1+1+1 등 (a)~(h) 8가지 → 길이 n 막대는 2^(n-1)가지

### 점화식 *(p.33)*
- `r_n = max_{1≤i≤n} ( p_i + r_{n-i} )`
  - 첫 조각의 길이 i를 정하고, 나머지 `n-i`는 **부분문제의 최적해** `r_{n-i}`를 사용

### 표 채우기 (n = 10) *(p.34~37)*
- `r[0] = 0`, `r[1] = p[1] + r[0] = 1`
- `r[2] = max(p[1]+r[1] = 2, p[2]+r[0] = 5) = 5`
- `r[3] = max(p[1]+r[2] = 6, p[2]+r[1] = 6, p[3]+r[0] = 8) = 8`
- 완성된 `r[0..10]` = 0, 1, 5, 8, 10, 13, 17, 18, 22, 25, 30
- `r[10]`은 `p[1]+r[9] = 26`, `p[2]+r[8] = 27`, …, `p[10]+r[0] = 30` 중 최대 → 30

### 해 복원용 테이블 `s` *(p.38~41)*
- `s[i]` = 길이 i에서 최적이 되는 **첫 조각의 길이**
- `s[0..10]` = 0, 1, 2, 3, 2, 2, 6, 1, 2, 3, 10

`EXTENDED-BOTTOM-UP-CUT-ROD(p, n)` *(p.39)*
```
r[0] = 0
for j = 1 to n
    q = -∞
    for i = 1 to j
        if q < p[i] + r[j-i]
            q = p[i] + r[j-i]
            s[j] = i
    r[j] = q
return r and s
```
`PRINT-CUT-ROD-SOLUTION(p, n)` *(p.40)*: `(r, s)`를 구한 뒤 `while n > 0: print s[n]; n = n - s[n]`

### 복잡도 *(p.42~43)*
- **공간** Θ(n), **시간** Θ(n²) (이중 루프, 1 + 2 + … + n = n(n+1)/2)
- 슬라이드의 생각해볼 질문: assembly-line에서 `s`를 줄였던 것처럼 **테이블 `r`도 줄일 수 있는가?** *(p.43)* — `r[j]`가 `r[0..j-1]` 전부를 참조하므로 쉽지 않음

## 3. Longest common subsequence (LCS) *(p.45~77)*

### 용어 정의 *(p.45~47)*
- **Character**, **String(sequence)**: 문자의 나열 (예: {0,1} 위의 binary string, {A,C,G,T} 위의 DNA sequence)
- **Substring**: 연속한 부분 — `CBD`는 `ABCBDAB`의 substring
- **Subsequence**: 순서만 유지하면 되는 부분 — `BCDB`는 `ABCBDAB`의 subsequence
- **Common subsequence**: 두 문자열 모두의 subsequence — `BCA`는 `X = ABCBDAB`, `Y = BDCABA`의 common subsequence
- **LCS**: 가장 긴 common subsequence — 위 X, Y의 LCS는 `BCBA`

### Brute force *(p.48)*
- X의 모든 subsequence를 나열해 Y의 subsequence인지 검사 → **불가능(infeasible)**: X의 subsequence 수가 **2^m**

### Optimal substructure *(p.49~51)*
- **Prefix** `X_i = x_1 x_2 … x_i` (`X_4 = ABCB`, `X_0` = 빈 문자열)
- `Z = z_1..z_k`가 `X_m`, `Y_n`의 LCS일 때
  1. **`x_m = y_n`이면** `z_k = x_m = y_n`이고, `Z_{k-1}`은 `X_{m-1}`과 `Y_{n-1}`의 LCS *(p.50)*
  2. **`x_m ≠ y_n`이면** Z는 `X_{m-1}`과 `Y`의 LCS 이거나, `X`와 `Y_{n-1}`의 LCS *(p.51)*

### 점화식 *(p.52)*
`c[i][j]` = `X_i`와 `Y_j`의 LCS 길이
- `0` (i = 0 또는 j = 0)
- `c[i-1][j-1] + 1` (i, j > 0 이고 `x_i = y_j`)
- `max(c[i][j-1], c[i-1][j])` (i, j > 0 이고 `x_i ≠ y_j`)

### 표 채우기 *(p.53)*
- X = ABCBDAB (행 i), Y = BDCABA (열 j)에 대한 `c` 테이블과 화살표 `b` 테이블 (대각 ↖ = 문자 일치, ↑ = 위쪽 값 사용, ← = 왼쪽 값 사용)
- 최종 `c[7][6] = 4` → LCS 길이 4

### 알고리즘 *(p.54~55)*
`LCS-LENGTH(X, Y)`
- `c[i][0] = 0`, `c[0][j] = 0`으로 초기화
- `x_i == y_j`이면 `c[i][j] = c[i-1][j-1] + 1`, `b[i][j] = ↖`
- `else if c[i-1][j] ≥ c[i][j-1]`이면 `c[i][j] = c[i-1][j]`, `b[i][j] = ↑`
- `else c[i][j] = c[i][j-1]`, `b[i][j] = ←`
- `c`, `b` 반환

`PRINT-LCS(b, X, i, j)`: `i == 0 or j == 0`이면 return. `b[i][j] = ↖`이면 `PRINT-LCS(b, X, i-1, j-1)` 후 `x_i` 출력, `↑`이면 `(i-1, j)`, 아니면 `(i, j-1)`로 재귀

### LCS가 여러 개인 경우 *(p.56~59)*
- `c[i-1][j] = c[i][j-1]`처럼 **값이 같은 경우 `←↑` 두 방향이 모두 가능** → 어느 쪽으로 따라가느냐에 따라 서로 다른 LCS가 나옴 (p.56~59는 경로를 달리 따라가는 예시)

### 복잡도와 공간 줄이기 *(p.60~77)*
- **공간 Θ(mn), 시간 Θ(mn)** *(p.60)*
- **LCS의 길이만** 필요하면 공간을 **Θ(min(m, n))**으로 축소 가능 *(p.60, 77)*
  - `c[i][j]`는 **바로 윗 행(i-1)** 과 같은 행만 참조하므로 한 행만 유지하며 위에서 아래로 갱신 *(p.61~74: X의 문자 A, B, C, B, D, A, B를 하나씩 처리하며 한 행(0 0 0 0 0 0 0)을 덮어쓰는 과정, 최종 행 마지막 값 4)*
  - 문자열이 매우 긴 경우(예: 길이 100,000) 전체 테이블이 필요 없음 *(p.75~76)*; 두 문자열 중 **짧은 쪽을 열 방향**으로 두면 공간이 min(m, n)
- (`b` 테이블이 없으므로 LCS 자체는 복원 불가 — 길이만 구하는 경우에 해당)

## 4. Matrix-chain multiplication *(p.79~90)*

### 행렬 곱 복습 *(p.79~80)*
- A(p×q)와 B(r×s)는 **q = r일 때만** 곱할 수 있고 결과는 **p×s**
- **스칼라 곱셈 횟수 = pqs** (ps개의 원소 × 원소당 q번 곱셈)

### 곱셈 순서가 비용을 바꾼다 *(p.81~82)*
- `(A1·A2)·A3 = A1·(A2·A3)` — **값은 같지만 연산량은 다름**
- 예시: A1: 10×100, A2: 100×5, A3: 5×50
  - `(A1 A2) A3`: (A1A2) = 10·100·5 = 5,000 → (10×5)·A3 = 10·5·50 = 2,500 → 합계 **7,500**
  - `A1 (A2 A3)`: (A2A3) = 100·5·50 = 25,000 → A1·(100×50) = 10·100·50 = 50,000 → 합계 **75,000**
  - 앞의 순서가 **10배 빠르다**

### 문제 정의 *(p.83)*
- n개 행렬 사슬 `A_1, …, A_n` (A_i의 크기는 `p_{i-1} × p_i`)가 주어질 때, 스칼라 곱셈 횟수를 **최소화**하는 곱셈 순서(= 완전한 괄호 치기, full parenthesization)를 구하라
- 입력은 차원 배열 `p_0, p_1, …, p_n`

### Brute force *(p.84~85)*
- A1A2A3A4는 5가지로 괄호 칠 수 있음: `A1(A2(A3A4))`, `A1((A2A3)A4)`, `(A1A2)(A3A4)`, `(A1(A2A3))A4`, `((A1A2)A3)A4`
- 개수 `P(n)`: `P(1) = 1`, `P(n) = Σ_{k=1}^{n-1} P(k)·P(n-k)` (n ≥ 2) → **Ω(4^n / n^{3/2})** → 비효율적
- Self-study: CLRS 15.2-3, `P(n) = Ω(2^n)` 증명

### Optimal substructure와 점화식 *(p.86)*
- `m[i][j]` = `A_i A_{i+1} … A_j` 계산에 필요한 **최소 스칼라 곱셈 수**
  - `m[i][j] = 0` (i = j)
  - `m[i][j] = min_{i≤k<j} { m[i][k] + m[k+1][j] + p_{i-1} p_k p_j }` (i < j)
- `A_{i..k}`와 `A_{k+1..j}`를 곱하는 비용이 `p_{i-1} p_k p_j`
- `s[i][j]`에 최적의 분할점 `k`를 저장해 최적해를 복원

### 표 채우기 예시 *(p.87)*
- 차원 `p = 30, 35, 15, 5, 10, 20, 25` (행렬 6개)
- `m[1][6] = 15125`
- 예: `m[2][5] = min { m[2][2] + m[3][5] + p1·p2·p5 = 0 + 2500 + 35·15·20 = 13000, m[2][3] + m[4][5] + p1·p3·p5 = 2625 + 1000 + 35·5·20 = 7125, m[2][4] + m[5][5] + p1·p4·p5 = 4375 + 0 + 35·10·20 = 11375 }` = **7125** (k = 3, 즉 `(A2 A3)(A4 A5)`)
- k의 후보: `(A2)(A3A4A5)`, `(A2A3)(A4A5)`, `(A2A3A4)(A5)`

### 알고리즘 *(p.88~89)*
`MATRIX-CHAIN-ORDER(p)`
```
n = p.length - 1
for i = 1 to n: m[i][i] = 0
for l = 2 to n                    // l is the chain length
    for i = 1 to n - l + 1
        j = i + l - 1
        m[i][j] = ∞
        for k = i to j - 1
            q = m[i][k] + m[k+1][j] + p[i-1]·p[k]·p[j]
            if q < m[i][j]
                m[i][j] = q
                s[i][j] = k
return m and s
```
- **사슬 길이 l이 짧은 것부터** 채우는 bottom-up

`PRINT-OPTIMAL-PARENS(s, i, j)`: `i == j`면 "A_i" 출력, 아니면 "(" 출력 → `(s, i, s[i][j])` → `(s, s[i][j]+1, j)` → ")" 출력

### 복잡도 *(p.90)*
- **공간** Θ(n²) (`m`, `s` 테이블)
- **시간** Θ(n³): 길이 l인 부분문제 `n-l+1`개 × 분할점 `l-1`개를 합하면 `(n³ + 5n)/6 = Θ(n³)`

## 5. 결론: 복잡도 요약 *(p.91)*

| 문제 | Space | Time |
|---|---|---|
| Assembly-line scheduling | Θ(n) | Θ(n) |
| Rod cutting | Θ(n) | Θ(n²) |
| Longest common subsequence | Θ(n²) (= Θ(mn)) | Θ(n²) (= Θ(mn)) |
| Matrix-chain multiplication | Θ(n²) | Θ(n³) |

- (p.78 중간 요약표에는 LCS가 Θ(mn) / Θ(n²) 두 줄로 나란히 표기됨 — 일반형 Θ(mn)과 m = n일 때 Θ(n²))
