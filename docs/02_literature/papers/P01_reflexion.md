# P-01: Reflexion — Language Agents with Verbal Reinforcement Learning

## 서지 정보

| 항목 | 내용 |
|------|------|
| 저자 | Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao |
| 발표 | NeurIPS 2023 (Poster) |
| 소속 | Princeton University |
| arXiv | [2303.11366](https://arxiv.org/abs/2303.11366) |
| GitHub | [noahshinn/reflexion](https://github.com/noahshinn/reflexion) |
| OpenReview | [vAElhFcKW6](https://openreview.net/forum?id=vAElhFcKW6) |
| PDF | [NeurIPS Proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/file/1b44b878bb782e6954cd888628510e90-Paper-Conference.pdf) |

---

## 핵심 아이디어

가중치 업데이트(gradient) 없이 **언어적 피드백(verbal reinforcement)**만으로 LLM 에이전트를 강화하는 프레임워크. 에이전트가 실패 경험을 자연어로 반성(self-reflection)하여 episodic memory buffer에 저장하고, 후속 시도에서 이 반성 텍스트를 컨텍스트로 활용해 더 나은 의사결정을 유도한다.

---

## 아키텍처

```
Actor (Ma) ─→ 환경과 상호작용, 텍스트/액션 생성
     ↑ (반성 텍스트 컨텍스트)
Self-Reflection (Msr) ─→ 실패 원인 분석, 개선 방향 제시
     ↑ (점수/신호)
Evaluator (Me) ─→ Actor 출력 품질 평가, 보상 스코어 계산
```

세 모듈의 반복 루프:
1. Actor가 환경에서 궤적(trajectory) τ 생성
2. Evaluator가 τ에 대한 보상 r 계산
3. r이 부족하면 Self-Reflection이 반성 텍스트 sr 생성
4. sr이 episodic memory에 추가
5. 다음 시도에서 Actor가 memory를 컨텍스트로 활용

---

## 실험 결과

| 태스크 | 벤치마크 | 성과 |
|--------|---------|------|
| 순차 의사결정 | AlfWorld | 반성 추가 시 +8% 성공률 향상 |
| 추론 | HotPotQA | 기존 대비 유의미한 개선 |
| 코드 생성 | HumanEval, MBPP, LeetcodeHardGym | SOTA 달성 |

핵심 발견: self-reflection이 단순 episodic memory보다 8% 절대 성능 향상을 가져옴 → "반성의 품질"이 학습 효율의 핵심 요인.

---

## clau-doom과의 관계

### 직접 차용 가능한 요소

1. **에피소드 회고 → MD 업데이트 패턴**
   - Reflexion: 반성 텍스트를 episodic memory buffer에 저장
   - clau-doom: 에피소드 종료 후 Claude Code가 DuckDB 분석 → DOOM_PLAYER_{SEQ}.MD 업데이트
   - 매핑: `Self-Reflection 모듈 ≈ Claude Code 에피소드 회고`

2. **Evaluator 구조**
   - Reflexion: 환경 피드백(scalar) + 자기 평가(language)
   - clau-doom: DuckDB 메트릭(kill rate, survival_time) + Opus PI의 통계적 판단
   - 매핑: `Evaluator ≈ DuckDB 집계 + Opus 분석`

### 핵심 차이점 (clau-doom이 확장하는 부분)

| 차원 | Reflexion | clau-doom |
|------|-----------|-----------|
| 에이전트 수 | 단일 | 멀티 (N개 동시) |
| 메모리 | episodic text buffer (in-context) | OpenSearch kNN 벡터 검색 + DuckDB |
| 지식 공유 | 없음 | NATS pub/sub로 노하우 브로드캐스트 |
| 진화 | 없음 | 세대별 MD 교차/변이 |
| 실시간성 | LLM 호출 필요 (느림) | RAG+Rust로 100ms 이내 |
| 반성 구조 | 자유 텍스트 | 구조화된 전략 문서 (JSON + 태그) |

### 논문이 제안한 미래 방향 중 clau-doom이 실현하는 것

> "replacing the current episodic memory component of Reflexion with more advanced structures such as vector embedding databases or traditional SQL databases"

→ clau-doom은 정확히 이 방향을 구현: OpenSearch(벡터 DB) + DuckDB(SQL) 조합.

---

## 인용 시 핵심 문장

- "Reflexion agents verbally reflect on task feedback signals, then maintain their own reflective text in an episodic memory buffer to induce better decision-making in subsequent trials."
- "self-reflection is extremely useful to learn complex tasks over a handful of trials"
- 정책을 "agent's memory encoding paired with a choice of LLM parameters"로 매개변수화

---

## 관련 후속 연구

- Self-Refine (2023) — 단일 생성 태스크에서의 반복 개선, Reflexion보다 범위 좁음
- ExpeL (2023) — 경험에서 insight 추출, Reflexion과 상보적
- Agent-Pro (P-06) — 정책 수준 반성으로 확장

---

## 프로젝트 적용 체크리스트

- [x] 에피소드 회고 구조 설계에 반영
- [ ] 반성 텍스트의 구조화 포맷 정의 (Reflexion은 자유 텍스트, clau-doom은 구조화 필요)
- [ ] Evaluator 이중 구조 (자동 메트릭 + LLM 분석) 상세 설계
- [ ] episodic memory → 전략 문서 승격 기준 정의
