###############################################################################
#
# Copyright (C) 2025 Tom Kralidis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

DOCKER_COMPOSE_ARGS=--project-name msc-wis2node --file docker-compose.yml --file docker-compose.override.yml

build:
	docker compose $(DOCKER_COMPOSE_ARGS) build

force-build:
	docker compose $(DOCKER_COMPOSE_ARGS) build --no-cache

up:
	docker compose $(DOCKER_COMPOSE_ARGS) up

down:
	docker compose $(DOCKER_COMPOSE_ARGS) down

restart: down up

login:
	docker exec -it msc-wis2node-management /bin/bash

dev:
	docker compose $(DOCKER_COMPOSE_ARGS) --file docker-compose.dev.yml up

reinit-backend:
	docker exec -it msc-wis2node-management sh -c "msc-wis2node setup --force"

logs:
	docker compose $(DOCKER_COMPOSE_ARGS) logs --follow

clean:
	docker system prune -f
	docker volume prune -f

rm:
	docker volume rm $(shell docker volume ls --filter name=msc-wis2node -q)

.PHONY: build up dev login down restart reinit-backend force-build logs rm clean
