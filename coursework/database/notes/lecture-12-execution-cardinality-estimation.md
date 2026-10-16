# Lecture 12: Query Execution — Cardinality Estimation

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Database Systems & its Applications — Cardinality Estimation*

> 슬라이드 쪽번호가 인쇄되어 있지 않거나 잘려 있어서, 아래 `p.N`은 PDF 파일의 페이지 순서(1부터 시작)를 가리킨다.
> 구성: **① Logical Query Optimization 예제 → ② Cardinality estimation 소개 → ③ 가정(Assumptions)으로부터 selectivity factor 유도 → ④ 종합 예제**

## 0. Outline *(p.2, 16, 23, 47)*
- Logical Query Optimization: Examples
- Cardinality estimation: Introduction / Deriving Selectivity Factors from Assumptions / Examples

## 1. Logical Query Optimization 예제 *(p.3~15)*

### Plan Enumeration에서 Execution까지 *(p.3)*
- RDBMS: SQL → Relational Algebra → **동치인 여러 Logical Plan**(조인 순서가 다른 트리들) → **Physical Plans**(각 join에 `⋈_smj`(sort-merge), `⋈_hj`(hash), `⋈_nlj`(nested loop) 등 알고리즘 선택) → **Least Cost Plan** → Execution
- 이 강의의 **Cardinality Estimation**은 이 과정에서 plan의 비용을 비교하는 데 쓰인다

### 암묵적 최적화 목표 *(p.4)*
- 동치인 query plan은 **같은 출력**을 낸다. 그럼 **어떻게, 왜 하나를 고르는가?**
- **트리 안에서 순환하는 데이터가 적을수록 RDBMS의 계산이 줄어든다**. 불필요한 column이나 불필요하게 큰 column을 줄이는 것도 포함되지만, 이 강의는 **중간 tuple 수를 줄이는 것**에 집중한다

### 사용하는 스키마 *(p.5)*
`Suppliers(sid, name, city, state)`, `Supplies(sid, pid, quantity)`, `Parts(pid, name, price)`

### Example Optimization #1: Push Selections Down *(p.5~7)*
```sql
SELECT x.sid, y.pid, y.quantity
FROM Suppliers x, Supplies y
WHERE x.sid = y.sid AND x.city = 'Seattle' AND x.state = 'WA'
```
- 원래 plan: `π_{x.sid, y.pid, y.quantity}(σ_{x.city='Seattle' and x.state='WA'}(Suppliers x ⋈_{x.sid=y.sid} Supplies y))` — join 후에 선택
- **Selection을 join 아래로 내린다 (Push Selections Down)**: `σ_C(R ⋈ S) = σ_C(R) ⋈ S` **(C가 R만 참조할 때)** → `Suppliers`에 먼저 σ를 적용하고 join

### Example Optimization #2 *(p.8~9)*
- 조건: `x.city = 'Seattle' AND y.pid = 5` (양쪽에 걸림)
- `σ_{C1 and C2}(R ⋈ S) = σ_{C1}(σ_{C2}(R ⋈ S)) = σ_{C1}(R ⋈ σ_{C2}(S)) = σ_{C1}(R) ⋈ σ_{C2}(S)` — 각 조건을 **자기 테이블 쪽으로** 내린다

### Example Optimization #3: Join Reordering *(p.10~12)*
```sql
SELECT * FROM Suppliers x, Supplies y, Parts z
WHERE x.sid = y.sid AND y.pid = z.pid
```
- **Join은 순서를 바꿀 수 있다**: `(R ⋈ S) ⋈ T = R ⋈ (S ⋈ T)`, `R ⋈ S = S ⋈ R`
- 두 가지 logical plan: `(Suppliers ⋈ Supplies) ⋈ Parts` vs `Suppliers ⋈ (Supplies ⋈ Parts)`
- **어느 plan이 더 좋은가?** → `|Suppliers ⋈ Supplies|`와 `|Supplies ⋈ Parts|` 중 **어느 것이 더 작은지**에 달려 있다 *(p.12)*

