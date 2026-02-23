check:
	uv run ruff format
	uv run ruff check --fix
	uvx pylint tg_auto_test tests --disable=all --enable=C0302 --max-module-lines=200
	uv run vulture tg_auto_test tests vulture_whitelist.py
	npx jscpd --exitCode 1
	uv run pytest -n auto

check-ci:
	uv run ruff format --check
	uv run ruff check
	uvx pylint tg_auto_test tests --disable=all --enable=C0302 --max-module-lines=200
	uv run vulture tg_auto_test tests vulture_whitelist.py
	npx jscpd --exitCode 1
	uv run pytest -n auto