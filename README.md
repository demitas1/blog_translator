# Astro blog translator

## Setup

- Install requirements

```
python -m venv venv
. ./venv/bin/activate

pip install -r requirements.txt
```

- Create config json file

```json
{
    "api_key": "your_anthropic_api_key"
}
```

## Usage

- Example

```
python astro_blog_translator.py test/about.en.md --config config/claude.json --output about.ja.md
```


## License

MIT
