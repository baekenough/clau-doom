# clau-doom 문헌 및 자료 수집

> 프로젝트: LLM 기반 멀티 에이전트 진화형 Doom 플레이어
> 수집일: 2026-02-07

---

## 1. 직접 관련 논문 (Core References)

### 1.1 LLM + FPS 게임

| 논문 | 저자 | 발표 | 핵심 내용 | 프로젝트 관련성 |
|------|------|------|-----------|----------------|
| **Will GPT-4 Run DOOM?** | Adrian de Wynter | IEEE Trans. on Games, 2024 | GPT-4(V)로 Doom E1M1 zero-shot 플레이. 스크린샷 → 텍스트 설명 → 행동 결정 파이프라인. 학습/메모리 메커니즘 없음 | 가장 직접적인 선행 연구. clau-doom의 RAG+경험축적이 이 연구의 한계(기억 없음, 학습 없음)를 보완 |

- arXiv: https://arxiv.org/abs/2403.05468
- GitHub: https://github.com/adewynter/Doom
- 주요 한계: GPT-4가 적을 잊어버리고 지나감, 모서리에 끼여 사망, 학습 불가

### 1.2 Verbal Reinforcement / 에피소딕 학습

| 논문 | 저자 | 발표 | 핵심 내용 | 프로젝트 관련성 |
|------|------|------|-----------|----------------|
| **Reflexion** | Shinn et al. | NeurIPS 2023 | 가중치 업데이트 없이 언어적 피드백으로 에이전트 강화. Actor + Evaluator + Self-Reflection 3모듈 구조 | **가장 가까운 선행 연구.** "에피소드 회고 → MD 업데이트" 패턴의 이론적 기반. 차이점: 단일 에이전트 vs clau-doom의 멀티 에이전트+세대 진화 |

- arXiv: https://arxiv.org/abs/2303.11366
- GitHub: https://github.com/noahshinn/reflexion
- 핵심 인사이트: episodic memory buffer에 반성 텍스트를 유지하면 후속 시도에서 더 나은 의사결정 유도

### 1.3 스킬 라이브러리 / 평생 학습

| 논문 | 저자 | 발표 | 핵심 내용 | 프로젝트 관련성 |
|------|------|------|-----------|----------------|
| **Voyager** | Wang et al. | NeurIPS 2023 (TMLR) | Minecraft에서 자동 커리큘럼 + 스킬 라이브러리(실행 가능 코드) + iterative prompting으로 평생 학습 | 스킬 라이브러리 ≈ OpenSearch 전략 문서 풀. 차이: 코드 기반 스킬 vs 상황-전략-결과 문서 RAG 검색 |

- arXiv: https://arxiv.org/abs/2305.16291
- 프로젝트 사이트: https://voyager.minedojo.org/
- GitHub: https://github.com/MineDojo/Voyager
- 핵심 수치: 기존 SOTA 대비 유니크 아이템 3.3x, 이동 거리 2.3x, 테크 트리 15.3x 빠름

### 1.4 LLM + RL 계층 분리

| 논문 | 저자 | 발표 | 핵심 내용 | 프로젝트 관련성 |
|------|------|------|-----------|----------------|
| **RL-GPT** | Liu et al. | NeurIPS 2024 **Oral** | 고수준 계획은 LLM 코딩(slow agent), 저수준 행동은 RL(fast agent)의 2레벨 계층 프레임워크 | "실시간은 RAG, 비동기는 LLM" 계층 분리와 구조적 유사. 차이: 전통적 RL 사용 → clau-doom은 RAG 기반 경험 검색으로 RL 대체 |

- NeurIPS: https://neurips.cc/virtual/2024/oral/97985
- PDF: https://proceedings.neurips.cc/paper_files/paper/2024/file/31f119089f702e48ecfd138c1bc82c4a-Paper-Conference.pdf

### 1.5 에이전트 자가 진화

