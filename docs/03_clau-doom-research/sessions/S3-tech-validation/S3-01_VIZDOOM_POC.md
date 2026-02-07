# S3-01: VizDoom 환경 PoC

> **세션**: S3 (기술 검증)
> **우선순위**: 🔴 critical
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

Docker 컨테이너 내에서 VizDoom + Xvfb + noVNC 스택이 정상 동작하는지 확인한다. 이것이 전체 프로젝트의 기술적 기반이므로, 여기서 실패하면 아키텍처 전체를 재검토해야 한다.

---

## 검증 항목

### 1. VizDoom 기본 동작

- [ ] Docker 컨테이너 내 VizDoom 설치 및 실행
- [ ] basic 시나리오 로드 및 게임 루프 동작
- [ ] Python API로 게임 상태(screen buffer, game variables) 정상 수신
- [ ] 액션 전송 및 게임 반응 확인

### 2. 가상 디스플레이 (Xvfb)

- [ ] Xvfb로 가상 디스플레이 생성
- [ ] VizDoom 윈도우 모드가 Xvfb에 정상 렌더링
- [ ] 해상도 설정 (320x240, 640x480 등) 동작 확인

### 3. noVNC 스트리밍

- [ ] x11vnc → noVNC WebSocket 브릿지 동작
- [ ] 브라우저에서 localhost:6901 접속 → 게임 화면 확인
- [ ] 프레임 레이트 측정 (최소 15fps 목표)
- [ ] 멀티 인스턴스 시 대역폭 측정 (2, 5, 10개 동시)

### 4. 컨테이너 격리

- [ ] 에이전트별 독립 컨테이너에서 VizDoom 인스턴스 실행
- [ ] 컨테이너 간 네트워크 격리 확인
- [ ] 바인드 마운트 볼륨으로 DuckDB 파일 접근 가능

---

## Dockerfile 초안

```dockerfile
FROM ubuntu:24.04

# VizDoom 의존성
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libboost-all-dev libsdl2-dev cmake git \
    xvfb x11vnc novnc websockify \
    && rm -rf /var/lib/apt/lists/*

# VizDoom 설치
RUN pip3 install vizdoom --break-system-packages

# 가상 디스플레이 + VNC 설정
ENV DISPLAY=:99
EXPOSE 6901

# 시작 스크립트
COPY entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
```

### entrypoint.sh 초안

```bash
#!/bin/bash
Xvfb :99 -screen 0 640x480x24 &
sleep 1
x11vnc -display :99 -forever -nopw -rfbport 5900 &
websockify --web /usr/share/novnc 6901 localhost:5900 &
python3 /app/vizdoom_bridge.py
```

---

## 성능 기준

| 항목 | 최소 기준 | 목표 |
|------|----------|------|
| VizDoom 초기화 | < 5초 | < 2초 |
| 게임 틱 처리 | < 20ms/tick | < 10ms/tick |
| noVNC 프레임 레이트 | 15fps | 30fps |
| 컨테이너 메모리 | < 512MB | < 256MB |
| 10개 동시 실행 | 안정 동작 | < 4GB 총 메모리 |

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | PoC 총괄, 성능 기준 판정 |
| Sub-agent A | Dockerfile 작성 + VizDoom 동작 확인 |
| Sub-agent B | noVNC 스트리밍 테스트 + 멀티 인스턴스 벤치마크 |

---

## 완료 기준

- [ ] Dockerfile 빌드 성공
- [ ] VizDoom basic 시나리오 게임 루프 동작 확인
- [ ] 브라우저에서 noVNC로 게임 화면 관전 성공
- [ ] 멀티 인스턴스 (최소 2개) 동시 실행 성공
- [ ] 성능 측정 결과 기록
- [ ] Lead 검수 완료
