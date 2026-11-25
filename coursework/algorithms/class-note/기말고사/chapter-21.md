# Chapter 21 수업노트: Data Structures for Disjoint Sets

*정리 노트: `notes/기말고사/chapter-21.md` / 수업일: 2026-11-25*

## 0. 선수 개념 확인
- **Disjoint**: 두 집합의 교집합이 공집합(A ∩ B = {}), 즉 겹치는 원소가 없다.
- **Connected component**: 무방향 그래프에서 간선을 따라 서로 도달할 수 있는 정점들의 최대 묶음. 정적 그래프는 DFS/BFS로 Θ(V+E)에 구한다. component들은 서로 겹치지 않으므로 disjoint set이다.
- **tail 포인터**: linked list의 마지막 노드를 가리키는 포인터(head는 첫 노드). tail이 있으면 list 뒤에 다른 list를 잇는 게 `A.tail.next = B.head; A.tail = B.tail`로 Θ(1). 없으면 끝까지 걸어가야 해서 O(길이).
- **트리의 높이**: root에서 가장 깊은 leaf까지 가장 긴 경로의 간선 수(최단 아님). 노드 n개 트리의 높이는 일직선 사슬이면 n−1(최대), 균형 잡히면 약 lg n(최소).
- **재귀 깊이**: 노드에서 parent를 따라 root까지 재귀로 올라가면 호출 횟수는 그 노드의 깊이에 비례. 사슬이면 Θ(n), 균형이면 Θ(lg n)이므로 균형 유지가 중요하다.

## 1. Disjoint sets *(p.3~5)*

**Disjoint sets**: 서로 공통 원소가 없는 집합들. 어느 원소든 정확히 한 집합에만 속한다.

- 두 집합: A = {1,2}, B = {3,4} → A ∩ B = {} 이므로 disjoint.
- 여러 집합 S1,…,Sk: 서로 다른 모든 쌍이 disjoint여야 disjoint. 예) S1={1,2,3}, S2={4,8}, S3={5,7}.
- **Collection of disjoint sets**: disjoint set들을 모아 놓은 집합. 예) `{{1,2,3},{4,8},{5,7}}`.
- **Representative(대표 원소)**: collection의 각 집합은 대표 원소를 하나 가지며, 그 원소가 집합의 이름표 역할을 한다. 같은 집합의 어떤 원소든 같은 대표를 가리키므로, 두 원소가 같은 집합인지 대표로 판별한다.
- **Dynamic**: 집합이 시간에 따라 변한다.
  - 새 집합 생성: `{{1,2,3},{4,8},{5,7}}` → `{{1,2,3},{4,8},{5,7},{9}}`.
  - 두 집합 합치기: `{{1,2,3},{4,8},{5,7}}` → `{{1,2,3},{4,8,5,7}}`.
  - 합치기만 있고 **쪼개기는 없다**.
- (확인) `{{1,2},{3},{4,5,6}}`은 집합 3개, 두 집합을 합치면 2개, 합치기만 계속하면 최종 1개. 1개가 되면 합칠 상대가 없어 UNION을 더 못 한다.

## 2. Disjoint-set operations *(p.6~8)*
- **MAKE-SET(x)**: 원소 x 하나만 든 새 집합을 만든다. 대표는 x 자신. 예) MAKE-SET(9): `{{1,2,3},{4,8},{5,7}}` → `{{1,2,3},{4,8},{5,7},{9}}`.
- **UNION(x, y)**: x가 속한 집합과 y가 속한 집합을 합친다. 인자가 집합이 아니라 **원소**라서 내부적으로 "x가 있는 집합"을 찾는 FIND-SET이 필요하다. 예) UNION(1,4): `{{1,2,3},{4,8},{5,7}}` → `{{1,2,3,4,8},{5,7}}`.
- **FIND-SET(x)**: x가 속한 집합의 대표 원소를 돌려준다. 예) FIND-SET(5) → 7.
- 같은 집합인지는 `FIND-SET(x) == FIND-SET(y)`로 판별한다.
- (확인) `{{1,2},{3},{4,5}}`에서 MAKE-SET(6), UNION(2,3), UNION(1,3) 후 → `{{1,2,3},{4,5},{6}}`. UNION(1,3)은 이미 같은 집합이라 아무 일도 일어나지 않는다.

## 3. 문제 정의와 분석 파라미터 *(p.9~11)*
- **문제**: MAKE-SET, UNION, FIND-SET을 지원하며 dynamic disjoint sets의 collection을 유지하는 자료구조를 설계한다.
- 기호: 전체 연산 수 m, MAKE-SET 수 n, UNION 수 u, FIND-SET 수 f. **m = n + u + f**.
- **u ≤ n − 1**: MAKE-SET을 n번 하면 집합이 n개. UNION은 한 번에 집합 수를 1개씩 줄이고, 1개가 남으면 더 UNION할 수 없다.
- **가정**: 처음 n개 연산은 모두 MAKE-SET이다. (원소가 먼저 있어야 UNION/FIND-SET이 가능하고, 분석이 단순해진다.)
- (확인) MAKE-SET 100번 뒤 UNION은 최대 99번. FIND-SET이 50번이면 m = 100 + 99 + 50 = 249.