| 논문 | 저자 | 발표 | 핵심 내용 | 프로젝트 관련성 |
|------|------|------|-----------|----------------|
| **Agent-Pro** | Zhang et al. | ACL 2024 | 정책 수준 반성/최적화로 자가 진화. belief 생성+반성 과정으로 정책 진화. DFS로 정책 최적화 | 에이전트의 policy-level reflection ≈ clau-doom의 세대별 MD 전략 업데이트 |
| **S-Agents** | Chen et al. | ICLR 2024 Workshop | 오픈 엔디드 환경에서 자기 조직화 에이전트. tree of agents, hourglass architecture, non-obstructive collaboration | 멀티 에이전트 조직화 패턴 참조. Minecraft 환경에서 검증 |

- Agent-Pro: https://arxiv.org/abs/2402.17574 / https://aclanthology.org/2024.acl-long.292/
- S-Agents: https://arxiv.org/abs/2402.04578 / https://github.com/fudan-zvg/S-Agents

---

## 2. 서베이 논문 (Surveys)

### 2.1 LLM 게임 에이전트 서베이

| 논문 | 저자 | 최신 버전 | 핵심 내용 |
|------|------|-----------|-----------|
| **A Survey on Large Language Model-Based Game Agents** | Hu et al. | arXiv v4, 2025.11 | 통합 참조 아키텍처로 LLMGA 리뷰. 단일 에이전트: memory, reasoning, perception-action. 멀티 에이전트: communication, organization. 6개 게임 장르별 도전 분류 |

- arXiv: https://arxiv.org/abs/2404.02039
- 논문 큐레이션 GitHub: https://github.com/git-disl/awesome-LLM-game-agent-papers
- **프로젝트 활용**: clau-doom의 에이전트 설계 시 memory/reasoning/action 3요소 프레임워크 참조

### 2.2 LLM 에이전트 메모리 메커니즘

| 논문 | 저자 | 발표 | 핵심 내용 |
|------|------|------|-----------|
| **A Survey on the Memory Mechanism of LLM-based Agents** | — | ACM TOIS, 2025 | LLM 에이전트의 메모리 메커니즘 포괄적 서베이. 메모리 설계/평가 방법론 체계화 |
| **From Storage to Experience: Evolution of LLM Agent Memory** | — | Preprints, 2026.01 | 메모리 진화 3단계: Storage(궤적 보존) → Reflection(궤적 정제) → Experience(궤적 추상화) |

- **프로젝트 활용**: DuckDB(Storage) → Ollama 정제(Reflection) → OpenSearch 전략 문서(Experience)로의 진화 경로와 정확히 매핑

### 2.3 LLM + 진화 알고리즘

| 논문 | 저자 | 발표 | 핵심 내용 |
|------|------|------|-----------|
| **Evolutionary Computation in the Era of LLM: Survey and Roadmap** | Wu et al. | arXiv, 2024.01 | LLM과 진화 알고리즘의 상호작용 종합 정리. LLM을 mutation/crossover 연산자로 사용, 프롬프트 진화 등 |
| **EvoAgent** | Yuan et al. | arXiv, 2024.06 | 기존 에이전트 프레임워크를 진화 알고리즘(mutation, crossover, selection)으로 자동 확장하여 멀티 에이전트 시스템 생성 |

- EvoAgent: https://arxiv.org/abs/2406.14228
- **프로젝트 활용**: clau-doom의 MD 교차/변이 알고리즘 설계 시 직접 참조. LLM을 진화 연산자로 사용하는 패턴

---

## 3. 기술 스택 관련 자료 (Technical Resources)

### 3.1 VizDoom 플랫폼

| 자료 | 내용 |
|------|------|
| **VizDoom 공식 사이트** | https://vizdoom.cs.put.edu.pl/ — 666+ 논문 인용, Farama Foundation 소속(2022~) |
| **VizDoom GitHub** | https://github.com/Farama-Foundation/ViZDoom — Python/C++ API, 커스텀 시나리오 지원 |
| **VizDoom 원논문** | Kempka et al., "ViZDoom: A Doom-based AI Research Platform for Visual Reinforcement Learning," IEEE CIG 2016 |

