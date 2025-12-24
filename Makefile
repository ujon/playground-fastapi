# 변수
PROJECT_ROOT := $(shell pwd)
INFRA_PATH := $(PROJECT_ROOT)/.infra
# - 컨테이너 런타임 확인 [docker, podman]
CONTAINER_RUNTIME ?= $(shell which podman >/dev/null && echo podman || echo docker)
VOLUME_PATH := $(PROJECT_ROOT)/.data

# dotenv 파일 로드
ENV ?= local
ENV_FILE := $(PROJECT_ROOT)/.infra/env/.env.$(ENV)
ifneq (,$(wildcard $(ENV_FILE)))
	include $(ENV_FILE)
	export
endif

help: ## 도움말
	@echo "Command list:"
	@echo "====================="
	@awk 'BEGIN {FS = ":.*?## "; printf "\n"} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Usage Examples:"
	@echo "  make help                   # Show this help"
	@echo "  make env-show               # Show current environment"
	@echo "  make container-up           # Start services"
	@echo "  make ENV=prod container-up  # Start services with production config"
	@echo ""
	@echo "Environments:"
	@echo "  local (default)"

make-volume: ## Volume mount path 생성 (Podman은 폴더 자동생성 안되어 수동 생성 필요)
	@mkdir $(VOLUME_PATH)
	@mkdir $(VOLUME_PATH)/postgresql
	@mkdir $(VOLUME_PATH)/redis

container-up: ## Docker compose 실행
	@echo "🐳 Starting services with $(CONTAINER_RUNTIME) ($(ENV))...$(ENV_FILE) $(PROJECT)"
	@$(CONTAINER_RUNTIME) compose \
	--env-file $(ENV_FILE) \
	-f $(INFRA_PATH)/docker-compose.yml \
	-p $(PROJECT) \
	up -d

container-down: ## Docker compose 중지
	@$(CONTAINER_RUNTIME) compose \
	-f $(INFRA_PATH)/docker-compose.yml \
	-p $(PROJECT) \
	down

container-clean: ## Docker volume mount 삭제
	@rm -rf $(VOLUME_PATH)
	@$(MAKE) make-volume

