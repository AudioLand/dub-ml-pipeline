mac/init:
	brew install flyctl

deploy:
	flyctl deploy --wait-timeout 3000

install:
	pip3 install -r requirements.txt

run:
	uvicorn main:app --host 0.0.0.0 --port 8080 --reload
