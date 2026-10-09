# Module author guide

This guide covers everything a Messages AI module can do, as of app 0.43.0 (versionCode 53). Read it from the top for a first module, or jump to a section. A Slovenian version is in [VODNIK.sl.md](VODNIK.sl.md).

## Community modules can do what official modules can

Messages AI has **one** module system. The modules published by the Messages AI developer (Automatic sending, Free AI, Reply suggestions, More reply languages …) use exactly the same `module.json` sections and settings described here. Nothing is reserved for them:

| | Official (signed with the developer key) | Community (signed with your key) | Unsigned |
|---|---|---|---|
| Every section and setting in this guide | ✓ | ✓ | ✓ |
| Locked settings and texts (accounts, consents, keys, terms …) | ✗ | ✗ | ✗ |
| Shown before installing | *Verified* | *Other author* + key fingerprint | *Unsigned* warning |

The signature only proves who published a module and that it was not changed; it never unlocks or blocks a capability. A signature that does not match the files is rejected. The app's unit tests (`V43ModulesTest`) check that an unsigned module and a module signed with an unknown key get the same capabilities as a developer-signed one.

To appear in the in-app **Community modules** list, open a pull request here (see [Submit](#submit-a-module)). After review the module is re-signed with the Messages AI key, so it shows *Verified* too.

## 1. Your first module in five minutes

```sh
git clone https://github.com/TilenInter/messages-ai-modules && cd messages-ai-modules
pip install cryptography
mkdir -p src/my-style
```

`src/my-style/module.json`:

```json
{
  "format": 1,
  "id": "my-style",
  "name": "My style",
  "version": "1.0.0",
  "author": "Your name",
  "license": "CC-BY-4.0",
  "description": "Short, warm replies with an emoji now and then.",
  "minAppVersion": 53,
  "settings": { "style_length": "short", "style_emoji": "rare" },
  "prompt": "Write warmly and simply."
}
```

```sh
python tools/mamod.py keygen my-key.pem                                   # once – keep it private
python tools/mamod.py pack src/my-style modules/my-style.mamod --key my-key.pem
python tools/mamod.py verify modules/my-style.mamod
```

Copy `modules/my-style.mamod` to the phone and choose **Settings → Modules → Import from file**. The install summary lists everything the module changes. Disable or remove the module to undo it; modules never rewrite saved settings.

## 2. Package format

- A `.mamod` file is a ZIP with `module.json`, optional `script.js` and `signature.json` (written by `pack`). Any other file is rejected – no Android code, libraries or assets.
- Limits: 512 KB per file, 256 KB `module.json`, 64 KB `script.js`.
- `id`: 3–64 characters `a-z 0-9 . _ -`, starting with a letter or digit. Installing a module with the same `id` updates it.
- `format` must be `1`. `minAppVersion` is the app **versionCode** (0.43.0 = 53); older apps refuse the module.
- `name`, `version`, `author`, `license`, `description`, `homepage` are shown to the user.
- Signature: ECDSA P-256 over `messages-ai-module-v1\n<sha256 module.json>\n<sha256 script.js>\n` (empty script = hash of nothing). `tools/mamod.py` does this for you.

## 3. What a module can change

| Section | Since | What it does |
|---|---|---|
| `settings` | 0.28 | Overrides app settings while the module is on ([list](#4-settings)). |
| `prompt` | 0.28 | Extra instructions for the AI (up to 8,000 characters). The app's honesty, safety and privacy rules always win. |
| `rules` | 0.28 | `forbidden` and `allowed` text added to the user's rules; `words` added to the forbidden words. |
| `topics` | 0.28 | Conversation topics added to the user's list. |
| `interventionPhrases` | 0.28 | Phrases that hand the chat over to the user. |
| `apps` | 0.28 | Messaging apps added to **Apps** ([details](#apps)). |
| `strings`, `languages` | 0.29 | App texts by language, also whole new UI languages ([details](#app-texts-and-new-ui-languages)). |
| `theme` | 0.29 | Light and dark colours ([details](#colour-themes)). |
| `freeAi` | 0.40 | Free AI providers with automatic switching ([details](#free-ai)). |
| `replyLogic` | 0.43 | Teaches the reply logic any language ([details](#reply-logic-for-any-language)). |
| `script.js` | 0.28 | Hooks before and after the AI ([details](#script-hooks)). |

Lists (`topics`, `interventionPhrases`, `rules.words`) keep up to 200 entries of up to 300 characters each.

## 4. Settings

`"settings": { "key": value }` – booleans, numbers and strings. Later modules override earlier ones. Any app setting that is not locked can be set; the most useful ones:

| Area | Keys and values |
|---|---|
| Reply style | `style_length` (`natural`, `very_short`, `short`, `medium`, `long`, `like_me`), `style_emoji` (`never`, `rare`, `often`, `like_me`), `style_address`, `style_lowercase`, `style_language`, `style_max_chars`, `split_messages`, `split_max` |
| Timing | `min_delay`, `max_delay` (seconds), `realistic_typing`, `quiet_enabled`, `quiet_from`, `quiet_to` (`"22:00"`), `start_reply_window` |
| Follow-ups | `followup_enabled`, `followup_max`, `followup_seen_min`, `followup_unseen_min`, `followup_style` |
| Rules | `rule_no_money`, `rule_no_meetings`, `rule_no_personal`, `rule_no_promises`, `rule_no_politics`, `rule_no_flirt`, `rule_no_insults`, `rule_no_links`, `rule_no_swearing`, `rule_admit_ai`, `money_style`, `money_action` |
| Hand-over | `pause_photo`, `pause_call`, `pause_personal_data`, `pause_threat`, `bot_question` |
| Memory and learning | `memory_enabled`, `memory_every`, `learn_owner`, `use_past_replies`, `max_history`, `review_replies`, `protected_ai` |
| Automation | `on_screen_auto: true` (start screen Auto in an open enabled app), `auto_send: true` or `send_mode: "auto"` (send instead of drafting), `dismiss_google_ads: true`, `max_reply_tokens`, `max_per_hour`, `max_per_contact_day` (`0` = no local cap), `min_reply_gap_ms` (`0` = no extra gap) |
| AI note | `ai_reply_note: false` omits the automatic “an AI assistant helps me” footer |
| Free AI | `free_ai: true` / `"first"` or `"backup"` with a `freeAi` section |
| Reply suggestions | `reply_suggestions: true` ([details](#reply-suggestions)) |

**Locked** (ignored and listed in the install summary): `terms_*`, `auto_consent*`, `disclosure_*`, `report_*`, `account*`, `signin*`, `access_*`, `billing_*`, `developer_*`, `lang_*`, `test_*`, `panel_*`, `device_*`, `phone_setup*`, `api_*`, `backup*`, `send_policy_v316`, `diag_include_content`, `retention_days`, `sms_history`, `keep_alive`, `active_provider`, `fallback_provider`, `persona`, `contact_notes`, `owner_languages`, `learn_daily`, `app_language`, and the lists `rules_forbidden`, `rules_allowed`, `forbidden_words`, `topics`, `intervention_phrases` (use the module sections for those). Account credentials, provider keys, consents, disclosure history, SMS and personal notes are never readable or changeable by a module.

## 5. Reply suggestions

```json
"settings": { "reply_suggestions": true }
```

Shows three suggested replies in bubbles above an open chat (app 0.43.0+):

- New suggestions are written when a new message from the other person is visible; **↻** writes three new ones for the same messages; **×** hides the bubbles until another chat is opened.
- Tapping a bubble sends that reply in the same chat – only if the chat and its last messages are still the same and the text field is empty. In the Google Play version (without a screen-automation module) the reply is typed into the field and the user sends it.
- Suggestions use the owner's AI provider (or Free AI) and pass the same checks as every reply: forbidden words, never denying that AI helps, no broken or garbled text, `afterReply` hooks. A message that needs the owner (money, photos, “are you a bot?” …) shows no suggestions.
- The bubbles appear only in a chat of an enabled app with a text field, with an AI model set up, and not while Auto is running there.

The official [Reply suggestions](src/reply-suggestions/module.json) module is just this one setting.

## 6. Reply logic for any language

Before the AI writes, the app reads each new message and works out what it needs (a yes/no answer, information, how-are-you, a clarification, a request, bad or good news, thanks, an apology, a greeting, a goodbye). It then checks the draft: “ok” is not an answer to “when?”, laughing at bad news is not fine, and so on. Built in: Slovenian, Croatian, Serbian, English, German, Italian, Spanish, French, Portuguese, Dutch, Polish, Czech, Slovak, Russian, Ukrainian and Turkish; a question mark in any script (`?`, `¿`, `？`, `؟`, Greek `;`) is a question in every language.

`replyLogic` adds words for any other language, by ISO 639 code:

```json
"replyLogic": {
  "fi": {
    "question": ["milloin", "missä", "miksi"],
    "info": ["milloin", "missä", "miksi", "paljonko"],
    "howAreYou": ["mitä kuuluu", "miten menee"],
    "confused": ["en ymmärrä", "mitä tarkoitat"],
    "request": ["voitko", "ole hyvä"],
    "greeting": ["moi", "huomenta"],
    "thanks": ["kiitos"],
    "apology": ["anteeksi"],
    "bad": ["olen sairas"],
    "good": ["onnistui"],
    "laugh": ["hah"],
    "goodbye": ["hyvää yötä", "nähdään"],
    "filler": ["joo", "okei"]
  }
}
```

| Category | Meaning |
|---|---|
| `question` | Words that make a message a question even without `?` (question words, question particles). |
| `info` | Question words asking for information (when, where, why, how much …). A question with one of these needs a real answer; “ok” is flagged. |
| `howAreYou`, `confused`, `request`, `thanks`, `apology`, `bad`, `good`, `laugh`, `goodbye` | Phrases for each need. `greeting` counts only at the start of a short message. |
| `filler` | Content-free replies (“ok”, “yes”, “sure”) that do not answer an information question. |

- Entries are plain words or phrases, never regular expressions. Case and accents are ignored (`miksi` also finds `Miksi`, `ł`/`đ`/`ß` work), and they match whole words only.
- The words apply to chats whose language the app detects as that code; when the language is not known yet (very short messages), words of all languages apply. Avoid very short words that are common in other languages.
- Up to 2,000 words per module, 40 characters each; codes are 2–3 lowercase letters. Several modules' words are combined.
- The languages also appear in **Settings → Languages → Languages I speak**.

See [More reply languages](src/more-languages/module.json) (Finnish, Hungarian, Romanian, Swedish) for a full example.

## 7. Free AI

```json
"settings": { "free_ai": true },
"freeAi": { "routes": [
  { "name": "Groq", "baseUrl": "https://api.groq.com/openai/v1", "models": ["openai/gpt-oss-120b"], "key": true, "keyUrl": "https://console.groq.com/keys" },
  { "name": "OVHcloud", "baseUrl": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1", "model": "gpt-oss-120b", "key": false }
] }
```

- Routes are tried in order and switch automatically on limits, used-up quota, rejected keys, missing models, errors and timeouts. `free_ai: "backup"` uses them only after the owner's own providers fail.
- `baseUrl` is an OpenAI-compatible HTTPS address on a known free-tier server: `generativelanguage.googleapis.com`, `api.groq.com`, `openrouter.ai`, `api.mistral.ai`, `integrate.api.nvidia.com`, `models.github.ai`, `api.sambanova.ai`, `api.cohere.com`, `router.huggingface.co`, `api.cerebras.ai`, `api.llm7.io`, `ollama.com`, `api.siliconflow.com`, `api.together.xyz`, `api.deepinfra.com`, `api.scaleway.ai`, `oai.endpoints.kepler.ai.cloud.ovh.net`, `gen.pollinations.ai`. Other routes are dropped, so no module can send conversations elsewhere.
- `key: true` routes wait until the owner saves their own key for a provider on the same server; a key is only ever sent to that server. Up to 60 routes.

## 8. Apps

```json
"apps": [ { "package": "org.example.chat", "name": "Example Chat", "mode": "SCREEN", "tip": "Open a chat first." } ]
```

`mode` is `NOTIFICATION` (reply from notifications) or `SCREEN` (read and type in the open chat); `anonymous: true` treats every new partner as a new conversation (random-chat apps). Up to 50 apps; built-in apps can't be replaced. The user still enables each app in **Apps**.

## 9. App texts and new UI languages

```json
"languages": { "fi": "Suomi" },
"strings": { "fi": { "home_master": "Automaattinen vastaus" }, "en": { "home_master": "Auto-reply" } }
```

- `strings` replaces texts in an existing language or translates the app into a new one; `languages` names a new language (in that language) so it appears in **Settings → Languages → App language**. Up to 40 languages and 3,000 texts per language.
- Start a translation from every English text: `python tools/mamod.py strings-template <messages-ai>/app/src/main/res/values/strings.xml fi src/finnish/strings.json` ([`templates/strings-en.json`](templates/strings-en.json) holds the current texts).
- Keep placeholders (`%1$s`, `%2$d`) exactly; a text with different placeholders is ignored. Texts about consents, privacy, terms, reports, data export and modules stay in English.

## 10. Colour themes

```json
"theme": { "name": "Ocean", "light": { "ios_bg": "#EEF4FA", "ios_blue": "#0A6CBF" }, "dark": { "ios_bg": "#08131F" } }
```

Themeable colours are listed in the [README](README.md#colour-themes). A mode whose text would be hard to read (WCAG 4.5:1 for text, 3:1 for secondary text and accents) is ignored.

## 11. Script hooks

`script.js` is plain JavaScript (Mozilla Rhino, ES6 subset) with no Java, network, files or timers, 300 ms per call. Errors and timeouts are ignored. All functions are optional.

```js
// Before a reply: "reply", "skip" or {handoff: "MONEY"} (PHOTO, MONEY, PERSONAL_DATA, CALL, THREAT, CUSTOM).
function onIncoming(e) {            // {app, contact, message, history: [{me, text}], language}
  return "reply";
}
// The prompt before it goes to the AI. kind: REPLY, FORCED, OPENER, FOLLOW_UP or SUGGESTIONS (reply suggestions).
function beforePrompt(p) {          // {system, user, app, contact, kind}
  return { system: p.system, user: p.user };
}
// Each reply (and each reply suggestion): new text, false (don't send) or undefined (keep it).
function afterReply(r) {            // {text, app, contact, language}
  return undefined;
}
```

A script can skip, hand over or change a reply, but the changed reply is checked again: it may never deny that AI helps, and forbidden words still apply.

## 12. Test your module

1. `python tools/mamod.py verify modules/<id>.mamod` – format, size, signature.
2. Import it on the phone and read the install summary: every capability should be listed, locked settings appear as ignored.
3. Try it in **Test Chat** (a separate fake chat app from the [releases](https://github.com/TilenInter/messages-ai/releases)) – never on real people while testing.
4. **Log → 📋 Copy detailed log** shows `module` lines: installed modules, script errors and timeouts.

## Submit a module

Open a pull request with `src/<id>/` and the packed `modules/<id>.mamod` (signed with your key or unsigned). The maintainer reviews it, re-signs it with the Messages AI key and adds it to `index.json`. The [README](README.md#submit-a-module) lists the rules: no deception (never deny that AI helps), no collecting or leaking personal data, nothing illegal or harmful.
