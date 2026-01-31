.PHONY: run dev install build test cleanup

install:
	pip install -r requirements.txt
	playwright install chromium

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

build:
	docker build -t animeska-api .

cleanup:
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
