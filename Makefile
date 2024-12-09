# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

# Variables
IMAGE_NAME := torch-python3.11-slim
IMAGE_TAG := latest
DOCKERNAME := raoulgrouls

.PHONY: build run interactive clean help push

.DEFAULT_GOAL := help

help:
	@echo "$(GREEN)Docker Management Commands$(NC)"
	@echo "────────────────────────────"
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make [target]"
	@echo ""
	@echo "$(YELLOW)Targets:$(NC)"
	@awk '/^[a-zA-Z0-9_-]+:/ { \
		helpMessage = match(lastLine, /^# (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 2, RLENGTH); \
			printf "  $(GREEN)%-15s$(NC) %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

# Build the Docker image
build:
	@echo "$(YELLOW)Building Docker image...$(NC)"
	@docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "$(GREEN)Build complete: $(IMAGE_NAME):$(IMAGE_TAG)$(NC)"

# Push image to Docker Hub
push: build
	@echo "$(YELLOW)Pushing to Docker Hub...$(NC)"
	@docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(DOCKERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)
	@docker push $(DOCKERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "$(GREEN)Push complete!$(NC)"

# Run container in detached mode
run: build
	@echo "$(YELLOW)Starting container...$(NC)"
	@docker run -d --name $(IMAGE_NAME) $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "$(GREEN)Container started: $(IMAGE_NAME)$(NC)"

# Start an interactive shell
interactive: build
	@echo "$(YELLOW)Starting interactive shell...$(NC)"
	@docker run -it --rm \
		--entrypoint /bin/bash \
		$(IMAGE_NAME):$(IMAGE_TAG)

# Remove container and image
clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@docker stop $(IMAGE_NAME) 2>/dev/null || true
	@docker rm $(IMAGE_NAME) 2>/dev/null || true
	@docker rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

# Check if Docker daemon is running
check-docker:
	@if ! docker info > /dev/null 2>&1; then \
		echo "$(RED)Error: Docker daemon is not running$(NC)"; \
		exit 1; \
	fi
