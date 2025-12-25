# 날씨 API 구현

## 사전 요구사항

- python v3.13 (필수)
- make (필수)
- docker | podman (필수)
- redis insight (선택)

## 시작하기

로컬 인프라 생성

```shell
make make-volume # podman 일경우 직접 volume 경로 생성 필요
make container-up
```
환경변수 설정
- `client_api/.env.local` 의 `OPENWEATHERMAP__API_KEY` 값을 채워주세요

애플리케이션 실행

```shell
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# local 환경 실행
python3.13 -m client_api.main
# 또는
make start

# dev 환경 실행
# client_api/.env.dev 파일 필요
ENV=dev python3.13 -m client_api.main
```

API 문서 확인 (Swagger UI)

- http://localhost:8000/docs

## Redis

### Keys

- weather:city:{city}
  - type: string
  - value: Weather(json string)


## 세부사항

- [코드 구조](.docs/structure.md)
- [API 흐름](.docs/api_flow.md)