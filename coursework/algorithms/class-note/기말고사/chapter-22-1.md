# Chapter 22-1 수업노트: Elementary Graph Algorithms — Graphs

*정리 노트: `notes/기말고사/chapter-22-1.md` / 수업일: 2026-11-26*

## 0. 선수 개념 확인
- **Θ와 O**: Θ는 상한이자 하한, O는 상한. 이 장에서 **V는 정점 수, E는 간선 수**다. O(V²)는 "정점 수의 제곱"이지 간선 수의 제곱이 아니다.
- **리스트 탐색**: 길이 n인 연결 리스트에서 원소 존재 확인은 최악 **n번**(맨 끝에 있거나 없을 때). 배열 인덱스 접근은 1번. → adjacency list의 간선 존재 확인 O(V)로 이어진다.
- **Partition(분할)**: V를 V1, V2로 나눌 때 V1 ∪ V2 = V, V1 ∩ V2 = ∅. 빠지는 원소도 겹치는 원소도 없다 (21장 disjoint set과 같은 얘기).
- **대칭 행렬**: 모든 i, j에 대해 a_ij = a_ji. main diagonal을 거울로 위아래가 같다.
- **n개 중 2개 고르기**: n(n−1)/2 → complete graph의 간선 수.

## 1. 그래프, 정점, 간선 *(p.3~5)*

**Graph**: 정점 집합 V와 간선 집합 E의 쌍 G = (V, E)로, 대상들 사이의 연결 관계를 나타내는 구조.
- **Vertex(node)**: 그림에서 원 / **Edge(link)**: 화살표나 선

슬라이드에서 계속 쓰는 예시 그래프 *(p.3)*
```
Directed graph                Undirected graph
1 → 2 ↺(self-loop)            1 — 2      3
↑  ↙ ↘                        | /  |     |
4 ⇄ 5        6 → 3            4 —  5     6
```
- Directed: 1→2, 2→2, 2→4, 2→5, 4→1, 4→5, 5→4, 6→3
- Undirected: 1–2, 1–4, 2–4, 2–5, 4–5, 3–6

**Directed graph(digraph)** *(p.4)*: 간선에 방향이 있는 그래프.
- 간선 (2, 4)는 2를 **leave**하고 4로 **enter**한다. = 2에서 **incident from**, 4로 **incident to**.
- **Self-loop**: 자기 자신으로 가는 간선 (2→2).

**Undirected graph** *(p.5)*: 간선에 방향이 없는 그래프. **self-loop가 없다**는 것도 정의에 포함. directed는 self-loop 허용, undirected는 불허 → 이 차이가 간선 수 상한에 영향을 준다.

## 2. Adjacency, degree *(p.6~8)*

**Adjacency**: (u, v)가 간선이면 v가 u에 adjacent하다. *(p.6)*
- Undirected: **대칭**. u가 v에 adjacent면 v도 u에 adjacent.
- Directed: **대칭 아님**. 1→2가 있으니 2는 1에 adjacent, 2→1이 없으니 1은 2에 adjacent하지 않음.
- 헷갈림 주의: "v가 u에 adjacent" = **u에서 v로 가는 간선이 있다**. 화살표가 도착하는 쪽이 주어 자리.

**Degree**: 정점에 붙어 있는 간선의 수. *(p.7~8)*
- Directed *(p.7)*: 나가는 간선 수 **out-degree**, 들어오는 간선 수 **in-degree**, 합이 **degree**.
    - vertex 2: 2→2, 2→4, 2→5 → out-degree 3 / 1→2, 2→2 → in-degree 2 / degree 5
    - self-loop는 나가는 쪽과 들어오는 쪽 **둘 다** 센다.
- Undirected *(p.8)*: 연결된 간선 수. vertex 2는 1, 4, 5와 연결 → degree 3.
- (확인) directed graph의 vertex 4: out-degree 2 (→1, →5), in-degree 2 (2→, 5→), 4에 adjacent한 정점은 **1, 5**. 2→4가 있다고 2가 4에 adjacent한 게 아니다.

