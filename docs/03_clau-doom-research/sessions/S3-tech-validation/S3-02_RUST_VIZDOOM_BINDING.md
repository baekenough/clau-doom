# S3-02: Rust ↔ VizDoom 바인딩 방식 결정

> **세션**: S3 (기술 검증)
> **우선순위**: 🟠 high
> **의존성**: S3-01 부분 완료 (VizDoom 동작 필요)
> **상태**: ⬜ 미시작

---

## 목적

DOOM_ARENA_CLAUDE.md 미결 사항 중 "Rust ↔ VizDoom 바인딩 방식"을 해소한다. Python FFI, gRPC, shared memory 3가지 후보를 PoC로 비교하여 최적 방식을 결정한다.

---

## 후보 비교

### Option A: Python FFI (PyO3/ctypes)

**구조**: Rust → PyO3로 Python 인터프리터 내장 → VizDoom Python API 호출

**장점**: VizDoom Python API 그대로 사용, 추가 인프라 불필요

**단점**: Python GIL 병목, FFI 오버헤드, 디버깅 복잡

**PoC 범위**: PyO3로 VizDoom 게임 상태 읽기 + 액션 전송 왕복 시간 측정

---

### Option B: gRPC

**구조**: Python 글루(gRPC 서버) ↔ Rust 에이전트(gRPC 클라이언트)

**장점**: 언어 분리 깔끔, 기존 설계(에이전트↔오케 gRPC)와 일관, 디버깅 용이

**단점**: 직렬화/역직렬화 오버헤드, 네트워크 레이턴시

**PoC 범위**: proto 정의 → Python gRPC 서버 → Rust gRPC 클라이언트 → 왕복 시간 측정

---

### Option C: Shared Memory

**구조**: Python 글루가 게임 상태를 shared memory에 쓰고, Rust가 직접 읽음

**장점**: 최소 레이턴시, 대량 데이터(screen buffer) 효율적

**단점**: 동기화 복잡, 플랫폼 의존성 (Docker 내부라서 완화됨), 디버깅 어려움

**PoC 범위**: mmap 기반 공유 메모리 → 게임 상태 구조체 쓰기/읽기 → 동기화 + 왕복 시간 측정

---

## 벤치마크 설계

### 측정 항목

| 항목 | 설명 |
|------|------|
| 왕복 레이턴시 | 게임 상태 읽기 → 액션 전송 → 다음 상태 수신 |
| 처리량 | 초당 틱 수 |
| 메모리 사용 | 바인딩 레이어의 추가 메모리 |
| CPU 사용 | 바인딩 레이어의 CPU 오버헤드 |
| 안정성 | 1000 에피소드 연속 실행 시 오류율 |

### 테스트 조건

- VizDoom basic 시나리오
- 1000틱 연속 실행 × 10회 반복
- screen buffer 포함/미포함 각각 측정

### 판단 기준

| 기준 | 가중치 |
|------|--------|
| 왕복 레이턴시 < 5ms | 0.3 |
| 구현/유지보수 복잡도 | 0.3 |
| 기존 아키텍처 정합성 | 0.2 |
| 안정성 | 0.2 |

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 벤치마크 설계, 최종 비교 판정 |
| Sub-agent A | Option A: Python FFI PoC |
| Sub-agent B | Option B: gRPC PoC |
| Sub-agent C | Option C: Shared Memory PoC |

---

## 완료 기준

- [ ] 3개 PoC 각각 게임 상태 읽기 + 액션 전송 동작 확인
- [ ] 벤치마크 수치 테이블 작성
- [ ] 최종 방식 결정 + 근거 기술
- [ ] 결정된 방식의 proto/인터페이스 초안 (gRPC 선택 시)
- [ ] Lead 검수 완료
