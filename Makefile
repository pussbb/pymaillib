BUILDDIR=build
DUTILS=dovecot_utils
DUTILS_BUILD=$(DUTILS)/build

all: clean build_dovecot_utils build

.PHONY: clean 

clean:
	rm -rf $(BUILDDIR)/
	rm -rf $(DUTILS_BUILD)/
	
build_dovecot_utils:
	mkdir -p $(DUTILS_BUILD)/
	cd $(DUTILS_BUILD) && cmake ../ && make
	
build:
	python3 setup.py build_ext -i -f -j 4

dist: clean build_dovecot_utils
	python3 setup.py sdist bdist_wheel
