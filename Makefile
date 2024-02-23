.PHONY: build
.DEFAULT_GOAL := help

ROOT_DIR=${PWD}

help:
	@echo "Type: make [rule]. Available options are:"
	@echo ""
	@echo "- help"
	@echo "- format"
	@echo "- build"
	@echo "- run"
	@echo "- dmg"
	@echo ""

build:
	rm -rf build
	rm -rf dist
	pyinstaller "My App.spec"

run:
	open "dist/My App.app"

format:
	black "My App.spec"
	black .

dmg:
	rm -rf "My App.dmg"

	create-dmg \
		--volname "My App" \
		--hdiutil-quiet \
		"My App.dmg" \
		"dist/My App.app"
