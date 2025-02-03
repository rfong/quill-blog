watch:
	python build.py

serve:
	python3 -m http.server --directory build 8080
