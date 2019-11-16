local:
	dune build ./main.exe

deploy:
	docker build -t 0install-key-lookup .
	docker save 0install-key-lookup | ssh roscidus.com docker load