### Example Optimization #4 *(p.13~15)*
```sql
SELECT * FROM Suppliers x, Supplies y, Parts z
WHERE x.city = 'Seattle' AND z.price > 99 AND x.sid = y.xid AND y.pid = z.pid
```
- 두 plan: `σ_{city='Seattle'}(Suppliers)`를 먼저 join하는 plan vs `σ_{price>99}(Parts)`를 먼저 join하는 plan
- 판단하려면 **`σ_{city='Seattle'}(Suppliers)` vs `σ_{price>99}(Parts)`의 크기 추정**이 필요 *(p.15)*

## 2. Cardinality Estimation 소개 *(p.17~22)*

### 논의 *(p.17)*
- **현대 query optimizer는 rewrite rule에 기반**한다 (SQL Server는 규칙이 약 400개!)
- 규칙을 적용해 **논리적으로 동치인 plan을 많이** 만든다. 어려운 질문: **어느 것을 선택할까?** → 정답은 **비용 추정(cost estimation)**에 달려 있다

### Cost Estimation vs Cardinality Estimation *(p.18)*
- query plan의 비용 추정 과정:
  1. **모든 중간 relation의 cardinality를 추정**
  2. cardinality를 CPU, 메모리 사용 같은 추가 요인을 고려한 **비용으로 변환**
- 이 수업은 더 단순한 문제인 **cardinality estimation**에 집중한다

### 추정의 자원 제약 *(p.19)*
- **주어진 것**: base table의 **통계**(주기적으로 계산, 보통 **sampling** 사용), 들어온 쿼리
- **원하는 것**: 답의 **크기 추정**
- 또한: **매우 빨리** 해야 하고 **메모리를 아주 적게** 써야 한다

### 정의 *(p.20~21)*
- **T(R)** = relation R의 tuple 수
- **V(R, attr)** = R에서 attr의 **서로 다른 값의 개수**. 직관: `GROUP BY attr`이 만드는 그룹 수
- **Selectivity factor θ** = 연산자의 **크기 감소 또는 증가** 비율. 한 연산자가 읽는 데이터의 양은 **이전 연산자가 출력한 양**에 달려 있으므로 이를 추정할 수 있다
- 구체적으로:
  - `T(σ_pred(R)) = θ_pred × T(R)`
  - `T(R ⋈_pred S) = θ_pred × T(R) × T(S)`

### Selectivity factor 유도 *(p.22)*
- **θ를 아는 것이 query의 cardinality(와 비용)를 추정하는 열쇠**
- 어떤 **가정이 성립하면**(예: 값이 균등 분포, 값들이 상관 없음 등) **연산자와 predicate만으로** θ를 유도할 수 있다. 어떻게? → 다음 절

## 3. 가정으로부터 Selectivity Factor 유도 *(p.24~46)*

### 이 수업의 네 가지 가정 *(p.24)*
1. **Uniformity** (균등성)
2. **Independence** (독립성)
3. **Containment of values** (값의 포함)
4. **Preservation of values** (값의 보존)
- "이 가정들은 **결함이 있다**. 하지만 이 수업에서 보게 될 **단순한 쿼리를 추정**할 수 있게 해준다."

### 1) Uniformity Assumption *(p.25~29)*
- 가정: **R의 값들이 균등하게 분포**
- **등호 선택** `σ_{a=x}`의 θ = **1 / V(R, a)** *(p.26)*
- **범위 선택** *(p.27~28)* — `[minA, maxA]`를 a의 최소/최댓값이라 할 때
  - `σ_{a<c}`의 θ = **(c − minA) / (1 + maxA − minA)**
  - `σ_{c1≤a<c2}`의 θ = **(c2 − c1) / (1 + maxA − minA)**
  - 분모에 **+1**을 더하는 이유: 분자는 **[포함, 미포함)** 구간이므로 분모의 범위도 "R의 끝을 지나게" 만들어 맞추기 위해서
