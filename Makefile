watch: static
	# Run build script
	python3 build.py

static:
	# Copy over static files
	rm -r build/public
	cp -r public build

serve:
	python3 -m http.server --directory build 8080

test:
	python -m unittest

# usage: `make daily title=my-title`
daily:
	./make_daily.sh $(title)
