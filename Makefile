all: deploy

deploy:
	rsync -avP --exclude '/.git' --exclude '/.gitignore' --filter ':- .gitignore' . violet-wlan:~/bustime