## 3. Path, length, reachable, simple path *(p.9~11)*

**Path**: 연속된 간선들의 나열로, 앞 간선이 도착한 정점에서 다음 간선이 출발한다. *(p.9)*
- <1,2>, <2,4>, <4,5>는 path, 줄여서 **<1, 2, 4, 5>**.
- **<1, 2, 4, 1, 2>** 도 path (4→1 있음). 정점이 반복돼도 path.
- **<1, 2, 4, 2>** 는 path 아님 (4→2 없음).

**Length**: path의 **간선 수**. <1, 2, 4, 5>는 length 3 (정점 수 − 1). *(p.10)*

**Reachable**: u에서 v로 가는 path가 있으면 v는 u에서 reachable.
- 5는 1에서 reachable (1→2→5).
- 3은 1에서 reachable하지 않음. 3으로 들어오는 간선은 6→3뿐인데 6으로 들어가는 간선이 없다.

**Simple path**: 모든 정점이 서로 다른 path. <1, 2, 4, 5>는 simple, <1, 2, 4, 1, 2>는 아님. *(p.11)*

## 4. Cycle, simple cycle *(p.12)*

**Cycle**: 시작과 끝 정점이 같은 path. <v0, v1, …, vk>에서 v0 = vk.

**Simple cycle**: cycle에서 **v1, v2, …, vk** 가 전부 distinct. v0 = vk는 당연히 같으니 빼고 **v1부터** 따진다.
- **<1, 2, 4, 5, 4, 1>**: cycle이지만 4가 두 번 → simple cycle 아님.
- **<1, 2, 4, 1>**: v1~vk = 2, 4, 1 다름 → simple cycle.
- (확인) **<2, 2>**: v0 = 2, v1 = 2, k = 1. v0 = vk라 cycle이고, v1~vk = {2}로 중복 없음 → **simple cycle**. self-loop 하나가 길이 1짜리 simple cycle이다. 그래서 self-loop 있는 directed graph는 acyclic이 아니다.

## 5. Acyclic, connected, connected components, strongly connected *(p.13~14)*

**Acyclic graph**: cycle이 하나도 없는 그래프. *(p.13)*

**Connected graph**: **undirected** graph에서 모든 정점 쌍이 path로 이어진 그래프.

**Connected components**: undirected graph를 **maximally connected**한 정점 부분집합들로 나눈 것.
- 슬라이드 그림 (간선 1–2, 1–5, 2–5, 3–6, 정점 4 고립) → **{1, 2, 5}, {3, 6}, {4}**
- **maximally**: 정점을 더 붙이면 connected가 깨지는 데까지 최대로 키운 것. {1, 2}도 connected지만 5를 붙여도 connected라서 component가 아니다.
- 혼자 있는 정점 4도 그 자체로 component.
- component들은 정점 집합의 **partition**이 된다.

**Strongly connected**: **directed** graph에서 모든 정점 쌍이 **서로** reachable (u→v, v→u 둘 다). *(p.14)*

**Strongly connected components(SCC)**: directed graph의 maximally strongly connected한 정점 부분집합들.
- 예시 directed graph: **{1, 2, 4, 5}, {3}, {6}**
    - 1→2→4→1로 1, 2, 4가 서로 돌고, 4⇄5라 5도 합류.
    - 6→3은 있지만 3→6이 없어서 따로. 한 방향으로만 이어지면 SCC가 아니다.

| | undirected | directed |
|---|---|---|
| 전체가 이어짐 | connected | strongly connected |
| 덩어리 | connected components | strongly connected components |

## 6. Complete graph, bipartite graph *(p.15~16)*

