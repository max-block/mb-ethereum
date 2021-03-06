set dotenv-load := false
version := `python3 setup.py --version | tr '+' '-'`

clean:
	rm -rf .pytest_cache build dist *.egg-info


dist: clean
    pip-audit
    python3 setup.py sdist bdist_wheel


publish: dist
	twine upload dist/*
	git tag -a 'v{{version}}' -m 'v{{version}}'
	git push origin v{{version}}


ganache:
	ganache-cli -m "question witness snow panther glance repeat village husband chalk lunar pen gift recipe desk salute horse same shield lizard disease step bicycle sunset ski"


ganache-token:
	ganache-cli -m "question witness snow panther glance repeat village husband chalk lunar pen gift recipe desk salute horse same shield lizard disease step bicycle sunset ski" &
	sleep 3
	mb-eth deploy tests/data/conf/deploy.yml -b


ganache-stop:
	pkill -f ganache-cli


dump-help:
    mb-ethereum dump-help > README.txt
