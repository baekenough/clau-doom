# P-04: RL-GPT — Integrating Reinforcement Learning and LLM

## 서지 정보
| 항목 | 내용 |
|------|------|
| 저자 | Liu et al. |
| 발표 | **NeurIPS 2024 Oral** |
| PDF | [NeurIPS Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/file/31f119089f702e48ecfd138c1bc82c4a-Paper-Conference.pdf) |

## 핵심 아이디어
고수준 계획은 LLM(slow agent), 저수준 행동은 RL(fast agent)의 **2레벨 계층 프레임워크**.

## 아키텍처
```
Slow Agent (LLM) ─── 계획/코드 생성 (비동기, 느림)
    │ 고수준 지시
    ▼
Fast Agent (RL) ─── 실시간 행동 실행 (동기, 빠름)
    │ 환경 피드백
    ▼
환경
```

## clau-doom 매핑

| RL-GPT | clau-doom | 비고 |
|--------|-----------|------|
| Slow Agent (LLM 코딩) | Claude Code / Opus PI | 비동기 분석·계획 |
| Fast Agent (RL) | **RAG + Rust 룰엔진** | RL 대신 RAG로 대체 — 핵심 차별점 |
| 2레벨 분리 | 4레벨 의사결정 계층 | clau-doom이 더 세분화 |

### 핵심 차이: RL → RAG 대체
RL-GPT는 fast agent에 전통적 RL(학습 필요)을 사용. clau-doom은 이를 **RAG 경험 검색**으로 대체하여:
- 학습 시간 0 (기존 전략 문서 즉시 활용)
- 새로운 전략 문서 추가만으로 행동 개선 가능
- 해석 가능성 높음 (어떤 전략 문서가 선택되었는지 추적 가능)

## 프로젝트 적용
- [x] 계층 분리 철학을 4레벨로 확장 적용
- [ ] RL 대비 RAG의 성능/학습효율 비교 실험 설계

---

# P-05: EvoAgent — Automatic Multi-Agent Generation via EA