**Complete graph**: 모든 정점 쌍이 adjacent한 undirected graph. *(p.15)*
- 예시: 정점 2개(a–b), 3개(삼각형), 4개(모든 쌍 연결).
- 정점 n개일 때 간선 수: 모든 쌍에 간선 하나 → **n(n−1)/2**.

**Bipartite graph**: 정점을 V1, V2로 partition해서 **모든 간선이 V1과 V2 사이에만** 있게 할 수 있는 undirected graph. *(p.16)*
- 예시: V1 = {a, b}, V2 = {c, d}, 간선 a–c, a–d, b–c, b–d. 같은 그룹 안에는 간선이 없다.
- (확인) 정점 3개 complete graph(삼각형)는 bipartite가 **아니다**. 3개를 두 그룹으로 나누면 한쪽에 2개가 들어가고, complete graph라 그 둘 사이에 간선이 있다.
- (슬라이드 밖) 일반적으로 **홀수 길이 cycle이 있으면 bipartite가 아니다**. 삼각형은 길이 3 cycle이라 깨진 것. 22-2 BFS와 연결되는 얘기.

## 7. Forest, tree, dag, handshaking lemma *(p.17~18)*

**Forest**: acyclic한 undirected graph. *(p.17)*

**Tree**: connected한 forest = **connected + acyclic + undirected**.

슬라이드 질문 "forest의 connected component는 tree인가?" → **그렇다.**
- component는 정의상 connected.
- forest 전체에 cycle이 없으니 그 일부인 component에도 없다.
- 그래서 connected + acyclic + undirected = tree. **forest는 tree 여러 개의 모임**.

**Dag**: directed acyclic graph. 예시: a→b, a→c, a→d, b→d, d→e. 22-3 topological sort가 dag 위에서 돈다. *(p.18)*

**Handshaking lemma**: undirected graph에서 모든 정점의 degree 합은 간선 수의 2배.

    Σ degree(v) = 2|E|     (v ∈ V)

간선 (u, v) 하나가 u와 v의 degree를 1씩 올려서 간선마다 2씩 기여한다. 악수 한 번에 두 사람이 각자 하나씩 세는 것.

## 8. Tree의 성질, 동치 조건, 간선 수 상한 *(p.19~21)*

**Tree의 성질** *(p.19)*
1. 임의의 두 정점은 **유일한 simple path**로 이어진다.
2. 간선 하나라도 **빼면 disconnected**.
3. 간선 하나라도 **더하면 cycle 발생**.
4. **|E| = |V| − 1**

직관: tree는 **연결을 유지하면서 간선을 최소로 쓴 상태**. 하나 빼면 끊기고(최소), 하나 더하면 남아서 돌아오는 길(cycle)이 생긴다. 2번과 3번이 양쪽 경계.

**동치 조건** *(p.20)*: 전부 같은 말.
1. G는 tree
2. G는 connected, acyclic, undirected
3. 임의의 두 정점이 unique simple path로 연결
4. connected이고, 어떤 간선을 빼도 disconnected
5. connected이고, |E| = |V| − 1
6. acyclic이고, |E| = |V| − 1
7. acyclic이고, 어떤 간선을 더해도 cycle 발생

패턴: **connected / acyclic / |E| = |V|−1** 중 **아무 두 개**만 있으면 tree (2, 5, 6번). 4, 7번은 "빼면 끊김 / 더하면 cycle" 경계 버전.

(확인) 정점 10개, 간선 9개인 undirected graph는 바로 tree라고 **단정할 수 없다**.
- 주어진 건 |E| = |V| − 1 하나뿐. connected인지 acyclic인지는 모른다.
- 반례 (축소판): 정점 4개, 간선 3개로 삼각형 + 고립 정점 1개. cycle도 있고 connected도 아니다.
- 확인은 **하나만** 하면 된다. 5번(connected + |E|=|V|−1), 6번(acyclic + |E|=|V|−1) 때문에 connected나 acyclic 중 아무거나 하나만 확인하면 tree.
- |E| = |V| − 1이면 connected와 acyclic은 같이 성립하거나 같이 깨진다. cycle 하나에 간선을 하나 "낭비"하면 그만큼 연결할 간선이 모자라 끊긴다. 반례에서 삼각형이 간선을 하나 더 먹어 네 번째 정점까지 갈 간선이 없어진 것.

