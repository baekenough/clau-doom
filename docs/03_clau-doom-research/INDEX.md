# clau-doom 연구 설계 점검 — 문서 인덱스

> **프로젝트**: clau-doom (LLM 기반 멀티 에이전트 진화형 Doom 플레이어)
> **문서 생성일**: 2026-02-07
> **목적**: 실험 설계 진입 전, 연구 설계 및 문헌/자료 수집의 적절성을 점검하고 보강 사항을 정리

---

## 실행 구조

```
4 Sessions × Agent Teams (병렬) × Sub-agents (세부 작업)

Session 1 ──┐
Session 2 ──┼── 병렬 실행 가능 (독립적)
Session 3 ──┘
Session 4 ────── S1~S3 결과 의존 (문서 통합)
```

---

## 문서 구조

### 메타 문서

| 파일 | 설명 |
|------|------|
| [INDEX.md](INDEX.md) | 이 파일. 전체 문서 인덱스 |
| [meta/REVIEW_SUMMARY.md](meta/REVIEW_SUMMARY.md) | 현 상태 점검 요약 — 양호/보강 필요 판정 |
| [meta/EXECUTION_PLAN.md](meta/EXECUTION_PLAN.md) | 4세션 실행 계획 및 Agent Teams 운용 방안 |
| [meta/DEPENDENCY_MAP.md](meta/DEPENDENCY_MAP.md) | 태스크 간 의존성 맵 |

### Session 1 — 문헌 수집

| 파일 | 태스크 | 우선순위 |
|------|--------|---------|
| [S1-literature/S1-01_EVOLUTION_COLLECTIVE.md](sessions/S1-literature/S1-01_EVOLUTION_COLLECTIVE.md) | 진화/집단지능 문헌 수집 | 🔴 critical |
| [S1-literature/S1-02_RAG_DECISION_MAKING.md](sessions/S1-literature/S1-02_RAG_DECISION_MAKING.md) | RAG for Decision-Making 문헌 수집 | 🔴 critical |
| [S1-literature/S1-03_LLM_AS_SCIENTIST.md](sessions/S1-literature/S1-03_LLM_AS_SCIENTIST.md) | LLM-as-Scientist 문헌 수집 | 🟡 medium |
| [S1-literature/S1-04_DOOM_RL_BASELINE.md](sessions/S1-literature/S1-04_DOOM_RL_BASELINE.md) | Doom RL 베이스라인 문헌 수집 | 🟡 medium |

### Session 2 — 연구 설계 보강

| 파일 | 태스크 | 우선순위 |
|------|--------|---------|
| [S2-design/S2-01_EVAL_BASELINES.md](sessions/S2-design/S2-01_EVAL_BASELINES.md) | 평가 베이스라인 정의 | 🔴 critical |
| [S2-design/S2-02_CORE_ASSUMPTION_ABLATION.md](sessions/S2-design/S2-02_CORE_ASSUMPTION_ABLATION.md) | 핵심 가정 검증 계획 | 🟠 high |
| [S2-design/S2-03_DIVERSITY_METRICS.md](sessions/S2-design/S2-03_DIVERSITY_METRICS.md) | 진화 수렴/다양성 측정 지표 | 🟠 high |
| [S2-design/S2-04_AGENT_TEAMS_WORKFLOW.md](sessions/S2-design/S2-04_AGENT_TEAMS_WORKFLOW.md) | Agent Teams 워크플로 설계 | 🟠 high |

### Session 3 — 기술 검증

| 파일 | 태스크 | 우선순위 |
|------|--------|---------|
| [S3-tech-validation/S3-01_VIZDOOM_POC.md](sessions/S3-tech-validation/S3-01_VIZDOOM_POC.md) | VizDoom 환경 PoC | 🔴 critical |
| [S3-tech-validation/S3-02_RUST_VIZDOOM_BINDING.md](sessions/S3-tech-validation/S3-02_RUST_VIZDOOM_BINDING.md) | Rust ↔ VizDoom 바인딩 방식 결정 | 🟠 high |
| [S3-tech-validation/S3-03_OPENSEARCH_LATENCY.md](sessions/S3-tech-validation/S3-03_OPENSEARCH_LATENCY.md) | OpenSearch kNN 검색 레이턴시 검증 | 🟠 high |
| [S3-tech-validation/S3-04_EMBEDDING_MODEL.md](sessions/S3-tech-validation/S3-04_EMBEDDING_MODEL.md) | 임베딩 모델 선정 | 🟡 medium |

### Session 4 — 문서 통합

| 파일 | 태스크 | 우선순위 | 의존성 |
|------|--------|---------|--------|
| [S4-integration/S4-01_DESIGN_DOC_LITERATURE.md](sessions/S4-integration/S4-01_DESIGN_DOC_LITERATURE.md) | DESIGN.md 문헌 섹션 업데이트 | 🟠 high | S1 전체 |
| [S4-integration/S4-02_CLAUDE_DOC_UNRESOLVED.md](sessions/S4-integration/S4-02_CLAUDE_DOC_UNRESOLVED.md) | CLAUDE.md 미결사항 해소 반영 | 🟠 high | S3 전체 |
| [S4-integration/S4-03_DESIGN_SUPPLEMENT.md](sessions/S4-integration/S4-03_DESIGN_SUPPLEMENT.md) | 연구 설계 보강 사항 문서화 | 🟠 high | S2 전체 |
| [S4-integration/S4-04_CLAUDE_MD.md](sessions/S4-integration/S4-04_CLAUDE_MD.md) | CLAUDE.md 작성 | 🟡 medium | S4-02, S4-03 |

---

## 우선순위 범례

| 기호 | 의미 |
|------|------|
| 🔴 critical | 실험 설계 진입 전 필수 완료 |
| 🟠 high | 연구 품질에 직접 영향 |
| 🟡 medium | 포지셔닝 강화, 후순위 가능 |