### 3.2 VizDoom + Deep RL 벤치마크

| 논문 | 발표 | 핵심 내용 |
|------|------|-----------|
| **Gunner: playing FPS game Doom with scalable deep RL** | PeerJ CS, 2025.12 | 모델 프리 RL 알고리즘으로 deathmatch 시나리오 훈련. 기존 DRL 알고리즘들과 비교 |
| **Optimizing RL Agents in First Person Shooter Doom Game** | Khan et al., CAVW 2025 | PPO + reward shaping + curriculum learning으로 VizDoom Deadly Corridor 최적화 |
| **Arnold Agent** | Lample & Chaplot, AAAI 2017 | DRQN + game features network으로 2017 VizDoom Competition Track 2 우승 |
| **F1 Agent** | Wu & Tian, ICLR 2017 | A3C + reward shaping + curriculum design으로 2016 VizDoom Competition Track 1 우승 |

- **프로젝트 활용**: RL 기반 에이전트의 성과를 RAG 기반 에이전트와 비교하는 베이스라인으로 활용

### 3.3 RAG (Retrieval-Augmented Generation)

| 자료 | 내용 |
|------|------|
| **Agentic RAG Survey** | arXiv 2501.09136 (2025.01) — RAG 파이프라인에 autonomous AI agent를 내장하여 동적 검색 전략, 반복 정제, 적응적 응답 생성 |
| **RAG Comprehensive Survey** | arXiv 2506.00054 (2025.05) — RAG 아키텍처, 개선 기법, robustness frontier 종합 정리 |

- **프로젝트 활용**: OpenSearch kNN 검색 + 전략 문서 생명주기 설계 시 adaptive retrieval, self-reflection 패턴 참조

---

## 4. 추가 관련 연구 (Extended References)

### 4.1 게임 내 LLM 에이전트

| 논문 | 발표 | 핵심 내용 | 관련성 |
|------|------|-----------|--------|
| **JARVIS-1** | arXiv 2023.11 | Memory-Augmented Multimodal LLM으로 Minecraft 오픈월드 멀티태스크 | 메모리 증강 패턴 |
| **Ghost in the Minecraft (GITM)** | arXiv 2023.05 | Text-based Knowledge + Memory로 Minecraft 일반 에이전트 | 텍스트 기반 지식 활용 |
| **Generative Agents** | Park et al., 2023 | 인간 행동 시뮬레이션. memory stream + reflection + planning | 에이전트 메모리 아키텍처의 원형 |
| **Cradle** | arXiv 2024.03 | Foundation Agent로 범용 컴퓨터 제어. 게임 포함 | 범용 에이전트 설계 참조 |

### 4.2 멀티 에이전트 협업/조직화

| 논문 | 발표 | 핵심 내용 | 관련성 |
|------|------|-----------|--------|
| **Embodied LLM Agents Learn to Cooperate in Organized Teams** | arXiv 2024.03 | LLM coordinator가 조직 구조를 반복 개선. VirtualHome 환경 | NATS pub/sub 기반 노하우 공유 설계 참조 |
| **Project Sid** | 2024.10 | 다수 에이전트 시뮬레이션으로 AI 문명 구축 시도 | 대규모 멀티 에이전트 시뮬레이션 참조 |

### 4.3 LLM 기반 진화/최적화

