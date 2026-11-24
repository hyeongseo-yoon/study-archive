# Chapter 17-3: Amortized Analysis (Dynamic Table)

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*Slides from Heejin Park, Hanyang Univ. / 파일: `17_Amortized_Analysis(Dynamic_Table).pdf` (슬라이드 p.58~124)*

## 0. 개요 *(슬라이드 p.58)*
- Contents: Aggregate analysis, Accounting method, Potential method, **Dynamic Table**
- 이 PDF(3편)는 Dynamic Table을 세 가지 분석 방법(aggregate / accounting / potential)으로 분석한다.

## 1. Dynamic tables *(p.59)*
- **Table allocation problem**: 응용에서 table에 객체를 몇 개 저장할지 미리 알 수 없는 경우가 많다.
- **insertion**: table 공간을 할당해 두고, 새 항목이 들어갈 때 table을 **reallocate**한다.
- **deletion**: 객체가 많이 삭제되면 더 작은 크기로 reallocate하는 편이 나을 수 있다.
- amortized analysis로 insertion과 deletion의 amortized cost가 **O(1)** 임을 보인다.

## 2. TABLE-INSERT와 Aggregate analysis

### INSERT 방식 *(p.60~61)*
- 가득 찬 table에 삽입할 때 기존보다 슬롯이 많은 새 table을 할당해 **expand**한다.
- 흔한 heuristic: 새 table을 기존의 **2배 슬롯**으로 할당.
- `T.table`: table 저장 블록을 가리키는 포인터 / `T.num`: table 안 항목 수 / `T.size`: table의 전체 슬롯 수

### TABLE-INSERT 의사코드 *(p.62)*
```
TABLE-INSERT(T, x)
1   if T.size == 0
2       allocate T.table with 1 slot
3       T.size = 1
4   if T.num == T.size
5       allocate new-table with 2 * T.size slots
6       insert all items in T.table into new-table      ← elementary insertion (expansion 때)
7       free T.table
8       T.table = new-table
9       T.size = 2 * T.size
10  insert x into T.table                               ← elementary insertion
11  T.num = T.num + 1
```
- elementary insertion은 두 종류: line 6(expansion 때 옮기기), line 10(새 항목 삽입)

### 비용 분석 *(p.63~68)*
- 초기에 빈 table에 n번의 TABLE-INSERT를 수행한다고 하자.
- table에 자리가 있으면 `c_i = 1`
- table이 가득 차 expansion이 일어나면 `c_i = i` (새 항목 삽입 1 + 옮기기 i−1)
- 슬라이드 그림(p.63~66): 1칸 → 2칸 → (3번째 삽입에서 4칸) → 4칸까지 채움
- 정리 *(p.67)*:
  - `c_i = i` (i−1이 2의 거듭제곱일 때), `1` (그 외)
- 총 비용 *(p.68)*:
  - `Σ_{i=1}^{n} c_i = n + Σ_{j=0}^{⌊lg(n−1)⌋} 2^j < n + Σ_{j=0}^{lg n} 2^j < n + 2n = 3n`

### 다른 관점의 분석 *(p.69~74)*
- 1~n번째 삽입에서 새 항목을 넣는 비용은 각각 1 → 총 `1 * n = n` *(p.69~71)*
- expansion은 table 크기가 2의 거듭제곱일 때 일어난다(`2^j`번 삽입 후). 일어나는 횟수는 `lg(n−1)`번 *(p.72~73)*
- expansion 비용 합: `Σ 2^j` (j = 0 ~ ⌊lg(n−1)⌋)
- 총 비용 *(p.74)*: `Σ c_i = n + Σ_{j=0}^{⌊lg(n−1)⌋} 2^j < n + Σ_{j=0}^{lg n} 2^j < n + 2n = 3n`
- n번 TABLE-INSERT의 총 비용이 `3n`으로 bounded → 연산 하나의 **amortized cost는 최대 3** (3n / n)