## 4. 응용: Connected components *(p.13~18)*
- 정적 그래프는 DFS 한 번이면 Θ(V+E). **동적 그래프**(간선이 계속 추가)는 매번 DFS를 다시 돌리면 비효율적이고, disjoint-set을 유지하면 간선 추가 시 UNION 한 번으로 갱신된다.
- 예 *(p.14)*: `{{a,b,c,d},{e,f,g},{h,i},{j}}`에서 간선 (h,j)가 추가되면 `{{a,b,c,d},{e,f,g},{h,i,j}}`. DFS는 Θ(V+E), disjoint-set은 `UNION(h, j)`.

```
CONNECTED-COMPONENTS(G)
1  for each vertex v ∈ G.V
2      MAKE-SET(v)
3  for each edge (u, v) ∈ G.E
4      if FIND-SET(u) ≠ FIND-SET(v)
5          UNION(u, v)
```
- 1~2줄: 모든 정점을 각자 하나짜리 집합으로 시작 (n = |V|).
- 3~5줄: 간선마다 양 끝점의 대표를 비교해 **다른 집합일 때만** UNION.

실행 예시 *(p.16~17)*: 간선 처리 순서 (b,d), (e,g), (a,c), (h,i), (a,b), (e,f), (b,c).

| 처리 간선 | 집합 상태 |
|---|---|
| Initial | {a} {b} {c} {d} {e} {f} {g} {h} {i} {j} |
| (b,d) | {a} {b,d} {c} {e} {f} {g} {h} {i} {j} |
| (e,g) | {a} {b,d} {c} {e,g} {f} {h} {i} {j} |
| (a,c) | {a,c} {b,d} {e,g} {f} {h} {i} {j} |
| (h,i) | {a,c} {b,d} {e,g} {f} {h,i} {j} |
| (a,b) | {a,b,c,d} {e,g} {f} {h,i} {j} |
| (e,f) | {a,b,c,d} {e,f,g} {h,i} {j} |
| (b,c) | {a,b,c,d} {e,f,g} {h,i} {j} (이미 같은 집합) |

```
SAME-COMPONENT(u, v)
1  if FIND-SET(u) == FIND-SET(v)
2      return TRUE
3  else return FALSE
```
- **간선 처리 순서는 중요하지 않다**: 알고리즘은 간선을 아무 순서로나 하나씩 본다. 최종 component 분할은 순서와 무관하게 같고, 어떤 간선에서 UNION이 일어나고 어떤 간선이 스킵되는지 같은 중간 과정만 달라진다. 사전식 등으로 정렬하면 O(E lg E)가 추가로 들 뿐 얻는 게 없다. (순서가 중요한 건 가중치 순 정렬이 필수인 MST의 Kruskal.)
- (확인) 마지막 간선 (b,c)는 b와 c가 이미 같은 집합이라 UNION이 실행되지 않는다. 최종 component는 4개.

## 5. Linked-list representation *(p.20~26)*

**Linked-list representation**: 각 집합을 linked list 하나로 표현하고, list의 첫 객체를 representative로 삼으며, 모든 객체가 representative를 가리키는 포인터를 갖는 구조.

- 집합 하나 = list 하나, 집합의 원소 = list의 객체, 첫 객체 = 대표, 모든 객체가 대표를 직접 가리키는 포인터를 가진다(FIND-SET이 빨라진다). list마다 head, tail 포인터를 유지.
- 예 *(p.22)*: `{{b,c,e,h},{d,f,g}}` → head→c→h→e→b (대표 c), head→f→g→d (대표 f).
- **MAKE-SET(x)**: x 하나짜리 list. **Θ(1)**.
- **FIND-SET(x)**: x의 대표 포인터를 읽는다. **Θ(1)**.
- **UNION(x, y)** *(p.24~25)*: 한 list를 다른 list 뒤에 붙인다. 예) b→c→e 뒤에 f→d를 붙여 b→c→e→f→d.
  1. 앞 list의 tail에 뒤 list를 연결하고 tail 갱신: Θ(1).
  2. 붙여진 list의 **모든 객체**의 대표 포인터를 새 대표로 갱신: Θ(m2) (m2 = 붙여지는 list의 객체 수).
  - 합치면 **UNION은 Θ(m2)**. 앞 list의 대표를 그대로 쓰므로 앞 list 객체들은 포인터를 안 바꿔도 되지만, 붙여지는 쪽 객체들은 옛 대표(이제 대표가 아닌 중간 객체)를 가리키므로 하나씩 고쳐야 FIND-SET이 맞게 나온다. FIND-SET이 Θ(1)인 대가로 UNION에서 갱신 비용을 치르는 구조.
