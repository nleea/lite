domain-test:
	cd domain && python -m pytest -q

backend-test:
	cd backend && python manage.py test

services-test:
	cd services && python -m pytest -q

frontend-build:
	cd frontend && npm run build

lint:
	ruff check domain backend services
	black --check domain backend services

coverage:
	-cd domain && poetry run pytest -q --cov=. --cov-report=xml:coverage.xml
	-cd services && poetry run pytest -q --cov=app --cov-report=xml:coverage.xml
	-cd backend && poetry run coverage run manage.py test && poetry run coverage xml -o coverage.xml


sonar: coverage
	docker run --rm --network host \
		-e SONAR_HOST_URL=$${SONAR_HOST_URL:-http://localhost:9000} \
		-e SONAR_TOKEN=$${SONAR_TOKEN} \
		-v "$$(pwd):/usr/src" sonarsource/sonar-scanner-cli

up:
	docker compose up --build

down:
	docker compose down -v
