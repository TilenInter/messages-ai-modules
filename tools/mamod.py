"""Messages AI modules (.mamod): pack, sign, verify and build the community index.

  python tools/modules/mamod.py keygen <private.pem>             new ECDSA P-256 key (keep the .pem private)
  python tools/modules/mamod.py pack <folder> <out.mamod> [--key private.pem]
  python tools/modules/mamod.py verify <file.mamod>
  python tools/modules/mamod.py index <modules-folder> <index.json>
  python tools/modules/mamod.py strings-template <strings.xml> <lang> <out.json>   texts to translate (English as a start)

A module folder contains module.json and, optionally, script.js. Packing checks the format, signs
"messages-ai-module-v1\\n<sha256 module.json>\\n<sha256 script.js>\\n" and writes a reproducible ZIP.
Requires: python -m pip install cryptography
"""
import base64
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
LANG = re.compile(r"^[a-z]{2,3}$")
PKG = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
# Longest texts packing accepts: names and tips are cut by the app beyond this, descriptions are kept short enough for
# a readable card (the app shows up to 1,000 characters since 0.73.0, 600 before).
MAX_NAME, MAX_DESCRIPTION, MAX_TIP = 60, 600, 300
# Icon names the app knows (ModuleIcons.NAMES in Messages AI 0.73+); older versions ignore "icon".
ICONS = {"activity", "bell", "book", "brain", "chat", "check", "clock", "cpu", "document", "download", "flask", "globe",
         "grid", "heart", "info", "lightbulb", "lock", "palette", "pen", "people", "phone", "rules", "scales", "search",
         "send", "settings", "shield", "sliders", "sparkles", "upload", "user"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def message(manifest: bytes, script: bytes) -> bytes:
    return f"messages-ai-module-v1\n{sha(manifest)}\n{sha(script)}\n".encode()


def check_manifest(data: bytes) -> dict:
    m = json.loads(data.decode("utf-8"))
    assert m.get("format") == 1, "format must be 1"
    assert ID.match(m.get("id", "")), "id: 3–64 of a-z 0-9 . _ - (starting with a letter or digit)"
    assert m.get("name", "").strip(), "name is required"
    assert m.get("license", "").strip(), "license is required (for example CC-BY-4.0 or MIT)"
    compatibility = m.get("compatibility", {})
    assert isinstance(compatibility, dict), "compatibility must be an object"
    for field in ("conflicts", "exclusiveGroups"):
        values = compatibility.get(field, [])
        assert isinstance(values, list) and len(values) <= 50, f"compatibility.{field} must be a list of up to 50 ids"
        assert all(isinstance(value, str) and ID.fullmatch(value) for value in values), \
            f"compatibility.{field} contains an invalid id"
    assert m.get("id") not in compatibility.get("conflicts", []), "a module cannot conflict with itself"
    assert len(data) <= 256 * 1024, "module.json is larger than 256 KB"
    check_texts(m)
    return m


def check_texts(m: dict):
    """Names, descriptions and tips must fit what the app shows (nothing is cut), in English and every translation."""
    def fits(label, value, limit):
        assert isinstance(value, str), f"{label} must be text"
        assert len(value.strip()) <= limit, f"{label} has {len(value.strip())} characters; the app shows at most {limit}"
    fits("name", m.get("name", ""), MAX_NAME)
    fits("description", m.get("description", ""), MAX_DESCRIPTION)
    for app in m.get("apps", []):
        fits(f"apps.{app.get('package')}.tip", app.get("tip", ""), MAX_TIP)
    if "icon" in m:
        assert m["icon"] in ICONS, f"icon must be one of: {', '.join(sorted(ICONS))}"
    translations = m.get("translations", {})
    assert isinstance(translations, dict), "translations must be an object: language → {name, description, tips}"
    packages = {app.get("package") for app in m.get("apps", [])}
    for lang, t in translations.items():
        assert LANG.fullmatch(lang), f"translations: {lang!r} is not a language code like sl or de"
        assert isinstance(t, dict), f"translations.{lang} must be an object"
        unknown = set(t) - {"name", "description", "tips"}
        assert not unknown, f"translations.{lang}: unknown fields {sorted(unknown)}"
        fits(f"translations.{lang}.name", t.get("name", ""), MAX_NAME)
        fits(f"translations.{lang}.description", t.get("description", ""), MAX_DESCRIPTION)
        for pkg, tip in t.get("tips", {}).items():
            assert PKG.fullmatch(pkg) and pkg in packages, f"translations.{lang}.tips: {pkg} is not one of the module's apps"
            fits(f"translations.{lang}.tips.{pkg}", tip, MAX_TIP)


def keygen(path):
    key = ec.generate_private_key(ec.SECP256R1())
    Path(path).write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    pub = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    print("private key:", path, "(keep it secret)")
    print("public key:", base64.b64encode(pub).decode())


def pack(folder, out, key_path=None):
    folder = Path(folder)
    manifest = (folder / "module.json").read_bytes()
    m = check_manifest(manifest)
    script_path = folder / "script.js"
    script = script_path.read_bytes() if script_path.exists() else b""
    assert len(script) <= 64 * 1024, "script.js is larger than 64 KB"
    files = [("module.json", manifest)]
    if script:
        files.append(("script.js", script))
    if key_path:
        key = serialization.load_pem_private_key(Path(key_path).read_bytes(), password=None)
        sig = key.sign(message(manifest, script), ec.ECDSA(hashes.SHA256()))
        pub = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        signature = {"publicKey": base64.b64encode(pub).decode(), "signature": base64.b64encode(sig).decode()}
        files.append(("signature.json", json.dumps(signature, indent=2).encode()))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files:
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    Path(out).write_bytes(buf.getvalue())
    print(f"packed {m['id']} {m.get('version', '')} -> {out} ({len(buf.getvalue())} bytes, {'signed' if key_path else 'unsigned'})")


def verify(path, quiet=False):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        extra = names - {"module.json", "script.js", "signature.json"}
        assert not extra, f"unexpected files: {sorted(extra)}"
        manifest = z.read("module.json")
        script = z.read("script.js") if "script.js" in names else b""
        m = check_manifest(manifest)
        if "signature.json" not in names:
            status, key = "unsigned", None
        else:
            s = json.loads(z.read("signature.json"))
            key = s["publicKey"]
            pub = serialization.load_der_public_key(base64.b64decode(key))
            pub.verify(base64.b64decode(s["signature"]), message(manifest, script), ec.ECDSA(hashes.SHA256()))
            status = "signed"
    if not quiet:
        fp = hashlib.sha256(base64.b64decode(key)).hexdigest()[:16] if key else "-"
        print(f"{m['id']} {m.get('version', '')}: {status} (key {fp}), script: {'yes' if script else 'no'}")
    return m


# Besedila, ki jih modul ne sme spremeniti (enako kot ModuleUi.LOCKED_TEXT v aplikaciji).
# Same prefixes as ModuleUi.LOCKED_TEXT in the app (legal texts, consents, disclosures, what is sent where).
LOCKED_TEXT = ("disclosure_", "auto_consent", "terms_", "account_privacy", "account_delete", "account_required", "protect_", "modules_",
               "wipe_", "report_", "signin_privacy", "signin_terms", "access_", "billing_", "developer_", "send_changed", "mydata_",
               "oss_", "backup_", "privacy", "sms_import_", "picture_", "voice_", "smart_actions_", "approval_", "business_")


def strings_template(strings_xml, lang, out):
    """English texts of the app as a starting point for a translation module (locked texts left out)."""
    import xml.etree.ElementTree as ET

    def unescape(text):
        text = text or ""
        if len(text) >= 2 and text[0] == text[-1] == '"':
            text = text[1:-1]
        return text.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n").replace("\\@", "@").replace("\\?", "?").replace("\\\\", "\\")

    texts = {}
    for e in ET.parse(strings_xml).getroot().findall("string"):
        name = e.get("name")
        if e.get("translatable") == "false" or name.startswith(LOCKED_TEXT):
            continue
        texts[name] = unescape("".join(e.itertext()))
    data = {"languages": {lang: "Language name in that language"}, "strings": {lang: texts}}
    Path(out).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(texts)} texts -> {out} (translate the values, keep the keys and placeholders like %1$s)")