- m개 연산 *(p.26)*:
  - 단순 구현: O(n + f + n²) = O(m + n²) (u < n).
  - **Weighted-union heuristic**: O(n + f + n lg n) = O(m + n lg n).
- (확인) 크기 1짜리에 크기 1000짜리를 붙이면 포인터 1000개 갱신으로 약 1001, 크기 1000짜리에 크기 1짜리를 붙이면 포인터 1개 갱신으로 2. 어느 쪽을 뒤에 붙이느냐로 비용이 갈린다.
- **Weighted-union heuristic**: 합칠 때 항상 **짧은 list를 긴 list 뒤에 붙인다**(각 list가 자기 길이를 들고 있다). 갱신할 포인터가 적은 쪽을 뒤로 보내는 것.
  - 왜 n lg n인가(직관): 객체 x의 포인터가 바뀌는 건 x가 짧은 쪽(뒤)일 때뿐이고, 그때 x가 속한 list 길이는 최소 2배가 된다. 길이가 1에서 시작해 n을 넘을 수 없으니 x의 포인터는 최대 lg n번 바뀌고, 객체 n개면 전체 n lg n. (슬라이드엔 결과만 있고 이건 이해용 직관이다.)
  - 단순 구현은 매번 긴 list를 뒤에 붙이는 최악의 경우가 있어 O(n²)까지 간다.
- (확인) 크기 2, 3인 list를 weighted-union하면 크기 2가 뒤에 붙고 포인터 2개가 바뀐다. 합친 길이는 5가 되어 바뀐 객체들의 list 길이가 2에서 5로 2배 이상이 된다.

## 6. Forest representation *(p.27~34)*

**Forest representation**: 각 집합을 트리 하나로 표현하고, 각 원소는 parent를 가리키며, 트리의 root가 representative인 구조.

- 집합 하나 = 트리 하나(트리들의 모임이 forest). 각 노드는 자기 parent만 가리키고(linked-list처럼 대표를 직접 가리키지 않음), root가 대표.
- 예 *(p.27)*: `{{b,c,e,h},{f,d,g}}` → c가 root(자식 h, e; h의 자식 b), f가 root(자식 d; d의 자식 g).

```
MAKE-SET(x)
1  x.p = x

FIND-SET(x)
1  if x == x.p
2      return x
3  else return FIND-SET(x.p)
```
- **x**는 root를 찾고 싶은 노드(원소), **x.p**는 그 노드의 parent 포인터(객체 필드 접근, `x.rank`와 같은 식).
- **MAKE-SET**: 막 만든 노드는 혼자라 자기가 root이므로 `x.p = x`. "parent가 자기 자신"이 root라는 표시.
- **FIND-SET**: parent를 따라 올라가다 `x == x.p`인 노드를 만나면 반환. 시간은 x의 **깊이**에 비례. UNION을 아무렇게나 하면 트리가 사슬이 되어 FIND-SET이 Θ(n), 균형이 잡히면 lg n.
- (확인) MAKE-SET이 `x.p = x`인 이유는 root를 만들기 위해서(root만 자기 자신을 가리킨다). linked-list에서는 모든 노드가 대표를 직접 가리켰지만 forest에서는 parent만 가리켜서 root까지 타고 올라가야 하므로 FIND-SET이 느려질 수 있다. 그래서 균형 유지가 핵심.

### Union by rank *(p.29~31)*

**Union by rank**: 두 트리를 합칠 때 rank가 작은 root의 트리를 rank가 큰 root 밑에 붙여서 트리가 높아지는 걸 막는 기법.

- **Idea**: 낮은 트리를 높은 트리에 붙인다. 낮은 트리 노드들은 깊이가 1 늘지만 높은 트리의 전체 높이는 그대로이고, 반대로 하면 높은 트리의 모든 노드 깊이가 1씩 는다.
- **rank**: 각 노드가 들고 있는 값으로 그 노드 **높이의 upper bound**. 정확한 높이를 매번 계산하긴 비싸서 근사값으로 유지.
- 두 root의 rank를 비교해 rank가 작은 쪽 root가 큰 쪽 root의 자식이 된다.
- 예 *(p.30)*: c-트리(c→h→b, c→e)와 f-트리(f→d→g)는 높이가 둘 다 2로 **rank가 같다**. LINK에서 `x.p = y`가 되어 c가 f 밑에 붙고 f의 rank가 2에서 3이 된다(결과 높이 3: f→c→h→b).

