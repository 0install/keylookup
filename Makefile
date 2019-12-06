local:
	dune build ./main.exe

deploy:
	docker build -t talex5/0install-key-lookup .
	docker save talex5/0install-key-lookup | ssh roscidus.com docker load
	do-docker-service-update www_key-lookup talex5/0install-key-lookup
