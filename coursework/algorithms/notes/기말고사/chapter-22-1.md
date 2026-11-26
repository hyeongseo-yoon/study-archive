# Chapter 22-1: Elementary Graph Algorithms — Graphs

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*Slides from Heejin Park, Hanyang Univ. / 파일: `22_Elementary Graph Algorithms_1.pdf` (슬라이드 p.1~35)*

## 0. 개요 *(슬라이드 p.2, p.22)*
- Graphs: Graph basics, Graph representation
- Searching a graph: Breadth-first search, Depth-first search
- Applications of depth-first search: Topological sort

## 1. Graph basics

### 1.1 그래프, 정점, 간선 *(p.3)*
- **Graph** G = (V, E): V는 vertex set, E는 edge set.
- **Vertex (node)**: 원으로 그림. **Edge (link)**: 화살표 또는 선.
- 슬라이드 예시 그래프 (이후 슬라이드에서 계속 사용)
    - Directed graph: 1→2, 2→2(self-loop), 2→4, 2→5, 4→1, 4→5, 5→4, 6→3
    - Undirected graph: 1–2, 1–4, 2–4, 2–5, 4–5, 3–6

### 1.2 Directed graph (digraph) *(p.4)*
- 파란 간선 (2,4)는 vertex 2를 **leave**하고 vertex 4로 **enter**한다.
- 파란 간선은 vertex 2에서 **incident from**, vertex 4로 **incident to**.
- 빨간 간선은 **self-loop** (자기 자신으로 가는 간선).

### 1.3 Undirected graph *(p.5)*
- 간선에 방향이 없다.
- self-loop가 없다.

### 1.4 Adjacency *(p.6)*
- (u, v)가 간선이면 vertex v는 vertex u에 **adjacent**하다.
- Undirected graph: adjacency 관계가 대칭. u가 v에 adjacent면 v도 u에 adjacent.
- Directed graph: 대칭이 아님. 예) 간선 1→2가 있으므로 vertex 2는 1에 adjacent, 하지만 vertex 1은 2에 adjacent하지 않음.

### 1.5 Degree *(p.7~8)*
- Directed graph *(p.7)*: vertex 2의 **out-degree**는 3 (2→2, 2→4, 2→5), **in-degree**는 2 (1→2, 2→2).
    - **degree = out-degree + in-degree**
- Undirected graph *(p.8)*: vertex 2의 **degree**는 3 (1, 4, 5와 연결).

### 1.6 Path *(p.9~10)*
- **Path**: 연속된 간선들의 sequence *(p.9)*
    - <1, 2>, <2, 4>, <4, 5>는 path. 줄여서 <1, 2, 4, 5>
    - <1, 2, 4, 1, 2>는 path (4→1 간선 존재).
    - <1, 2, 4, 2>는 path가 아님 (4→2 간선 없음).
- **Length**: path에 포함된 간선 수. <1, 2, 4, 5>의 length는 3. *(p.10)*
- u에서 v로 가는 path가 있으면 v는 u에서 **reachable**.
    - vertex 5는 vertex 1에서 reachable.
    - vertex 3은 vertex 1에서 reachable하지 않음.

### 1.7 Simple path *(p.11)*
- path의 모든 vertex가 서로 다르면(distinct) **simple**.
- <1, 2, 4, 5>는 simple path, <1, 2, 4, 1, 2>는 simple path 아님.

### 1.8 Cycle과 simple cycle *(p.12)*
- path <v0, v1, …, vk>가 v0 = vk이면 **cycle**.
- cycle <v0, v1, …, vk>에서 v1, v2, …, vk가 distinct면 **simple cycle**.
- <1, 2, 4, 5, 4, 1>은 cycle이지만 simple cycle은 아님 (4가 두 번).
- <1, 2, 4, 1>은 simple cycle.

### 1.9 Acyclic, connected, connected components *(p.13)*
- **Acyclic graph**: cycle이 없는 그래프.
- **Connected graph**: undirected graph에서 모든 vertex 쌍이 path로 연결되어 있으면 connected.
- **Connected components**: undirected graph의 maximally connected한 vertex 부분집합들.
    - 예시 그림 (간선 1–2, 1–5, 2–5, 3–6, vertex 4 고립): {1, 2, 5}, {3, 6}, {4}