AUTOMATION_SETTINGS = {"on_screen_auto", "auto_send", "send_mode", "dismiss_google_ads", "ai_reply_note", "automation_enabled",
                       # 0.50: features the app shows only with a module (ModuleFeature in the app)
                       "followups", "followup_enabled", "openers", "opener_auto", "new_chats", "group_chats", "reply_groups", "skip_ads",
                       # 0.55: SMS import (the owner turns it on in Learning → SMS import)
                       "sms_import"}


def module_types(manifest, script=False):
    """Stable catalog groups used by Messages AI's module browser; a module may be in more than one."""
    settings = manifest.get("settings", {})
    types = []
    if (any(key not in AUTOMATION_SETTINGS for key in settings) or any(manifest.get(key) for key in
            ("freeAi", "replyLogic", "prompt", "rules", "topics", "interventionPhrases")) or settings.get("reply_suggestions") is True):
        types.append("ai")
    if any(key in AUTOMATION_SETTINGS for key in settings):
        types.append("automation")
    if any(manifest.get(key) for key in ("strings", "languages", "theme")):
        types.append("appearance")
    if manifest.get("apps") or script:
        types.append("apps")
    return types


def index(folder, out):
    folder = Path(folder)
    entries = []
    for f in sorted(folder.glob("*.mamod")):
        m = verify(f, quiet=True)
        with zipfile.ZipFile(f) as z:
            types = module_types(m, "script.js" in z.namelist())
        entry = {
            "id": m["id"], "name": m["name"], "version": m.get("version", ""), "author": m.get("author", ""),
            "description": m.get("description", ""), "types": types,
            "conflicts": m.get("compatibility", {}).get("conflicts", []),
            "exclusiveGroups": m.get("compatibility", {}).get("exclusiveGroups", []),
            "file": f"modules/{f.name}", "sha256": sha(f.read_bytes()),
        }
        # 0.73: the catalog shows each module's icon and its name and description in the app's language.
        if m.get("icon"):
            entry["icon"] = m["icon"]
        translations = {lang: {k: t[k] for k in ("name", "description") if t.get(k)} for lang, t in m.get("translations", {}).items()}
        if any(translations.values()):
            entry["translations"] = {lang: t for lang, t in translations.items() if t}
        entries.append(entry)
    Path(out).write_text(json.dumps({"format": 1, "modules": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"index: {len(entries)} module(s) -> {out}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "keygen":
        keygen(a[1])
    elif a[0] == "pack":
        pack(a[1], a[2], a[a.index("--key") + 1] if "--key" in a else None)
    elif a[0] == "verify":
        verify(a[1])
    elif a[0] == "index":
        index(a[1], a[2])
    elif a[0] == "strings-template":
        strings_template(a[1], a[2], a[3])
    else:
        print(__doc__)
