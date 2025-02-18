# usage: `env=DEV make watch`, `env=GH make watch`, etc.
watch: static
	# Run build script
	env=DEV python build.py

build-gh:
	# Rebuild for GH environment
	env=GH python build.py

static:
	# Copy over static files
	rm -rf build/public
	cp -r public build

serve:
	python -m http.server --directory build 8080

test:
	python -m unittest

# usage: `make daily title=my-title`
daily:
	./make_daily.sh $(title)
