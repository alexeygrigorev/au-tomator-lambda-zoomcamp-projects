build:
	gitbash build.sh

publish: build
	gitbash publish.sh

.PHONY: build publish


update_env:
	aws lambda update-function-configuration \
		--function-name="automator-zoomcamp-projects" \
		--environment="Variables={GITHUB_TOKEN=${GITHUB_TOKEN},AIRTABLE_TOKEN=${AIRTABLE_TOKEN},CONFIG_FILE=${CONFIG_FILE}}"