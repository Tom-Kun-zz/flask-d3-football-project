tag_prefix=local
project=football-analysis
version=v1

registry_url=quay.io
registry_password=SECRET
registry_username=USERNAME

build:
	docker build -t $(tag_prefix)-$(project):$(version) .

run:
	docker run -d $(tag_prefix)-$(project):$(version) -p 5000

login:
	@docker login -u="$(registry_username)" -p="$(registry_password)" "$(registry_url)"

push:
	docker tag $(tag_prefix)-$(project):$(version) $(registry_url)/$(registry_username)/$(project):$(version)
	docker push $(registry_url)/$(registry_username)/$(project):$(version)