### 1.10 Strongly connected *(p.14)*
- **Strongly connected**: directed graph에서 모든 vertex 쌍이 서로 reachable.
- **Strongly connected components**: directed graph의 maximally strongly connected한 vertex 부분집합들.
    - 예시(1.1의 directed graph): {1, 2, 4, 5}, {3}, {6}

### 1.11 Complete graph *(p.15)*
- **Complete graph**: 모든 vertex 쌍이 adjacent한 undirected graph.
- 예시: vertex 2개(a, b) / 3개(a, b, c) / 4개(a, b, c, d)의 complete graph.
- 질문: vertex n개일 때 간선 수는? → n(n − 1) / 2

### 1.12 Bipartite graph *(p.16)*
- **Bipartite graph**: undirected graph G = (V, E)에서 V를 두 집합 V1, V2로 분할할 수 있어서, 모든 간선 (u, v)에 대해 u∈V1, v∈V2 이거나 u∈V2, v∈V1인 그래프.
- 예시: V1 = {a, b}, V2 = {c, d}, 간선 a–c, a–d, b–c, b–d

### 1.13 Forest와 Tree *(p.17)*
- **Forest**: acyclic, undirected graph.
- **Tree**: connected forest = connected, acyclic, undirected graph.
- 질문: forest의 connected component는 tree인가? → 그렇다 (component는 connected이고 forest의 일부라 acyclic).

### 1.14 Dag와 Handshaking lemma *(p.18)*
- **Dag**: directed acyclic graph. 예시: a→b, a→c, a→d, b→d, d→e
- **Handshaking lemma**: G = (V, E)가 undirected graph이면
    - Σ_{v∈V} degree(v) = 2|E|
    - (간선 하나가 양 끝점 degree를 1씩 올리므로)

### 1.15 Tree의 성질 *(p.19)*
Tree(connected, acyclic, undirected graph)에서
- 임의의 두 vertex는 **유일한 simple path**로 연결된다.
- 간선을 하나라도 제거하면 **disconnected**가 된다.
- 간선을 하나라도 추가하면 **cycle**이 생긴다.
- |E| = |V| − 1

### 1.16 Tree의 동치 조건 *(p.20)*
다음은 모두 동치:
1. G는 tree.
2. G는 connected, acyclic, undirected graph.
3. G에서 임의의 두 vertex는 unique simple path로 연결된다.
4. G는 connected이고, 어떤 간선을 제거해도 disconnected가 된다.
5. G는 connected이고, |E| = |V| − 1.
6. G는 acyclic이고, |E| = |V| − 1.
7. G는 acyclic이고, 어떤 간선을 추가해도 cycle이 생긴다.

### 1.17 간선 수의 상한 *(p.21)*
- Directed graph: |E| ≤ |V|² (self-loop 포함)
- Undirected graph: |E| ≤ |V|(|V| − 1) / 2

## 2. Graph representation

### 2.1 두 가지 표현 *(p.23)*
- Adjacency-list representation
- Adjacency-matrix representation

### 2.2 Adjacency-list representation *(p.24~25)*
- |V|개 list의 배열, vertex마다 하나. *(p.24)*
- vertex u의 adjacency list는 u에 adjacent한 모든 vertex를 담는다.
- Directed graph 예시 (간선 1→2, 1→4, 2→5, 3→6, 3→5, 4→2, 5→4, 6→6):

| vertex | adjacency list |
|---|---|
| 1 | 2 → 4 |
| 2 | 5 |
| 3 | 6 → 5 |
| 4 | 2 |
| 5 | 4 |
| 6 | 6 |

- Undirected graph는 directed 버전(양방향)으로 저장한다. *(p.25)*
- 예시 (간선 1–2, 1–5, 2–5, 2–3, 2–4, 3–4, 4–5):

| vertex | adjacency list |
|---|---|
| 1 | 2 → 5 |
| 2 | 1 → 5 → 3 → 4 |
| 3 | 2 → 4 |
| 4 | 2 → 5 → 3 |
| 5 | 4 → 1 → 2 |

- 공간: **Θ(V + E)**

