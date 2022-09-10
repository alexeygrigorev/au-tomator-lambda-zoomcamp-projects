build:
	gitbash build.sh

publish: build
	gitbash publish.sh

.PHONY: build publish