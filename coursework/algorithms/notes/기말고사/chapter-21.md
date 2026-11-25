# Chapter 21: Data Structures for Disjoint Sets

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*Slides from Heejin Park, Hanyang Univ. / 파일: `21_Data Structures for Disjoint Sets.pdf` (슬라이드 p.1~34)*

## 0. 개요 *(슬라이드 p.2)*
- Contents: Disjoint-sets, Disjoint-set operations, An application of disjoint-set data structures, Disjoint-set data structures

## 1. Disjoint sets *(p.3~5)*
- **Disjoint**: 두 집합 A, B가 A ∩ B = {} 이면 disjoint. 예) A = {1, 2}, B = {3, 4}
- 집합 S1, S2, …, Sk가 disjoint: 서로 다른 모든 쌍 Si, Sj가 disjoint. 예) S1 = {1,2,3}, S2 = {4,8}, S3 = {5,7}
- **Collection of disjoint sets**: disjoint set들의 집합. 예) {{1,2,3}, {4,8}, {5,7}}
- collection의 각 집합은 **representative member**(대표 원소)를 갖고, 그 원소로 집합이 식별된다.
- **Dynamic disjoint sets**: 집합이 변한다.
    - 새 집합 생성: {{1,2,3},{4,8},{5,7}} → {{1,2,3},{4,8},{5,7},{9}}
    - 두 집합 합침: {{1,2,3},{4,8},{5,7}} → {{1,2,3},{4,8,5,7}}

## 2. Disjoint-set operations *(p.6~8)*
- **MAKE-SET(x)**: 원소 x 하나로 된 집합 생성. MAKE-SET(9): {{1,2,3},{4,8},{5,7}} → {{1,2,3},{4,8},{5,7},{9}}
- **UNION(x, y)**: x를 포함한 집합과 y를 포함한 집합을 합친다. UNION(1,4): {{1,2,3},{4,8},{5,7}} → {{1,2,3,4,8},{5,7}}
- **FIND-SET(x)**: x를 포함한 집합의 representative를 찾는다. FIND-SET(5): 7

## 3. Disjoint-set data structures 문제 정의 *(p.9~11)*
- **Problem**: MAKE-SET, UNION, FIND-SET을 지원하며 dynamic disjoint sets collection을 유지하는 자료구조 개발.
- 실행시간 분석 파라미터: 총 연산 수 m, MAKE-SET 수 n, UNION 수 u, FIND-SET 수 f, **m = n + u + f**
- **u ≤ n − 1**: UNION 한 번마다 집합 수가 1 줄고, n개 집합이 만들어졌으니 n−1번 UNION하면 집합이 1개 남아 더 UNION 불가.
- **가정**: 처음 n개 연산은 MAKE-SET이다.

## 4. 응용: Connected components *(p.13~18)*
- static graph의 CC: DFS, Θ(V+E).
- **dynamic graph**: DFS는 비효율적, disjoint-set 자료구조 유지가 더 효율적.
- 예시 *(p.14)*: {{a,b,c,d},{e,f,g},{h,i},{j}} → {{a,b,c,d},{e,f,g},{h,i,j}}. DFS는 Θ(V+E), disjoint-set은 UNION(h, j) 하나.

### CONNECTED-COMPONENTS *(p.15)*
```
CONNECTED-COMPONENTS(G)
1  for each vertex v ∈ G.V
2      MAKE-SET(v)
3  for each edge (u, v) ∈ G.E
4      if FIND-SET(u) ≠ FIND-SET(v)
5          UNION(u, v)
```

### 실행 예시 *(p.16~17)*
그래프: 정점 a~j, 간선 (b,d), (e,g), (a,c), (h,i), (a,b), (e,f), (b,c)

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

### SAME-COMPONENT *(p.18)*
```
SAME-COMPONENT(u, v)
1  if FIND-SET(u) == FIND-SET(v)
2      return TRUE
3  else return FALSE
```