| 논문 | 발표 | 핵심 내용 | 관련성 |
|------|------|-----------|--------|
| **Evolving Code with LLM (LLM_GP)** | Genetic Programming & Evolvable Machines, 2024 | LLM을 진화 연산자로 사용. 텍스트 기반 유전체, LLM으로 mutation/crossover | MD 파일 교차/변이 알고리즘의 직접적 참조 |
| **EvoPrompt** | Guo et al. | EA 기반 프롬프트 최적화. GA와 DE로 프롬프트 진화 | 에이전트 MD 프롬프트 진화에 적용 가능 |
| **AlphaEvolve** | Google DeepMind, 2025 | LLM 생성-실행-검증 폐루프로 알고리즘 개선 | PI 주도 실험-검증 루프와 유사 |

---

## 5. 논문 큐레이션 리포지토리

| 리포지토리 | URL | 내용 |
|-----------|-----|------|
| **awesome-LLM-game-agent-papers** | https://github.com/git-disl/awesome-LLM-game-agent-papers | LLM 게임 에이전트 논문 종합 큐레이션 (Game Agents Survey 연계) |
| **LLM-Agents-Papers** | https://github.com/AGI-Edgerunners/LLM-Agents-Papers | LLM 에이전트 관련 논문 종합 (분야별 분류) |
| **Agent-Memory-Paper-List** | https://github.com/Shichun-Liu/Agent-Memory-Paper-List | LLM 에이전트 메모리 메커니즘 논문 리스트 |
| **LLM-Agent-Survey (CoLing 2025)** | https://github.com/xinzhel/LLM-Agent-Survey | LLM 에이전트 서베이 논문 관련 리소스 |

---

## 6. clau-doom 고유 기여점 vs 기존 연구 매핑

| clau-doom 기여점 | 가장 가까운 기존 연구 | 차별점 |
|-----------------|-------------------|--------|
| **RL 없이 RAG + 경험 문서로 행동 개선** | Reflexion (verbal RL) | Reflexion은 episodic memory buffer, clau-doom은 OpenSearch kNN + 전략 문서 풀로 확장. 검증된 전략의 생명주기 관리 포함 |
| **멀티 에이전트 간 지식 공유 + 자연선택** | EvoAgent, S-Agents | EvoAgent는 자동 에이전트 생성, S-Agents는 자기 조직화. clau-doom은 NATS pub/sub 기반 노하우 브로드캐스트 + 세대 진화를 결합 |
| **LLM을 PI로서 실험을 자율 설계/제어** | 해당 없음 (거의 미탐색) | 기존 연구에서 LLM이 실험 전체의 설계-실행-분석-결론까지 자율 수행하는 사례 없음 |
| **FPS 도메인에서 RAG 기반 에이전트** | Will GPT-4 Run DOOM? | GPT-4 연구는 zero-shot, 학습 없음. clau-doom은 경험 축적 + 세대 진화 |
| **MD 파일 기반 에이전트 DNA** | Voyager 스킬 라이브러리 | Voyager는 코드 스킬, clau-doom은 자연어 전략 문서. LLM 교차/변이로 진화 가능 |

---

## 7. 권장 우선순위

### 필독 (Must Read)
1. **Reflexion** — 핵심 이론적 기반
2. **Will GPT-4 Run DOOM?** — 도메인 직접 선행 연구
3. **Voyager** — 스킬 라이브러리 / 평생 학습 아키텍처
4. **RL-GPT** — 계층 분리 프레임워크
5. **LLM Game Agents Survey** — 전체 landscape 파악

### 심화 참고 (Deep Dive)
6. **Agent-Pro** — policy-level reflection 메커니즘
7. **EvoAgent** — 진화 알고리즘으로 멀티 에이전트 생성
8. **Evolutionary Computation in the Era of LLM** — LLM+EA 결합 전략
9. **LLM Agent Memory Survey** — 메모리 아키텍처 설계 참조
10. **Agentic RAG Survey** — RAG 파이프라인 고도화

### 기술 참조 (Technical Reference)
11. **VizDoom 원논문 + 공식 문서** — 게임 환경 API
12. **Gunner / Arnold / F1** — RL 기반 VizDoom 에이전트 베이스라인
13. **S-Agents** — 멀티 에이전트 자기 조직화 패턴