```
MAKE-SET(x)
1  x.p = x
2  x.rank = 0

UNION(x, y)
1  LINK(FIND-SET(x), FIND-SET(y))

LINK(x, y)
1  if x.rank > y.rank
2      y.p = x
3  else x.p = y
4      if x.rank == y.rank
5          y.rank = y.rank + 1
```
- MAKE-SET: 혼자라 rank = 0.
- UNION: 원소 x, y의 root를 FIND-SET으로 먼저 찾고 두 root를 LINK한다(섹션 2의 "UNION은 내부적으로 FIND-SET이 필요하다"가 실제로 나오는 곳).
- LINK(x, y) (x, y는 root): x.rank > y.rank면 y를 x 밑에(rank 그대로). 아니면 x를 y 밑에 붙이고, 두 rank가 같았다면 y.rank + 1.

| 상황 | 붙이는 방향 | root rank |
|---|---|---|
| x.rank > y.rank | y를 x 밑에 (`y.p = x`) | 그대로 |
| x.rank < y.rank | x를 y 밑에 (`x.p = y`) | 그대로 |
| x.rank == y.rank | 아무 쪽이나 (코드는 `x.p = y`) | +1 |

- rank가 같으면 어느 쪽이 밑으로 가도 되고 결과 높이는 똑같이 1 는다. rank가 다르면 반드시 낮은 쪽이 높은 쪽 밑으로 가야 한다(반대로 하면 정확성은 괜찮아도 균형이 깨져 성능이 나빠짐).
- (확인) rank 2, 2를 LINK하면 root rank 3. rank 3, 1이면 rank 안 늘어난다(3 그대로).
- UNION 자체(LINK)는 포인터 하나를 바꾸는 Θ(1)이고, UNION이 비싸 보이는 건 안에서 부르는 FIND-SET 두 번 때문이다.

### Path compression *(p.32~33)*

**Path compression**: FIND-SET(x)를 하면서 지나온 모든 노드의 parent를 root로 바꿔서 다음 탐색을 빠르게 만드는 기법.

```
FIND-SET(x)
1  if x ≠ x.p          // x가 root가 아니면
2      x.p = FIND-SET(x.p)   // 부모의 root를 찾아 x의 새 parent로 삼는다
3  return x.p          // root일 때는 자기 자신, 아닐 때는 방금 갱신된 root
```
- 재귀가 되돌아오면서 각 노드의 `x.p`를 root로 덮어쓴다. 2번 줄에서 `FIND-SET(x.p)`가 root를 반환하고 그걸 `x.p`에 대입하는 것.
- 예 *(p.33)*: 사슬 a→b→c→d→e→f(root)에서 FIND-SET(a)를 하면 a, b, c, d, e가 전부 f를 직접 가리키는 납작한 트리가 된다. 이번 FIND-SET은 깊이만큼 비싸지만 다음부터는 깊이 1이라 싸다.
- 추적 예: 사슬 a→b→c→d→e(root)에서 FIND-SET(c): c≠c.p(=d)이므로 `c.p = FIND-SET(d)`, d≠d.p(=e)이므로 `d.p = FIND-SET(e)`, e는 root라 e 반환. 돌아오며 `d.p = e`(이미 e라 변화 없음), `c.p = e`(**바뀜**). 실제로 바뀐 노드는 c 하나. 이후 FIND-SET(a)는 a→b→c→e로 3번 올라가고, 이때 a와 b도 e를 직접 가리키게 된다.

### 결론 *(p.34)*
- **union by rank + path compression**을 같이 쓰면 m개 연산의 worst case가 **O(m α(n))**.
- **α(n)**: Ackermann 함수의 역함수로 극도로 느리게 커진다. **α(n) ≤ 4** (현실적인 모든 n). 사실상 연산당 상수 시간.
- 비교: linked-list + weighted-union은 O(m + n lg n), union by rank만 쓰면 O(m lg n), 둘을 합친 forest는 O(m α(n)).
- 두 기법의 역할: union by rank는 트리가 처음부터 높아지지 않게 **예방**하고, path compression은 FIND-SET 때 이미 길어진 경로를 납작하게 **고친다**.

## 7. 종료 점검 (학생 설명)
- linked-list는 FIND-SET이 Θ(1)이고 UNION은 붙인 뒤 뒤쪽 노드의 대표를 바꾸느라 시간이 든다. forest는 FIND-SET이 깊이만큼 비싸질 수 있고, 균형이 안 잡히면 비싸진다.
- union by rank는 트리를 붙일 때 높이가 덜 늘게 하고, path compression은 순회한 노드들이 root를 직접 가리키게 한다.

## Self-study
- union by rank만 쓰면 m개 연산이 O(m lg n)인 이유 (슬라이드 p.29, Exercise 21.4-4).
