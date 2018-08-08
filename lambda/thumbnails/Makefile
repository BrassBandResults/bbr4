PROJECT = bbr-thumbnails
FUNCTION = $(PROJECT)

all: build

.PHONY: clean build deploy

clean:
	rm -rf build

build:
	rm -rf build
	mkdir -p build/site-packages
	zip -r build/$(FUNCTION).zip . -x "*.DS_Store*" "*.git*" "build*" "Makefile" "requirements.txt"
	cp -r $$VIRTUAL_ENV/lib/python3.4/site-packages/* build/site-packages
	cd build/site-packages; zip -g -r ../$(FUNCTION).zip . -x "*__pycache__*"    