## 3. TABLE-INSERT와 Accounting method *(p.75~86)*
- accounting method로 TABLE-INSERT의 amortized cost가 왜 **3**이어야 하는지 감을 잡을 수 있다 *(p.75)*.
- elementary insertion 두 종류 *(p.77)*: line 6(table 옮기기), line 10(x 삽입)
- 각 항목이 elementary insertion 3번 분을 낸다 *(p.78)*:
  - 1 cost는 line 10에 사용
  - 2 credit은 line 6(expansion 때 옮기기)을 위해 저장. **credit은 expansion이 일어날 때 항목을 옮기는 데 쓴다**
- 구체적으로 각 항목이 낸 3은 *(p.79~)*:
  1. 자기 자신을 현재 table에 삽입
  2. table이 expand될 때 **자기 자신**을 옮기기
  3. table이 expand될 때 **이미 한 번 옮겨진 다른 항목**을 옮기기
- 슬라이드 그림(p.79~86): 크기 4 table에 항목 1~4가 들어갈 때 새로 들어온 항목 아래 credit이 쌓인다
  - 삽입 직후 새 항목 credit 1 (p.79~83), 크기 4가 되면 credit이 각각 1씩(1 1 1 1)
  - 5번째 항목 삽입으로 expansion이 일어나면 옮겨진 항목들이 credit을 소모(0), 새 항목들이 credit을 다시 쌓아 감 (p.84~86: `1 2 3 4` / `0 0 0 0`)
  - 즉 expansion 직전에 table이 가득 차면 항목마다 credit이 쌓여 있어 옮기는 비용을 전부 낼 수 있다

## 4. TABLE-INSERT와 Potential method *(p.87~94)*
- potential method로 n번 TABLE-INSERT를 분석할 수 있다. 또 17.4.2에서 TABLE-DELETE도 O(1) amortized cost가 되도록 설계하는 데 쓴다 *(p.87)*.

### Potential function *(p.88~89)*
- 요구 조건: **expansion 직후에는 0**, **table이 가득 찰 때에는 table 크기(=항목 수)** 만큼 쌓여 있어야 한다.
- `Φ(T) = 2*T.num − T.size` (17.5)
- expansion 직전에는 `T.num = T.size` → `Φ(T) = T.num`
- `Φ(T)`는 항상 **음이 아니다**:
  - 초기 potential = 0
  - table이 항상 **적어도 절반은 차 있으므로** `T.num ≥ T.size/2`
- 슬라이드 그림: expansion 직전 `Φ_i = num_i` (p.90), expansion 직후 `Φ_i = 0`이었다가 바로 **2 증가** (p.91)

### i번째 TABLE-INSERT의 amortized cost *(p.92)*
- `num_i`: i번째 연산 후 항목 수 / `size_i`: i번째 연산 후 table 크기 / `Φ_i`: i번째 연산 후 potential / `ĉ_i`: Φ에 대한 amortized cost
- 초기: `num_0 = 0`, `size_0 = 0`, `Φ_0 = 0`

**Expansion이 일어나지 않는 경우** *(p.93)* (`size_i = size_{i-1}`)
- `ĉ_i = c_i + Φ_i − Φ_{i-1}`
- `= 1 + (2*num_i − size_i) − (2*num_{i-1} − size_{i-1})`
- `= 1 + (2*num_i − size_i) − (2*(num_i − 1) − size_i)`
- `= 3`

**Expansion이 일어나는 경우** *(p.94)*
- `size_i = 2*size_{i-1}`, `size_{i-1} = num_{i-1} = num_i − 1` → `size_i = 2*(num_i − 1)`
- `ĉ_i = c_i + Φ_i − Φ_{i-1}`
- `= num_i + (2*num_i − size_i) − (2*num_{i-1} − size_{i-1})`
- `= num_i + (2*num_i − 2*(num_i − 1)) − (2*(num_i − 1) − (num_i − 1))`
- `= num_i + 2 − (num_i − 1)`
- `= 3`

## 5. Table expansion and contraction (TABLE-DELETE)