## 서지 정보
| 항목 | 내용 |
|------|------|
| 저자 | Siyu Yuan, Kaitao Song, Jiangjie Chen, Xu Tan, Dongsheng Li, Deqing Yang |
| 발표 | NAACL 2025 (Long Paper) / arXiv 2024.06 |
| 소속 | Fudan University + Microsoft Research Asia |
| arXiv | [2406.14228](https://arxiv.org/abs/2406.14228) |
| 사이트 | [evo-agent.github.io](https://evo-agent.github.io/) |
| GitHub | [siyuyuan/evoagent](https://github.com/siyuyuan/evoagent) |
| ACL Anthology | [2025.naacl-long.315](https://aclanthology.org/2025.naacl-long.315/) |

## 핵심 아이디어
기존 단일 에이전트 프레임워크를 **진화 알고리즘(mutation, crossover, selection)**으로 자동 확장하여 멀티 에이전트 시스템을 생성. 인간 설계 의존성을 제거.

## 진화 파이프라인
```
초기 에이전트 (개체)
    │
    ├─ Mutation: 에이전트 파라미터/역할 랜덤 변경
    ├─ Crossover: 두 에이전트의 특성 교차
    └─ Selection: 성과 기반 적합도 평가 → 우수 개체 선택
    │
    ▼
다음 세대 에이전트 집단
```

## 실험 결과
- Logic Grid Puzzle, Trivia Creative Writing, Codenames 등에서 기존 프레임워크 대비 유의미한 성능 향상
- MetaGPT, Camel, AutoGen 등 다양한 프레임워크에 적용 가능 (범용성)

## clau-doom 매핑

| EvoAgent | clau-doom | 비고 |
|----------|-----------|------|
| 에이전트 = 개체 | DOOM_PLAYER_{SEQ}.MD = 개체 | MD 파일이 유전체 |
| Mutation | 파라미터 랜덤 조정 | retreat_threshold, play_style 등 |
| Crossover | 상위 2개 MD 전략 조합 | 교차 알고리즘 상세 미정 |
| Selection | 성과 기반 적합도 | kill rate + survival + 실험 채택률 |
| 세대 반복 | 세대 N → N+1 | 동일 |

### 핵심 차이
- EvoAgent는 **NLP 태스크**(텍스트 기반), clau-doom은 **FPS 게임**(실시간 행동)
- EvoAgent의 fitness가 단일 태스크 점수, clau-doom은 다차원 메트릭
- EvoAgent는 에이전트 역할/프롬프트 진화, clau-doom은 전략 파라미터+학습 규칙 진화

## 프로젝트 적용
- [x] MD 교차/변이의 이론적 근거로 활용
- [ ] EvoAgent의 population size / selection pressure 하이퍼파라미터 참조
- [ ] 코드 리포지토리에서 구체적 진화 연산자 구현 참조

---

# P-06: Agent-Pro — Policy-Level Reflection and Optimization

## 서지 정보
| 항목 | 내용 |
|------|------|
| 저자 | Zhang et al. |
| 발표 | ACL 2024 (Long Paper) |
| arXiv | [2402.17574](https://arxiv.org/abs/2402.17574) |
| ACL | [2024.acl-long.292](https://aclanthology.org/2024.acl-long.292/) |

## 핵심 아이디어
단순 행동 수준이 아닌 **정책(policy) 수준**에서 반성(reflection)과 최적화를 수행하는 자가 진화 에이전트. 
- Belief 생성: 현재 상황에 대한 신념 형성
- Reflection: 결과 대비 신념의 적절성 평가
- DFS 기반 정책 최적화: 정책 공간을 깊이 우선 탐색

## clau-doom 매핑
- Agent-Pro의 policy reflection ≈ Opus PI의 세대별 전략 분석
- Belief 생성 ≈ 전략 문서의 situation_tags
- DFS 최적화 ≈ 실험 변수 격리 + A/B 테스트

## 프로젝트 적용
- [ ] 정책 수준 반성 구조를 세대 진화 분석에 반영
- [ ] belief-action 매핑의 명시적 추적 메커니즘 고려

---

# P-07: S-Agents — Self-organizing Agents in Open-ended Environment

## 서지 정보
| 항목 | 내용 |
|------|------|
| 저자 | Chen et al. |
| 발표 | ICLR 2024 Workshop |
| arXiv | [2402.04578](https://arxiv.org/abs/2402.04578) |
| GitHub | [fudan-zvg/S-Agents](https://github.com/fudan-zvg/S-Agents) |

## 핵심 아이디어
오픈 엔디드 환경(Minecraft)에서 에이전트들이 **자기 조직화(self-organizing)**하는 멀티 에이전트 시스템.
- Tree of Agents: 계층적 에이전트 구조
- Hourglass Architecture: 정보 흐름 구조
- Non-obstructive Collaboration: 방해 없는 협업

## clau-doom 관련성 (★☆☆ 낮음)
- 직접 적용보다는 멀티 에이전트 조직화 패턴의 참고 자료
- clau-doom의 에이전트 간 상호작용은 협업보다 **경쟁적 진화**에 가까움
- NATS pub/sub 노하우 공유 설계 시 참조할 수 있는 비방해 협업 패턴

---

# P-08: AlphaEvolve — A Coding Agent for Scientific and Algorithmic Discovery

## 서지 정보
| 항목 | 내용 |
|------|------|
| 저자 | Alexander Novikov et al. (18명) |
| 발표 | Google DeepMind, 2025.05 (White Paper) |
| arXiv | [2506.13131](https://arxiv.org/abs/2506.13131) |
| 블로그 | [deepmind.google/blog/alphaevolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) |
| GitHub (결과) | [google-deepmind/alphaevolve_results](https://github.com/google-deepmind/alphaevolve_results) |
| 오픈소스 구현 | [codelion/openevolve](https://huggingface.co/blog/codelion/openevolve) |

## 핵심 아이디어
LLM 앙상블(Gemini Flash + Pro)이 **코드를 진화적으로 개선**하는 자율 파이프라인. 평가 함수 기반 폐루프로 과학적/공학적 문제를 해결.

## 아키텍처 (4대 컴포넌트)
```
1. Prompt Sampler ─── 이전 프로그램+점수+문제 설명으로 프롬프트 구성
2. LLM Ensemble ─── Gemini Flash(처리량) + Gemini Pro(품질)
3. Evaluator Pool ─── 자동 평가, 점수 산출
4. Program Database ─── MAP-Elites 기반 진화적 선택
```

## 핵심 성과
- 4×4 복소 행렬 곱셈: 48 스칼라 곱셈 (56년 만에 Strassen 알고리즘 개선)
- Google 데이터센터: 0.7% 전역 컴퓨트 자원 절감
- FlashAttention 커널: 23% 학습 속도 향상
- 50+ 수학 문제: 75%에서 SOTA 재발견, 20%에서 초과

## clau-doom 매핑

| AlphaEvolve | clau-doom | 비고 |
|-------------|-----------|------|
| LLM 앙상블 | Claude Code + Ollama | 규모는 다르지만 구조 유사 |
| Program Database (MAP-Elites) | OpenSearch 전략 문서 풀 | 둘 다 다양성+품질 동시 추구 |
| Evaluator Pool | DuckDB 메트릭 + A/B 실험 | AlphaEvolve는 자동, clau-doom은 PI 주도 |
| 진화 루프 | 세대 진화 | 코드 vs MD 파일 |
| Prompt Sampler | PI의 실험 설계 | AlphaEvolve는 자동, clau-doom은 PI 지능 |

### 핵심 교훈
1. **Flash+Pro 앙상블**: 처리량(탐험)과 품질(활용) 밸런스 — clau-doom의 Ollama(경량)+Claude(고품질) 구조와 유사
2. **자동 평가 필수**: "correct by construction" — clau-doom의 DuckDB 메트릭 자동 집계
3. **MAP-Elites**: 단순 최고 성과가 아닌 **다양성 보존** — clau-doom의 전략 문서 풀에 적용 가능
4. **OpenEvolve(오픈소스)**: 구현 참조 가능

## 프로젝트 적용
- [x] 진화 루프 설계의 상위 참조 모델로 활용
- [ ] MAP-Elites 아이디어를 전략 문서 풀 관리에 적용 검토
- [ ] OpenEvolve 코드에서 진화 연산자 구현 패턴 참조
- [ ] 앙상블(경량+고성능) 전략을 Ollama+Claude 분업에 반영
