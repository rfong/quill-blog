watch:
	cp -r public build
	python3 build.py

serve:
	python3 -m http.server --directory build 8080
