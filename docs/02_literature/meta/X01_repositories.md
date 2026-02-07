# X-01: 논문 큐레이션 리포지토리 + 추가 참고 논문

## 논문 큐레이션 리포지토리

| 이름 | URL | 내용 | 갱신 상태 |
|------|-----|------|----------|
| awesome-LLM-game-agent-papers | [git-disl](https://github.com/git-disl/awesome-LLM-game-agent-papers) | S-01 서베이 연계, LLM 게임 에이전트 논문 종합 | 활발 |
| LLM-Agents-Papers | [AGI-Edgerunners](https://github.com/AGI-Edgerunners/LLM-Agents-Papers) | LLM 에이전트 전반 (분야별 분류) | 활발 |
| Agent-Memory-Paper-List | [Shichun-Liu](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) | 메모리 메커니즘 특화 | 보통 |
| LLM-Agent-Survey | [xinzhel](https://github.com/xinzhel/LLM-Agent-Survey) | CoLing 2025 서베이 관련 리소스 | 보통 |

---

## 추가 참고 논문 (Extended References)

### 게임 내 LLM 에이전트

| 논문 | 발표 | 핵심 | clau-doom 관련성 |
|------|------|------|-----------------|
| JARVIS-1 | arXiv 2023.11 | Memory-Augmented Multimodal LLM, Minecraft 멀티태스크 | 메모리 증강 패턴 |
| Ghost in the Minecraft (GITM) | arXiv 2023.05 | Text-based Knowledge+Memory, Minecraft 일반 에이전트 | 텍스트 지식 활용 |
| Generative Agents | Park et al., 2023 | 인간 행동 시뮬레이션, memory stream+reflection+planning | 에이전트 메모리 아키텍처 원형 |
| Cradle | arXiv 2024.03 | Foundation Agent, 범용 컴퓨터 제어 (게임 포함) | 범용 설계 참조 |

### 멀티에이전트 협업/조직화

| 논문 | 발표 | 핵심 | clau-doom 관련성 |
|------|------|------|-----------------|
| Embodied LLM Agents Learn to Cooperate in Organized Teams | arXiv 2024.03 | LLM coordinator가 조직 구조를 반복 개선, VirtualHome | NATS 노하우 공유 참조 |
| Project Sid | 2024.10 | 다수 에이전트 시뮬레이션, AI 문명 구축 시도 | 대규모 멀티에이전트 참조 |

### LLM 기반 진화/최적화

| 논문 | 발표 | 핵심 | clau-doom 관련성 |
|------|------|------|-----------------|
| LLM_GP | Genetic Programming & Evolvable Machines, 2024 | LLM을 진화 연산자로 사용, 텍스트 기반 유전체 | MD 교차/변이 직접 참조 |
| EvoPrompt | Guo et al. | EA 기반 프롬프트 최적화, GA와 DE로 프롬프트 진화 | MD 프롬프트 진화 적용 가능 |

---

## 주기적 업데이트 지침

이 문헌 컬렉션은 프로젝트 진행에 따라 갱신 필요:

1. **매 2주**: awesome-LLM-game-agent-papers 리포 확인 → 새 관련 논문 추가
2. **새 기술 결정 시**: 해당 기술 관련 문헌 보강 (예: ONNX 임베딩 채택 시 관련 벤치마크 추가)
3. **실험 결과 분석 시**: 결과와 가장 유사한 기존 연구 비교 논문 추가
4. **논문 작성 시**: Related Work 섹션 구성 기반으로 활용
