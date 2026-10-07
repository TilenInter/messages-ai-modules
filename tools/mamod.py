"""Messages AI modules (.mamod): pack, sign, verify and build the community index.

  python tools/modules/mamod.py keygen <private.pem>             new ECDSA P-256 key (keep the .pem private)
  python tools/modules/mamod.py pack <folder> <out.mamod> [--key private.pem]
  python tools/modules/mamod.py verify <file.mamod>
  python tools/modules/mamod.py index <modules-folder> <index.json>

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
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


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
    assert len(data) <= 256 * 1024, "module.json is larger than 256 KB"
    return m


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


def index(folder, out):
    folder = Path(folder)
    entries = []
    for f in sorted(folder.glob("*.mamod")):
        m = verify(f, quiet=True)
        entries.append({
            "id": m["id"], "name": m["name"], "version": m.get("version", ""), "author": m.get("author", ""),
            "description": m.get("description", ""), "file": f"modules/{f.name}", "sha256": sha(f.read_bytes()),
        })
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
    else:
        print(__doc__)
