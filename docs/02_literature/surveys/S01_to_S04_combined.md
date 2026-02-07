# S-01: A Survey on Large Language Model-Based Game Agents

## 서지 정보
| 항목 | 내용 |
|------|------|
| 저자 | Hu et al. |
| 버전 | arXiv v4, 2025.11 |
| arXiv | [2404.02039](https://arxiv.org/abs/2404.02039) |
| 논문 큐레이션 | [git-disl/awesome-LLM-game-agent-papers](https://github.com/git-disl/awesome-LLM-game-agent-papers) |

## 핵심 내용

### 통합 참조 아키텍처

**단일 에이전트 3요소:**
```
Perception ─→ Memory ─→ Reasoning ─→ Action
              (핵심)
```

**멀티 에이전트 추가 2요소:**
```
Communication (에이전트 간 정보 교환)
Organization (조직 구조, 역할 분담)
```

### 6대 게임 장르별 분류
Adventure, Strategy, Simulation, Social, Puzzle, FPS/Action 각각에서 LLM 에이전트의 도전과 기회 정리.

## clau-doom 활용

| 서베이 요소 | clau-doom 대응 |
|------------|---------------|
| Memory | DuckDB + OpenSearch + MD 파일 (3계층) |
| Reasoning | Rust 룰엔진 + RAG 스코어링 |
| Perception | VizDoom 게임 상태 API 직접 추출 |
| Action | Rust → VizDoom 액션 커맨드 |
| Communication | NATS pub/sub |
| Organization | Opus PI → Claude Code → 에이전트들 (계층적) |

### FPS 장르에서의 도전 과제 (서베이 기준)
- 실시간 의사결정 필수 (LLM 지연 문제)
- 복잡한 3D 환경 인식
- 연속 행동 공간
→ clau-doom이 이 모든 도전을 RAG+Rust로 해결하는 첫 시도

---

# S-02: A Survey on the Memory Mechanism of LLM-based Agents

## 서지 정보
| 항목 | 내용 |
|------|------|
| 발표 | ACM Transactions on Information Systems (TOIS), 2025 |

## 핵심 내용
LLM 에이전트의 메모리 메커니즘을 체계적으로 분류:
- **단기 메모리**: in-context window
- **장기 메모리**: 외부 저장소 (벡터 DB, SQL 등)
- **메모리 연산**: 저장, 검색, 갱신, 삭제, 통합

## clau-doom 활용

| 메모리 유형 | clau-doom 구현 |
|------------|---------------|
| 단기 (작업 메모리) | Rust 에이전트의 현재 틱 상태 |
| 에피소드 메모리 | DuckDB encounters 테이블 |
| 의미 메모리 | OpenSearch 전략 문서 |
| 절차 메모리 | MD 파일의 Learned Rules |

---

# S-03: From Storage to Experience — Evolution of LLM Agent Memory

## 서지 정보
| 항목 | 내용 |
|------|------|
| 발표 | Preprints, 2026.01 |

## 핵심 내용 — 메모리 진화 3단계

```
Stage 1: Storage (궤적 보존)
    ─ 경험을 있는 그대로 저장
    ─ ≈ DuckDB 로우 데이터

Stage 2: Reflection (궤적 정제)
    ─ 저장된 경험에서 패턴 추출, 추상화
    ─ ≈ Ollama 비동기 정제 + Claude Code 에피소드 회고

Stage 3: Experience (궤적 추상화)
    ─ 정제된 지식이 일반화된 경험으로 승격
    ─ ≈ OpenSearch 전략 문서 (검증된 전략)
```

## clau-doom 매핑 — 정확히 3단계와 대응

```
DuckDB (raw logs)     → Storage    : 교전/에피소드 원시 기록
Ollama + Claude Code  → Reflection : 패턴 감지, 회고, 문서 정제
OpenSearch 전략 문서  → Experience : 검증된 전략의 벡터 검색 풀
```

이 서베이가 제시한 3단계 프레임워크는 clau-doom의 데이터 파이프라인을 **이론적으로 정당화**하는 핵심 근거.

---

# S-04: Evolutionary Computation in the Era of Large Language Model

## 서지 정보
| 항목 | 내용 |
|------|------|
| 저자 | Wu et al. |
| 발표 | arXiv, 2024.01 |
| arXiv | [2401.10034](https://arxiv.org/abs/2401.10034) |

## 핵심 내용

LLM과 EA(Evolutionary Algorithms)의 상호작용 4가지 패턴:

### 1. EA가 LLM을 개선
- 프롬프트 진화 (EvoPrompt 등)
- 아키텍처 탐색

### 2. LLM이 EA를 개선
- **LLM을 mutation 연산자로 사용** ← clau-doom 핵심
- **LLM을 crossover 연산자로 사용** ← clau-doom 핵심
- LLM으로 fitness 평가

### 3. LLM+EA 결합
- 공동 최적화
- 진화적 프롬프트 튜닝

### 4. 이론적 연결
- EA의 탐험-활용 밸런스 ≈ LLM의 temperature 조절

## clau-doom 활용

| 서베이 패턴 | clau-doom 적용 |
|------------|---------------|
| LLM as Mutation Operator | Claude Code가 MD 파라미터 랜덤 변경 |
| LLM as Crossover Operator | Claude Code가 상위 2개 MD 전략 조합 |
| Fitness Evaluation | DuckDB 메트릭 (kill rate, survival 등) |
| Exploration-Exploitation | 전체 실험의 30%는 탐험적 실험 |

### 핵심 인사이트
LLM을 진화 연산자로 사용할 때의 장점:
- 도메인 지식을 활용한 **지능적 변이** (랜덤이 아닌 의미 있는 변경)
- 자연어 유전체(MD 파일)에 대한 의미론적 교차/변이 가능
- 전통적 EA보다 적은 세대 수로 수렴 가능

## 프로젝트 적용 체크리스트
- [x] LLM을 mutation/crossover 연산자로 사용하는 이론적 근거 확보
- [ ] 구체적 mutation/crossover 프롬프트 템플릿 설계
- [ ] exploration ratio(30%) 최적화 실험 설계
- [ ] 전통 EA(랜덤 변이) vs LLM 변이 비교 실험 설계
