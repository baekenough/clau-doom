# clau-doom 문헌·자료 마스터 인덱스

> 프로젝트: LLM 기반 멀티 에이전트 진화형 Doom 플레이어
> 최종 갱신: 2026-02-07
> 총 항목: 26건 (논문 16 / 서베이 4 / 기술자료 4 / 방법론 2)

---

## 범례

| 기호 | 의미 |
|------|------|
| ★★★ | 필독 — 프로젝트 핵심 이론 기반 |
| ★★☆ | 심화 — 설계 참조 필수 |
| ★☆☆ | 배경 — 선택적 참고 |
| 🔗 | clau-doom 컴포넌트와 직접 연결 |

---

## A. 핵심 논문 (Core Papers)

| ID | 파일 | 제목 | 중요도 | clau-doom 연결 |
|----|------|------|--------|----------------|
| P-01 | [papers/P01_reflexion.md](papers/P01_reflexion.md) | Reflexion: Language Agents with Verbal Reinforcement Learning | ★★★ | 🔗 에피소드 회고 → MD 업데이트 패턴 |
| P-02 | [papers/P02_gpt4_doom.md](papers/P02_gpt4_doom.md) | Will GPT-4 Run DOOM? | ★★★ | 🔗 유일한 LLM+Doom 선행연구, 한계점이 곧 우리 목표 |
| P-03 | [papers/P03_voyager.md](papers/P03_voyager.md) | Voyager: An Open-Ended Embodied Agent with LLMs | ★★★ | 🔗 스킬 라이브러리 ≈ OpenSearch 전략 문서 풀 |
| P-04 | [papers/P04_rl_gpt.md](papers/P04_rl_gpt.md) | RL-GPT: Integrating RL and LLM for General-Purpose Robotics | ★★★ | 🔗 fast/slow 계층 분리 ≈ RAG/LLM 분리 |
| P-05 | [papers/P05_evoagent.md](papers/P05_evoagent.md) | EvoAgent: Automatic Multi-Agent Generation via EA | ★★☆ | 🔗 진화적 에이전트 생성 → MD 교차/변이 |
| P-06 | [papers/P06_agent_pro.md](papers/P06_agent_pro.md) | Agent-Pro: Activation of Policy-Level Reflection and Optimization | ★★☆ | 🔗 정책 수준 반성 → 세대별 전략 진화 |
| P-07 | [papers/P07_s_agents.md](papers/P07_s_agents.md) | S-Agents: Self-organizing Agents in Open-ended Environment | ★☆☆ | 🔗 멀티에이전트 자기조직화 패턴 |
| P-08 | [papers/P08_alphaevolve.md](papers/P08_alphaevolve.md) | AlphaEvolve: A Coding Agent for Scientific Discovery | ★★☆ | 🔗 LLM+진화 폐루프 ≈ PI 주도 실험-검증 루프 |

## B. 서베이 (Surveys)

| ID | 파일 | 제목 | 중요도 | clau-doom 연결 |
|----|------|------|--------|----------------|
| S-01 | [surveys/S01_llm_game_agents.md](surveys/S01_llm_game_agents.md) | A Survey on LLM-Based Game Agents | ★★★ | 🔗 에이전트 설계 참조 아키텍처 |
| S-02 | [surveys/S02_memory_mechanism.md](surveys/S02_memory_mechanism.md) | A Survey on the Memory Mechanism of LLM-based Agents | ★★☆ | 🔗 메모리 아키텍처 설계 |
| S-03 | [surveys/S03_memory_evolution.md](surveys/S03_memory_evolution.md) | From Storage to Experience: Evolution of LLM Agent Memory | ★★☆ | 🔗 DuckDB→Ollama→OpenSearch 파이프라인 |
| S-04 | [surveys/S04_llm_ea.md](surveys/S04_llm_ea.md) | Evolutionary Computation in the Era of LLM | ★★☆ | 🔗 LLM을 진화 연산자로 사용하는 패턴 |

## C. 기술 자료 (Technical Resources)