- **비판** *(p.29)*: `V(Payroll, Job) = 2`(TA, Prof)라고 해서 **Prof 행이 테이블의 1/2인 것은 아니다** (예시 테이블은 5행 중 TA 3, Prof 2)

### 2) Independence Assumption *(p.30~33)*
- 가정: R.a와 R.b의 값이 **서로 독립** — 즉 R.a와 R.b 사이에 **함수 종속(FD)이 없다**
- **conjunction** `σ_{a=x and b=y}`의 θ = **θ_{a=x} × θ_{b=y}** *(p.31)*
- 균등성도 가정하면 θ = **1/V(R,a) × 1/V(R,b)** *(p.32)*
- **비판** *(p.33)*: `Job → Salary` FD가 없다고 해서 두 값이 서로 **영향을 주지 않는 것은 아니다** (TA는 월급이 낮고 Prof는 높음)

### 3) Containment Assumption *(p.34~43)*
- 가정: **V(R,a) ≤ V(S,b)이면, R의 a 값 집합이 S의 b 값 집합에 포함**된다
- 가장 흔히 적용되는 경우: `⋈_{R.a=S.b}`에서 **b가 S의 PK이고 a가 R의 FK**일 때 *(p.35)*
- **특수 경우: PK/FK join** `R ⋈_{R.fk=S.pk} S` *(p.36~37)*
  - R의 tuple t는 S의 **정확히 1개 tuple**과 join된다 → **`T(R ⋈ S) = T(R)`**
- **일반 경우** `⋈_{R.a=S.b}` *(p.38)* (V(R,a) ≤ V(S,b)만 안다. 꼭 PK/FK는 아님)
  - R의 한 tuple t는 S의 **T(S)/V(S,b)** 개 tuple과 join된다
  - **`T(R ⋈_{R.a=S.b} S) = T(R) × T(S) / V(S,b)`**
- **정보가 부족한 경우** (V(R,a)와 V(S,b)의 대소를 모를 때) *(p.39~42)*
  - 한쪽은 `T(R)·T(S)/V(S,b)`, 반대쪽은 `T(S)·T(R)/V(R,a)`일 수 있다
  - 따라서 **`T(R ⋈_{R.a=S.b} S) = T(R) × T(S) / max(V(R,a), V(S,b))`**
  - 즉 **θ_{R.a=S.b} = 1 / max(V(R,a), V(S,b))**
- **비판** *(p.43)*: **서로소(disjoint)인 값**을 조심해야 한다. 예: FK constraint가 강제되지 않아 Registry에 Payroll에 없는 UserID `007`(Aston Martin)이 있는 경우

### 4) Preservation Assumption *(p.44~46)*
- 가정: c가 `R ⋈_{R.a=S.b} S`의 attribute일 때, **V(R ⋈ S, c)는 V(R, c) 또는 V(S, c)**와 같다 *(p.44)*
  - 덕분에 plan의 **위쪽에서도 c에 대해 아는 정보를 재사용**할 수 있다. 예: `π_{p.name, c}(Payroll p ⋈_{p.userid=r.userid} Registry r)`에서 `V(output, name) = V(Payroll, name)`
- **join이 아닌 연산자에 이 가정을 쓰는 경우를 가끔 볼 수 있는데, 그건 결함이 있다** *(p.45)* — 예: `σ_{p.job='TA'}(Payroll p)` 뒤에는 `V(output, name) ≠ V(Payroll, name)`이고 `V(output, userID) ≠ V(Payroll, userID)`
- **비판** *(p.46)*: join 같은 일부 연산자에는 말이 되지만 **보편적인 가정은 아니다**

## 4. 종합 예제 *(p.48~75)*

### 통계 *(p.49)*
`T(Suppliers) = 1000`, `V(Suppliers, city) = 20`, `V(Suppliers, state) = 10`, `T(Supplies) = 10000`, `V(Supplies, pid) = 2500`. **Supplies는 Suppliers에 대한 FK**를 가지므로 `V(Supplies, sid) ≤ V(Suppliers, sid)`.

