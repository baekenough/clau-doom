# P-03: Voyager — An Open-Ended Embodied Agent with Large Language Models

## 서지 정보

| 항목 | 내용 |
|------|------|
| 저자 | Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, Anima Anandkumar |
| 발표 | NeurIPS 2023 / TMLR |
| 소속 | NVIDIA + Caltech + UT Austin + UIUC |
| arXiv | [2305.16291](https://arxiv.org/abs/2305.16291) |
| 사이트 | [voyager.minedojo.org](https://voyager.minedojo.org/) |
| GitHub | [MineDojo/Voyager](https://github.com/MineDojo/Voyager) ⭐6.6k |

---

## 핵심 아이디어

Minecraft에서 인간 개입 없이 **지속적으로 탐험하고, 다양한 스킬을 습득하며, 새로운 발견을 하는** 최초의 LLM 기반 embodied lifelong learning 에이전트. 가중치 파인튜닝 없이 GPT-4 블랙박스 쿼리만으로 동작.

---

## 3대 핵심 컴포넌트

### 1. Automatic Curriculum (자동 커리큘럼)
- GPT-4가 현재 스킬 수준과 월드 상태를 기반으로 다음 태스크 제안
- 에이전트의 인벤토리, 완료/실패 태스크, 주변 환경을 컨텍스트로 제공
- GPT-3.5 기반 Minecraft 위키 QA로 추가 컨텍스트 제공
- **bottom-up 방식**: 나무 채집 → 도구 제작 → 광물 채굴 순서로 자연 진행

### 2. Skill Library (스킬 라이브러리)
- 검증된 스킬을 **실행 가능한 JavaScript 코드**로 저장
- 유사 상황에서 기존 스킬을 **retrieval**하여 재사용
- 스킬은 compositional (조합 가능) — 복잡한 행동을 기존 스킬 조합으로 구성
- **catastrophic forgetting 방지** — 스킬이 영구 저장됨

### 3. Iterative Prompting (반복 프롬프팅)
- 환경 피드백 + 실행 에러 + self-verification을 반복적으로 LLM에 전달
- 코드 생성 → 실행 → 에러 분석 → 코드 수정 반복
- GPT-4의 코드 생성 능력을 최대한 활용

---

## 핵심 수치

| 메트릭 | Voyager | 기존 SOTA | 배수 |
|--------|---------|-----------|------|
| 유니크 아이템 | 3.3x | 1x (AutoGPT 등) | 3.3x |
| 이동 거리 | 2.3x | 1x | 2.3x |
| 돌도구 획득 | 8.5x 빠름 | 1x | 8.5x |
| 철도구 획득 | 6.4x 빠름 | 1x | 6.4x |
| 테크트리 마일스톤 | 15.3x 빠름 | 1x | 15.3x |

Ablation: GPT-3.5로 교체 시 성능 급격히 하락 → 모델 능력이 핵심.

---

## clau-doom과의 관계

### 구조적 매핑

| Voyager 컴포넌트 | clau-doom 대응 | 차이점 |
|-----------------|---------------|--------|
| Skill Library (JS 코드) | OpenSearch 전략 문서 풀 | 코드 vs 자연어 전략 문서 |
| Skill Retrieval (임베딩 검색) | OpenSearch kNN 벡터 검색 | 거의 동일한 메커니즘 |
| Automatic Curriculum | Opus PI 실험 설계 | Voyager는 자기 주도, clau-doom은 PI 주도 |
| Iterative Prompting | 에피소드 회고 + MD 업데이트 | Voyager는 실시간, clau-doom은 비동기 |
| Self-Verification | DuckDB 메트릭 + A/B 실험 | Voyager는 즉시, clau-doom은 통계적 검증 |

### Voyager에서 배울 핵심 교훈

1. **스킬 라이브러리 = 누적 가능한 외부 메모리** — clau-doom의 전략 문서 풀과 동일 철학
2. **compositional skills** — 기본 전략을 조합해 복잡한 전술 구성 가능
3. **catastrophic forgetting 방지** — 외부 저장소에 영구 저장하면 해결
4. **retrieval 품질이 성능을 결정** — 검색 정확도가 곧 에이전트 실력

### 핵심 차이점 (clau-doom이 다른 부분)

| 차원 | Voyager | clau-doom |
|------|---------|-----------|
| 게임 도메인 | Minecraft (오픈월드, 턴 기반에 가까움) | Doom (FPS, 실시간 전투) |
| 실시간성 | LLM 호출이 게임 루프에 포함 (느려도 됨) | 100ms 이내 필수 → RAG+Rust |
| 스킬 형태 | 실행 가능 코드 | 상황-전략-결과 자연어 문서 |
| 에이전트 수 | 단일 | 멀티 + 세대 진화 |
| 검증 방식 | self-verification (1회) | A/B 실험 + 통계적 검증 (30+ 에피소드) |
| 지식 공유 | 없음 | NATS pub/sub 브로드캐스트 |

### 전략 문서 vs 코드 스킬 — 설계 결정 근거

Voyager가 코드를 선택한 이유: Minecraft API가 풍부하고 행동이 이산적이라 코드로 표현 가능.
clau-doom이 자연어 전략 문서를 선택한 이유:
- Doom의 행동 공간이 연속적 (이동+조준+사격 동시)
- 상황 판단의 뉘앙스가 코드보다 자연어로 표현하기 쉬움
- LLM 교차/변이에 자연어가 더 적합
- Rust 룰엔진이 자연어 전략을 실행 가능 행동으로 변환

---

## 프로젝트 적용 체크리스트

- [x] 전략 문서 풀 = Voyager 스킬 라이브러리의 자연어 버전으로 위치 설정
- [x] retrieval 품질 → 에이전트 실력 공식에 반영
- [ ] compositional 전략 설계 — 기본 전술을 조합하는 메타 전략 구조 정의
- [ ] Voyager의 자동 커리큘럼과 clau-doom PI의 실험 설계 비교 분석
- [ ] 스킬 라이브러리 성장 곡선 메트릭을 대시보드에 반영