### 2.3 Adjacency-matrix representation *(p.26~28)*
- |V| × |V| 행렬: **Θ(V²)** 공간. *(p.26)*
- entry (i, j)는 간선이 있으면 1, 없으면 0.
- Directed graph 예시 (2.2와 같은 그래프):

```
  1 2 3 4 5 6
1 0 1 0 1 0 0
2 0 0 0 0 1 0
3 0 0 0 0 1 1
4 0 1 0 0 0 0
5 0 0 0 1 0 0
6 0 0 0 0 0 1
```

- Undirected graph 예시 (2.2와 같은 그래프) *(p.27)*:

```
  1 2 3 4 5
1 0 1 0 0 1
2 1 0 1 1 1
3 0 1 0 1 0
4 0 1 1 0 1
5 1 1 0 1 0
```

- Undirected graph의 adjacency matrix는 **main diagonal 기준으로 대칭**이다. → **lower matrix만 저장해도 충분**. *(p.28)*

### 2.4 Adjacency list vs adjacency matrix *(p.29~30)*
- **Storage** *(p.29)*
    - G가 **sparse**하면 adjacency list가 낫다 (|E|가 |V|²보다 훨씬 작으므로).
    - G가 **dense**하면 adjacency matrix가 낫다 (matrix는 entry당 1 bit만 쓰므로).
- **Edge present test** (간선 (i, j)가 있는가?)
    - Adjacency matrix: Θ(1)
    - Adjacency list: O(V)
- **모든 간선 나열/방문** *(p.30)*
    - Adjacency matrix: Θ(V²)
    - Adjacency list: Θ(V + E)

| | Adjacency list | Adjacency matrix |
|---|---|---|
| 공간 | Θ(V + E) | Θ(V²) |
| 간선 존재 확인 | O(V) | Θ(1) |
| 모든 간선 방문 | Θ(V + E) | Θ(V²) |
| 유리한 경우 | sparse | dense |

### 2.5 Weighted graph *(p.31~33)*
- 간선에 weight가 있는 그래프. *(p.31)*
- 예시: a–b 2, a–c 4, b–c 5, b–d 2, b–e 5, c–d 1, d–e 3
- Adjacency list: 각 노드에 (vertex, weight)를 저장 *(p.32)*

| vertex | adjacency list |
|---|---|
| a | (b, 2) → (c, 4) |
| b | (a, 2) → (c, 5) → (d, 2) → (e, 5) |
| c | (a, 4) → (b, 5) → (d, 1) |
| d | (b, 2) → (c, 1) → (e, 3) |
| e | (b, 5) → (d, 3) |

- Adjacency matrix: Θ(V²) 공간, 간선 없으면 ∞, 대각선은 0 *(p.33)*

```
   a  b  c  d  e
a  0  2  4  ∞  ∞
b  2  0  5  2  5
c  4  5  0  1  ∞
d  ∞  2  1  0  3
e  ∞  5  ∞  3  0
```

### 2.6 Transpose *(p.34)*
- 행렬 A = (a_ij)의 **transpose**는 A^T = (a^T_ij), 여기서 a^T_ij = a_ji.
- Undirected graph는 자기 자신의 transpose: A = A^T.

## 3. Self-study *(p.35)*
- Exercise 22.1-3: directed graph의 transpose
- Exercise 22.1-4: multigraph에서 중복 간선을 O(V + E) 시간에 제거
- Exercise 22.1-6: universal sink를 O(V) 시간에 탐지

---

## 수업에서 다룬 섹션
1. 그래프, 정점, 간선 / directed·undirected, self-loop (p.3~5)
2. Adjacency, degree — out-degree, in-degree (p.6~8)
3. Path, length, reachable, simple path (p.9~11)
4. Cycle, simple cycle (p.12)
5. Acyclic, connected, connected components, strongly connected components (p.13~14)
6. Complete graph, bipartite graph (p.15~16)
7. Forest, tree, dag, handshaking lemma (p.17~18)
8. Tree의 성질과 동치 조건, 간선 수 상한 (p.19~21)
9. Adjacency list / adjacency matrix (p.23~28)
10. List vs matrix 비교 — 공간, 간선 존재 확인, 모든 간선 방문 (p.29~30)
11. Weighted graph, transpose (p.31~34)