**간선 수 상한** *(p.21)*
- Directed: **|E| ≤ |V|²**. 모든 순서쌍 (u, v)에 간선 가능 + self-loop (u, u) 허용 → |V| × |V|.
- Undirected: **|E| ≤ |V|(|V|−1)/2**. self-loop 없고 방향 없음 → complete graph의 간선 수.

## 9. Adjacency list / adjacency matrix *(p.23~28)*

그래프를 메모리에 저장하는 두 가지 방법. *(p.23)*

### Adjacency-list representation *(p.24~25)*

**Adjacency list**: 정점마다 하나씩 |V|개의 리스트를 두고, u의 리스트에 u에 adjacent한 정점들을 담는 표현.

Directed 예시 (간선 1→2, 1→4, 2→5, 3→6, 3→5, 4→2, 5→4, 6→6) *(p.24)*
```
1: 2 → 4
2: 5
3: 6 → 5
4: 2
5: 4
6: 6        ← self-loop도 자기 자신을 넣는다
```
리스트에 들어가는 건 **u에서 나가는 간선이 도착하는 정점** (adjacency 방향 그대로).

**Undirected는 양방향 directed로 저장**: 간선 u–v를 u→v, v→u 두 개로 보고 양쪽 리스트에 모두 넣는다. *(p.25)*

예시 (간선 1–2, 1–5, 2–5, 2–3, 2–4, 3–4, 4–5)
```
1: 2 → 5
2: 1 → 5 → 3 → 4
3: 2 → 4
4: 2 → 5 → 3
5: 4 → 1 → 2
```

**공간 Θ(V + E)**: 리스트 머리 배열 |V|칸 + 노드 |E|개(directed) 또는 2|E|개(undirected). 2|E|도 Θ(E). undirected 리스트 길이 합 = degree 합 = 2|E| → handshaking lemma.

### Adjacency-matrix representation *(p.26~28)*

**Adjacency matrix**: |V|×|V| 행렬에서 간선 (i, j)가 있으면 1, 없으면 0. **공간 Θ(V²)**. *(p.26)*

Directed 예시 (위와 같은 그래프)
```
  1 2 3 4 5 6
1 0 1 0 1 0 0
2 0 0 0 0 1 0
3 0 0 0 0 1 1
4 0 1 0 0 0 0
5 0 0 0 1 0 0
6 0 0 0 0 0 1
```
**행 = 출발, 열 = 도착**. i행을 가로로 읽으면 i의 adjacency list와 같다. i행의 1 개수 = out-degree, j열의 1 개수 = in-degree.

Undirected 예시 (위와 같은 그래프) *(p.27)*
```
  1 2 3 4 5
1 0 1 0 0 1
2 1 0 1 1 1
3 0 1 0 1 0
4 0 1 1 0 1
5 1 1 0 1 0
```

Undirected는 간선 u–v가 (u, v), (v, u) 둘 다 1 → **main diagonal 기준 대칭**(a_ij = a_ji) → **lower matrix만 저장해도 충분**. *(p.28)*

(확인) undirected adjacency matrix의 **대각선은 항상 0**. self-loop가 없으니까. 그래서 lower matrix 저장 시 대각선도 뺄 수 있다. directed는 self-loop가 있을 수 있어 a_66 = 1처럼 나올 수 있다.

## 10. Adjacency list vs matrix 비교 *(p.29~30)*