### Example #1: join 후에 selection *(p.48~58)*
```sql
SELECT x.sid, y.pid, y.quantity
FROM Suppliers x, Supplies y
WHERE x.sid = y.sid AND x.city = 'Seattle' AND x.state = 'WA' AND y.pid = 5
```
plan: `π(σ_{city='Seattle' and state='WA' and pid=5}(Suppliers x ⋈_{x.sid=y.sid} Supplies y))`
1. **join 크기** *(p.50~52)*: sid에 대한 equijoin이고 **Supplies가 Suppliers로의 FK를 쓰므로** `T(x ⋈ y) = T(Supplies) = 10000`. (또한 θ = 1/max(V(Suppliers,sid), V(Supplies,sid)) 로도 설명)
2. **selection** *(p.53~55)*: **preservation 가정**으로 아래쪽 추정치를 재사용. **independence 가정**으로 conjunction의 selectivity =
   θ_{city=Seattle} × θ_{state=WA} × θ_{pid} = 1/20 × 1/10 × 1/2500
   → 최종 **T < 1**
3. **결함** *(p.56)*: **"하지만 Seattle은 Washington에 있으므로 이 조건들은 독립이 아니다!"** (city와 state는 종속)
4. **수정** *(p.57)*: city와 state는 종속이므로 **min(θ_city, θ_state)** × θ_pid = min(1/20, 1/10) × 1/2500 = **1/20 × 1/2500** 를 쓴다. 그래도 결과는 **T < 1** *(p.58)*

### Example #2: selection을 먼저 내린 plan *(p.59~72)*
plan: `π(σ_{city='Seattle' and state='WA'}(Suppliers x) ⋈_{x.sid=y.sid} σ_{pid=5}(Supplies y))`
1. **왼쪽 σ_{city, state}** *(p.61~63)*
   - independence로 계산하면 1/20 × 1/10 → **T = 5** (1000 × 1/200). **결함**: city와 state는 이미 종속인 열 *(p.62)*
   - 수정: **min(θ_city, θ_state) = min(1/20, 1/10) = 1/20** → **T = 50** *(p.63)*
2. **오른쪽 σ_{pid=5}** *(p.61)*: θ = 1/V(Supplies, pid) = 1/2500 → **T = 4** (10000 / 2500)
3. **join 추정** *(p.64~66)*: sid equijoin이고 Supplies가 FK로 Suppliers를 참조 — **containment가 있을 것 같지만 이제는 가정하면 안 된다** (selection이 한쪽 값을 걸러내서 *(p.65)*). 일단 계속 진행하되 추정치가 결함이 있음을 인정
   - containment 가정: `T = T(left) × T(right) / max(V(left,sid), V(right,sid))` = 50 × 4 / max(…)
4. **Preservation 사용** *(p.67~68)*: `V(left, sid) = V(Suppliers, sid) = 1000`, `V(right, sid) = V(Supplies, sid) = 1000` → 50 × 4 / max(1000, 1000) = **0.2 → T < 1**
5. **Preservation 무시** *(p.69~70)*: **σ 때문에 모든 sid가 남아 있을 수 없다**. `T(left) = 50`인데 `V(left, sid) = 1000`은 불가능. 대신 **`V(left, sid) = T(left)`, `V(right, sid) = T(right)`**로 가정하면 → 50 × 4 / max(50, 4) = **T = 4**
6. **결론** *(p.72)*: **가정에 따라 추정치가 달라진다** (<1 vs =4)

### 추정은 추정일 뿐 *(p.73~75)*
- **Cardinality Estimation은 "추정치(ESTIMATES)"를 만든다** *(p.73)* — 서로 다른 plan(selection을 join 위에 두는 것 vs 아래로 내린 것)이 서로 다른 추정치(T<1, T=4)를 보인다
- 그러나 **추정치로도 트리를 비교하는 데 도움**이 된다 *(p.74~75)*: 왼쪽 tree가 내부 노드가 더 적으므로 아마 더 효율적일 것 (슬라이드 설명은 "Left tree has fewer internal nodes, so probably more efficient than the right tree")
