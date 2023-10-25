mac/init:
	brew install flyctl

deploy:
	flyctl deploy --wait-timeout 3000

run:
	python3 main.py