## 5. Disjoint-set data structures 종류 *(p.20)*
- Linked-list representation
- Forest representation

## 6. Linked-list representation *(p.21~26)*
- 각 집합을 linked list로 표현. 원소들은 list의 객체. **첫 객체가 representative**. **모든 객체가 representative를 가리키는 포인터**를 가진다.
- 예 *(p.22)*: {{b,c,e,h},{d,f,g}} → list 두 개 (head/tail 포인터 유지). 예: head→c→h→e→b, head→f→g→d.

### MAKE-SET, FIND-SET *(p.23)*
- MAKE-SET(x): **Θ(1)**
- FIND-SET(x): **Θ(1)** (representative 포인터를 따라감)

### UNION(x, y) *(p.24~25)*
- 한 list를 다른 list 뒤에 붙인다. (예: b→c→e 뒤에 f→d를 붙여 b→c→e→f→d)
- **Θ(m2)** 시간 (m2 = 붙여지는 list의 객체 수)
    - tail 포인터 변경 및 두 list 연결: Θ(1)
    - 붙여지는 list의 객체들이 가리키는 representative 포인터 변경: Θ(m2)

### m개 연산의 실행시간 *(p.26)*
- **단순 union 구현**: O(n + f + n²) → O(m + n²) (u < n이므로)
- **weighted-union heuristic**: O(n + f + n lg n) → O(m + n lg n)

## 7. Forest representation *(p.27~34)*
- 각 집합을 **tree**로 표현. 각 원소는 **parent를 가리킨다**. 각 tree의 **root가 representative**.
- 예 *(p.27)*: {{b,c,e,h},{f,d,g}} → c가 root(자식 h, e; h의 자식 b), f가 root(자식 d; d의 자식 g).

### MAKE-SET, FIND-SET *(p.28)*
```
MAKE-SET(x)
1  x.p = x

FIND-SET(x)
1  if x == x.p
2      return x
3  else return FIND-SET(x.p)
```

### Union by rank *(p.29~31)*
- **Idea**: 낮은 tree를 높은 tree에 붙인다.
- 각 node가 **rank**(node 높이의 upper bound)를 유지. 두 root의 rank를 비교해 **rank가 작은 root의 tree를 다른 쪽에 붙인다**.
- **Self-study** *(p.29)*: O(m·lg n) 시간, Exercise 21.4-4
- 예 *(p.30)*: c-tree(c,h,e,b)와 f-tree(f,d,g)를 합치면 f가 root가 되고 c-tree가 f 밑으로 붙음.

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

### Path compression *(p.32~33)*
- FIND-SET(x) 중에 지나온 node들의 parent를 **root로 바꾼다**.
```
FIND-SET(x)
1  if x ≠ x.p
2      x.p = FIND-SET(x.p)
3  return x.p
```
- 예 *(p.33)*: a→b→c→d→e→f 로 긴 사슬이던 tree에서 FIND-SET(a)를 하면, 모든 node가 root f를 직접 가리키는 납작한 tree가 된다.

### 결론 *(p.34)*
- union by rank + path compression의 worst case 실행시간: **O(m α(n))**
- **α(n) ≤ 4**: 현실적인 모든 경우에서.

---

## 수업에서 다룬 섹션
1. Disjoint sets — disjoint, collection, representative, dynamic (p.3~5)
2. Disjoint-set operations — MAKE-SET, UNION, FIND-SET (p.6~8)
3. 문제 정의와 분석 파라미터 — m = n + u + f, u ≤ n−1 (p.9~11)
4. 응용: Connected components — CONNECTED-COMPONENTS, SAME-COMPONENT (p.13~18)
5. Linked-list representation — Θ(1) MAKE-SET/FIND-SET, UNION 비용, weighted-union (p.20~26)
6. Forest representation — MAKE-SET/FIND-SET, union by rank, path compression, O(m α(n)) (p.27~34)