### Contraction 개념 *(p.95~97)*
- **Table contraction**은 expansion과 대칭: table의 항목 수가 너무 적어지면 더 작은 새 table을 할당하고 항목을 복사한다.
- **load factor**: `α(T) = T.num / T.size`
- 보존하고 싶은 성질 두 가지:
  - dynamic table의 load factor가 **양의 상수로 아래에서 bounded**
  - table 연산의 amortized cost가 **상수로 위에서 bounded**

### TABLE-DELETE 의사코드 (단순 전략) *(p.98)*
```
TABLE-DELETE(T, x)
1   if T.size == 0
2       break
3   delete x from T.table
4   if T.num == T.size / 2
5       allocate new-table with T.size / 2 slots
6       insert all items in T.table into new-table
7       free T.table
8       T.table = new-table
9       T.size = T.size / 2
10  T.num = T.num − 1
```

### 단순 전략의 문제 *(p.99~108)*
- 전략: 가득 찬 table에 삽입하면 **크기 2배**, 삭제로 table이 **절반보다 덜 차게 되면 크기 절반**
- load factor가 1/2 밑으로 안 떨어지는 건 보장되지만 **문제가 있다** *(p.99)*
- 반례 *(p.100)*: n(2의 거듭제곱)개 연산을 table T에 수행
  - 처음 n/2개는 insertion → 총 `Θ(n)`
  - 이 시점에 `T.num = T.size = n/2`
  - 나머지 n/2개 연산은 **insert, delete, delete, insert, insert, delete, delete, insert, insert, ...** 순서
- 슬라이드 그림 *(p.101~107)*:
  - 처음 n/2번 insertion 후 크기 n/2 table이 가득 참
  - 첫 insert → expansion (n/2 elementary insertion, 크기 n)
  - delete, delete → 절반 밑으로 떨어져 contraction (n/2 − 1 elementary insertion, 크기 n/2)
  - insert, insert → 다시 expansion (n/2 elementary insertion)
  - → **연산 2개마다 n/2번의 insertion이 발생**
- 각 expansion·contraction의 비용은 `Θ(n)`이고 그런 연산이 `Θ(n)`개 *(p.108)*
  - n/2번째 연산 이후, 연산 2개마다 비용 n/2
  - 따라서 n번 연산의 총 비용 `Θ(n²)`, 연산 하나의 amortized cost는 `Θ(n)`

### 개선 전략 *(p.109)*
- 가득 찬 table에 삽입하면 **계속 크기 2배**
- 삭제로 table이 **1/4보다 덜 차게 되면** 크기 절반 (이전의 1/2 기준이 아님)
- load factor는 상수 **1/4** 이상으로 bounded

### Potential function *(p.110~114)*
- 빈 table이면 `T.num = T.size = 0`이고 `α(T) = 1`로 둔다 *(p.110)*
- potential function:
  - `Φ_i = 2*num_i − size_i` &nbsp; (`α(T) ≥ 1/2`)
  - `Φ_i = size_i/2 − num_i` &nbsp; (`α(T) < 1/2`)
- `α(T) = 1/4`에서 i번째 연산이 deletion이면 contraction 발생. 필요한 potential은 `num_i` *(p.111)*
- **load factor 1/2**: potential = 0 *(p.112)*
- **load factor 1**: `T.size = T.num` → `Φ(T) = T.num`. potential이 삽입 시의 **expansion** 비용을 낼 수 있다 *(p.113)*
- **load factor 1/4**: `T.size = 4*T.num` → `Φ(T) = T.num`. potential이 삭제 시의 **contraction** 비용을 낼 수 있다 *(p.114)*

### 기호 정의 *(p.115)*
- `c_i`: i번째 연산의 actual cost / `ĉ_i`: Φ에 대한 amortized cost
- `num_i`: i번째 연산 후 항목 수 / `size_i`: 연산 후 table 크기 / `α_i`: 연산 후 load factor / `Φ_i`: 연산 후 potential
- 초기: `num_0 = 0`, `size_0 = 0`, `α_0 = 1`, `Φ_0 = 0`

