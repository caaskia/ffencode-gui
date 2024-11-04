uv venv
source .venv/bin/activate

uv pip compile pyproject.toml -o requirements.txt

uv pip sync requirements.txt --link-mode=copy

# pip freeze > requirements.txt