| ID | 파일 | 제목 | 중요도 | clau-doom 연결 |
|----|------|------|--------|----------------|
| T-01 | [tech/T01_vizdoom.md](tech/T01_vizdoom.md) | VizDoom 플랫폼 + API | ★★★ | 🔗 게임 환경 자체 |
| T-02 | [tech/T02_rl_baselines.md](tech/T02_rl_baselines.md) | VizDoom RL 베이스라인 (Arnold/F1/Gunner) | ★★☆ | 🔗 RAG 에이전트 vs RL 에이전트 비교 기준 |
| T-03 | [tech/T03_opensearch_knn.md](tech/T03_opensearch_knn.md) | OpenSearch kNN 벡터 검색 | ★★★ | 🔗 실시간 RAG 파이프라인 핵심 인프라 |
| T-04 | [tech/T04_rag_surveys.md](tech/T04_rag_surveys.md) | RAG 서베이 (Agentic RAG / Comprehensive RAG) | ★★☆ | 🔗 전략 문서 검색 파이프라인 고도화 |

## D. 방법론·알고리즘 (Methods)

| ID | 파일 | 제목 | 중요도 | clau-doom 연결 |
|----|------|------|--------|----------------|
| M-01 | [methods/M01_wilson_score.md](methods/M01_wilson_score.md) | Wilson Score Interval (신뢰도 스코어링) | ★★★ | 🔗 Rust 스코어링 엔진의 핵심 알고리즘 |
| M-02 | [methods/M02_md_evolution.md](methods/M02_md_evolution.md) | MD 파일 기반 진화 알고리즘 설계 노트 | ★★☆ | 🔗 세대 진화 교차/변이 구현 |

## E. 메타 (Repositories & Collections)

| ID | 파일 | 내용 |
|----|------|------|
| X-01 | [meta/X01_repositories.md](meta/X01_repositories.md) | 논문 큐레이션 리포지토리 4곳 + 추가 참고 논문 8건 |

---

## 프로젝트 컴포넌트별 문헌 매핑

```
┌─────────────────────────────────────────────────────────────────┐
│ clau-doom 컴포넌트          → 참조 문헌                          │
├─────────────────────────────────────────────────────────────────┤
│ 실시간 의사결정 (Rust)       → P-01, P-04, M-01, T-03           │
│ RAG 파이프라인 (OpenSearch)  → P-03, T-03, T-04, S-02           │
│ 에피소드 회고 (Claude Code)  → P-01, P-06, S-03                 │
│ 세대 진화 (MD 교차/변이)     → P-05, P-08, S-04, M-02           │
│ PI 실험 설계 (Opus)          → P-08 (부분), 미탐색 영역          │
│ 멀티에이전트 지식 공유 (NATS) → P-07, P-05, S-01               │
│ VizDoom 환경                → P-02, T-01, T-02                  │
│ 대시보드 시각화              → (해당 문헌 없음, UI/UX 영역)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## clau-doom 고유 기여점 vs 기존 연구

| # | 기여점 | 가장 가까운 기존 연구 | 격차 |
|---|--------|---------------------|------|
| 1 | RL 없이 RAG+경험문서로 행동 개선 | P-01 Reflexion (episodic buffer) | Reflexion은 텍스트 버퍼, clau-doom은 kNN+생명주기 관리 |
| 2 | 멀티에이전트 지식 공유+자연선택 | P-05 EvoAgent, P-07 S-Agents | EvoAgent는 task-solving 중심, clau-doom은 FPS 도메인+NATS 브로드캐스트 |
| 3 | LLM을 PI로서 실험 자율 설계/제어 | **해당 없음** (거의 미탐색) | clau-doom의 가장 독창적 기여점 |
| 4 | FPS 도메인에서 RAG 기반 에이전트 | P-02 GPT-4 Doom (zero-shot) | GPT-4 Doom은 학습 없음, clau-doom은 경험 축적+세대 진화 |
| 5 | MD 파일 기반 에이전트 DNA | P-03 Voyager (코드 스킬) | Voyager는 실행 코드, clau-doom은 자연어 전략 문서 |