**Storage** *(p.29)*
- **Sparse**(|E|가 |V|²보다 훨씬 작음) → **list 유리**. list는 실제 간선만큼, matrix는 간선이 없어도 V² 칸을 다 잡는다.
- **Dense**(|E|가 |V|²에 가까움) → **matrix 유리**. 둘 다 V² 정도 쓰는데 matrix는 entry 하나를 **1 bit**로 저장할 수 있고, list는 노드마다 정점 번호 + next 포인터가 필요해 더 크다.

**Edge present test: 간선 (i, j)가 있는가?**
- Matrix: **Θ(1)**. a_ij 하나만 보면 된다 (배열 인덱스 접근).
- List: **O(V)**. i의 리스트를 처음부터 훑어 j를 찾는다. 리스트 길이 최대 |V|.

**모든 간선 나열/방문** *(p.30)*
- Matrix: **Θ(V²)**. 간선 수와 상관없이 V² 칸을 전부 봐야 한다.
- List: **Θ(V + E)**. 리스트 머리 |V|개 + 각 리스트 노드 전부.

| | Adjacency list | Adjacency matrix |
|---|---|---|
| 공간 | Θ(V + E) | Θ(V²) |
| 간선 (i, j) 존재 확인 | O(V) | Θ(1) |
| 모든 간선 방문 | Θ(V + E) | Θ(V²) |
| 유리한 그래프 | sparse | dense |

BFS/DFS가 Θ(V + E)인 건 adjacency list를 쓰기 때문. matrix로 하면 Θ(V²).

## 11. Weighted graph, transpose *(p.31~34)*

**Weighted graph**: 각 간선에 가중치(weight)가 붙은 그래프. *(p.31)*
- 예시: a–b 2, a–c 4, b–c 5, b–d 2, b–e 5, c–d 1, d–e 3

**List 표현**: 리스트 노드에 (정점, weight)를 같이 저장. *(p.32)*
```
a: (b,2) → (c,4)
b: (a,2) → (c,5) → (d,2) → (e,5)
c: (a,4) → (b,5) → (d,1)
d: (b,2) → (c,1) → (e,3)
e: (b,5) → (d,3)
```

**Matrix 표현**: entry에 0/1 대신 **weight**. 공간 Θ(V²). *(p.33)*
```
   a  b  c  d  e
a  0  2  4  ∞  ∞
b  2  0  5  2  5
c  4  5  0  1  ∞
d  ∞  2  1  0  3
e  ∞  5  ∞  3  0
```
- **간선 없음 = ∞** (0 아님). weight 0인 간선과 구분해야 한다. "가는 비용이 무한대 = 못 간다".
- **대각선 = 0**. 자기 자신까지 가는 비용은 0.
- 23장 MST, 이후 최단경로에서 계속 쓰이는 형태.

**Transpose**: 행렬 A = (a_ij)의 전치 A^T는 a^T_ij = a_ji, 행과 열을 뒤바꾼 행렬. *(p.34)*
- 그래프 관점: **모든 간선의 방향을 뒤집은 것**. (i, j)가 1이면 이제 (j, i)가 1.
- **Undirected graph는 자기 자신의 transpose**: A = A^T (대칭 행렬).
- 22-3에서 SCC 구할 때 쓰인다.

## 12. 종료 점검 (학생 설명)
- **Connected component**: undirected graph에서 모든 정점 쌍이 path로 이어지는 **maximal** 정점 부분집합. **SCC**: directed graph에서 모든 정점 쌍이 서로 reachable한 **maximal** 정점 부분집합.
    - 처음 답에서 maximal이 빠졌음. {1, 2}는 서로 방문 가능하지만 5를 붙여도 조건이 유지되므로 component가 아니다. 정점을 더 붙이면 조건이 깨지는 데까지 최대로 키워야 component.
- 정점 1000개, 간선 3000개 그래프에서 모든 간선을 훑는 작업 → **list**. matrix는 1000² = 100만 칸을 다 봐야 하지만 list는 1000 + 3000번이면 된다 (sparse 그래프).
