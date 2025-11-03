import os, re, sys, json, pathlib, datetime
from dateutil import tz
from openai import OpenAI
import tomli_w
from dotenv import load_dotenv
load_dotenv()  # will read .env from the current working directory


MODEL = "gpt-4.1-mini"

PROMPT = """You are a metadata assistant for a technical blog.
Given a blog post body (no frontmatter), return a concise JSON object with:
- title: <= 70 chars, descriptive, no emojis.
- description: 1–2 sentences, <= 160 chars.
- categories: 1–3 high-level buckets (e.g., ["projects", "tutorials", "data"]).
- tags: 3–10 topical keywords (snake_case or lowercase words), ordered by relevance.
Strict rules:
- Only include fields: title, description, categories, tags.
- Must be valid JSON.
Here is the post body:
"""

JSON_SCHEMA = {
    "name": "post_metadata",
    "schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "categories": {"type": "array", "items": {"type": "string"}},
            "tags": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title", "description", "categories", "tags"]
    }
}

FRONTMATTER_FLAGS = {
    "lang": "en",
    "toc": True,
    "comment": False,
    "copy": True,
    "outdate_alert": False,
    "outdate_alert_days": 120,
    "math": False,
    "mermaid": False,
    "featured": False,
    "reaction": False
}

#FRONTMATTER_IMAGES = ["images/feature-image.png"]


def strip_frontmatter(text: str) -> str:
    m = re.match(r"^\+\+\+[\s\S]*?\+\+\+\s*", text, re.MULTILINE)
    if m:
        return text[m.end():].lstrip()
    m = re.match(r"^---[\s\S]*?---\s*", text, re.MULTILINE)
    if m:
        return text[m.end():].lstrip()
    return text


def extract_existing_date(text: str):
    m = re.search(r'^date\s*=\s*"(.*?)"', text, re.MULTILINE)
    return m.group(1) if m else None


def build_frontmatter_toml(meta: dict, existing_date: str | None = None) -> str:
    if existing_date:
        date_str = existing_date
    else:
        now = datetime.datetime.now(tz=tz.gettz("America/New_York"))
        date_str = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        date_str = date_str[:-2] + ":" + date_str[-2:]  # -0500 → -05:00

    data = {
        "title": meta["title"],
        "description": meta["description"],
        "tags": meta["tags"],
        #"images": FRONTMATTER_IMAGES,
        "date": date_str,
        "categories": meta["categories"],
        "series": [],
        "extra": FRONTMATTER_FLAGS,
    }

    toml_str = tomli_w.dumps(data)
    return f"+++\n{toml_str}+++\n\n"

def process_file(client, md_path: pathlib.Path):
    text = md_path.read_text(encoding="utf-8")
    body = strip_frontmatter(text).strip()
    if not body:
        print(f"⚠️ Skipping empty body: {md_path}")
        return

    SYSTEM_MSG = (
        "You are a metadata assistant for a technical blog. "
        "Return ONLY valid JSON with keys: title, description, categories, tags. "
        "title<=70 chars; description 1–2 sentences<=160 chars; "
        "categories 1–3 items; tags 3–10 lowercase keywords."
    )

    chat = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": f"Here is the post body:\n\n{body}"}
        ],
        temperature=0.2,
    )

    raw = chat.choices[0].message.content
    try:
        meta = json.loads(raw)
    except Exception as e:
        print(f"❌ Could not parse JSON for {md_path.name}: {e}")
        print("Raw:", raw)
        return

    for k in ["title", "description", "categories", "tags"]:
        if k not in meta:
            print(f"❌ Missing '{k}' in model output for {md_path.name}")
            print("Raw:", raw)
            return

    existing_date = extract_existing_date(text)
    fm = build_frontmatter_toml(meta, existing_date)
    md_path.write_text(fm + body + "\n", encoding="utf-8")
    print(f"✅ Updated: {md_path}")



#def process_file(client, md_path: pathlib.Path):
#    text = md_path.read_text(encoding="utf-8")
#    body = strip_frontmatter(text).strip()
#    if not body:
#        print(f"⚠️ Skipping empty body: {md_path}")
#        return
#
#    resp = client.responses.create(
#        model=MODEL,
#        input=PROMPT + body,
#        response_format={"type": "json_schema", "json_schema": JSON_SCHEMA},
#    )
#
#    raw = resp.output_text
#    try:
#        meta = json.loads(raw)
#    except Exception:
#        meta = getattr(resp, "parsed", None) or {}
#
#    if not all(k in meta for k in ["title", "description", "categories", "tags"]):
#        print(f"❌ Model returned incomplete metadata for {md_path.name}")
#        print("Raw:", raw)
#        return
#
#    existing_date = extract_existing_date(text)
#    fm = build_frontmatter_toml(meta, existing_date)
#    new_text = fm + body + "\n"
#    md_path.write_text(new_text, encoding="utf-8")
#    print(f"✅ Updated: {md_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fill_frontmatter.py posts/")
        sys.exit(1)

    base_dir = pathlib.Path(sys.argv[1]).resolve()
    if not base_dir.exists():
        print(f"Directory not found: {base_dir}")
        sys.exit(1)

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    md_files = list(base_dir.rglob("index.md"))

    print(f"Found {len(md_files)} index.md files under {base_dir}")

    for f in md_files:
        process_file(client, f)


if __name__ == "__main__":
    main()