### TABLE-INSERT 분석 *(p.116~119)*
- `α_{i-1} ≥ 1/2` 이면 17.4.1의 expansion 분석과 동일. expansion이 일어나든 아니든 amortized cost는 **최대 3** *(p.116)*
- `α_{i-1} < 1/2` 이면 table은 expand될 수 없다 *(p.117)*
  - `size_i = size_{i-1}`, `num_{i-1} = num_i − 1`
  - `α_i < 1/2` 이면:
    - `ĉ_i = c_i + Φ_i − Φ_{i-1}`
    - `= 1 + (size_i/2 − num_i) − (size_{i-1}/2 − num_{i-1})`
    - `= 1 + (size_i/2 − num_i) − (size_i/2 − (num_i − 1))`
    - `= 0`
- `α_{i-1} < 1/2` 이지만 `α_i ≥ 1/2` 인 경우 *(p.118~119)*:
  - `Φ_{i-1} = T.size/2 − T.num`, `Φ_i = 2*T.num − T.size`, `num_i = num_{i-1} + 1 = α_i * size_i`
  - `ĉ_i = c_i + Φ_i − Φ_{i-1}`
  - `= 1 + (2*num_i − size_i) − (size_{i-1}/2 − num_{i-1})`
  - `= 1 + (2*(num_{i-1} + 1) − size_{i-1}) − (size_{i-1}/2 − num_{i-1})`
  - `= 3*num_{i-1} − (3/2)*size_{i-1} + 3`
  - `= 3*α_{i-1}*size_{i-1} − (3/2)*size_{i-1} + 3`
  - `< (3/2)*size_{i-1} − (3/2)*size_{i-1} + 3 = 3`
- 따라서 TABLE-INSERT의 amortized cost는 **최대 3**

### TABLE-DELETE 분석 *(p.120~123)*
- `num_i = num_{i-1} − 1` *(p.120)*
- `α_{i-1} < 1/2` 인 경우 두 가지로 나눈다:
  1. contraction이 일어나지 않는 경우 *(p.121)*
     - `size_i = size_{i-1}`
     - `ĉ_i = c_i + Φ_i − Φ_{i-1}`
     - `= 1 + (size_i/2 − num_i) − (size_{i-1}/2 − num_{i-1})`
     - `= 1 + (size_i/2 − num_i) − (size_i/2 − (num_i + 1))`
     - `= 2`
  2. contraction이 일어나는 경우 *(p.122)*
     - actual cost `c_i = num_i + 1`
     - `size_i/2 = size_{i-1}/4 = num_{i-1} = num_i + 1`
     - `ĉ_i = c_i + Φ_i − Φ_{i-1}`
     - `= (num_i + 1) + (size_i/2 − num_i) − (size_{i-1}/2 − num_{i-1})`
     - `= (num_i + 1) + (num_i + 1 − num_i) − (2*num_i + 2 − (num_i + 1))`
     - `= 1`
- `α_{i-1} ≥ 1/2` 인 경우 *(p.123)*:
  - amortized cost는 상수.
  - `α_i < 1/2` 이어도 contraction을 일으키지 않는다.
- **Self-study**: Exercise 17.4-2 *(p.123)*

### 결론 *(p.124)*
- 각 연산의 amortized cost가 상수로 bounded → dynamic table에 대한 **n개 연산 sequence의 실제 시간은 O(n)**

---

## 수업에서 다룬 섹션
1. Dynamic tables — table allocation 문제, expansion/contraction (p.59)
2. TABLE-INSERT와 Aggregate analysis — 2배 확장, `c_i`, 총비용 < 3n (p.60~74)
3. TABLE-INSERT와 Accounting method — 항목당 charge 3 (p.75~86)
4. TABLE-INSERT와 Potential method — `Φ = 2·num − size`, `ĉ_i = 3` (p.87~94)
5. TABLE-DELETE 단순 전략(1/2 기준)과 Θ(n²) 반례 (p.95~108)
6. 개선 전략(1/4 기준)과 potential function (p.109~114)
7. 개선 전략에서 TABLE-INSERT 분석 — `ĉ_i ≤ 3` (p.115~119)
8. 개선 전략에서 TABLE-DELETE 분석 — 축소 없음 2, 축소 발생 1, 결론 O(n) (p.120~124)
