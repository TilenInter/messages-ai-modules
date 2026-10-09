# Messages AI – community modules

Modules change how [Messages AI](https://github.com/TilenInter/messages-ai) writes and behaves: reply styles, rules, conversation topics, instructions for the AI, support for more messaging apps and small scripts. This repository is the reviewed list the app shows under **Settings → Modules → Community modules**.

A module is **data that the app reads**, never executable Android code. Scripts run in a closed JavaScript sandbox with no access to the phone, files, contacts or the internet. Automation modules use the app's built-in Android actions described below.

## Install a module

In the app: **Settings → Modules → Community modules**, pick one and confirm. Or download a `.mamod` file from [`modules/`](modules) and use **Import from file**. Modules signed by the Messages AI developer show **Verified**. Other modules can be installed after a warning.

**Write your own:** the [module author guide](GUIDE.md) ([slovensko](VODNIK.sl.md)) describes every section and setting. Community modules can use everything the official modules use – the signature only changes the warning before installing, never what a module may do.


## External automation modules — Messages AI 0.33.0/code 43+

Install from **Settings → Modules → Community modules**, or download the packages below. First update the app from [v0.33.0](https://github.com/TilenInter/messages-ai/releases/tag/v0.33.0). Enable the Messages AI accessibility service, configure an AI provider and enable the messaging apps you want it to use.

| Module | Behaviour |
|---|---|
| [Automatic drafts](modules/automatic-drafts.mamod) | Starts screen Auto in an enabled app and writes a draft. You send it. |
| [Automatic sending](modules/automatic-send.mamod) | Starts screen Auto and notification automation, writes and sends replies. Takes priority over drafts regardless of installation order. |
| [Close Google ads](modules/google-ads-close.mamod) | Independently recognizes Google full-screen ads and presses an available enabled Close/Skip control. |

Each module is independently enabled/disabled. Disable sending to return to drafts; disable both reply modules to restore saved settings. The Auto switch pauses the module-started screen session. The sending module's background setting is removed by disabling that module. The ad module does not enable replies or reopen a paused writer session.

Manifest `settings` API: `on_screen_auto: true`, `auto_send: true`, `dismiss_google_ads: true`; `max_reply_tokens`, `max_per_hour` and `max_per_contact_day` accept `0` for no local cap; `min_reply_gap_ms: 0` removes the extra local gap. `min_delay`, `max_delay` and `realistic_typing` configure writing delay. The published reply modules remove these local caps/delays. Account entitlement and the selected AI provider still apply.

The ads module does not click advertiser destinations, resume reward videos, bypass timers or guess coordinates. Google composers that hide EditText can use the Android 13+ accessibility input method if an actual editor connection is available; the app verifies the target, draft contents and resulting message.

## No AI footer — Messages AI 0.39.0/code 49+

[No AI footer](modules/no-ai-footer.mamod) omits the automatic AI-assistance note from replies sent through notifications or an open conversation. Install it from **Settings → Modules → Community modules** after updating to [v0.39.0](https://github.com/TilenInter/messages-ai/releases/tag/v0.39.0).

Its only setting is `ai_reply_note: false`. It does not enable automatic replies or sending, edit the reply body, or instruct the AI to deny its involvement. Disabling/removing it restores the default one-time note for conversations that have not received it. Saved disclosure timestamps are preserved; sending without the note does not record it as delivered. The module is signed with the developer key and requires app versionCode 49, so older apps refuse installation.

## Free AI (automatic) — Messages AI 0.40.0/code 50+

[Free AI (automatic)](modules/free-ai-auto.mamod) writes replies with free AI providers. The app tries them in the listed order and automatically switches to the next one when a provider runs out of free quota, is rate-limited, rejects the key, no longer has the model, fails or does not answer – like an [OmniRoute](https://github.com/diegosouzapw/OmniRoute) combo, but inside the app, without a server.

| Order | Provider | Key | Models |
|---|---|---|---|
| 1 | Google Gemini | free key from [AI Studio](https://aistudio.google.com/apikey) | gemini-2.5-flash, gemini-3-flash-preview, gemini-2.5-flash-lite |
| 2 | Groq | free key from [console.groq.com](https://console.groq.com/keys) | openai/gpt-oss-120b, qwen/qwen3.6-27b, openai/gpt-oss-20b |
| 3 | Mistral | free key from [console.mistral.ai](https://console.mistral.ai/api-keys) | mistral-small-latest, mistral-large-latest |
| 4 | OpenRouter | free key from [openrouter.ai](https://openrouter.ai/keys) | openrouter/free |
| 5 | NVIDIA | free key from [build.nvidia.com](https://build.nvidia.com) | openai/gpt-oss-120b, google/gemma-4-31b-it |
| 6 | GitHub Models | GitHub token with Models access | openai/gpt-4.1-mini |
| 7 | SambaNova | free key from [cloud.sambanova.ai](https://cloud.sambanova.ai/apis) | Meta-Llama-3.3-70B-Instruct, gpt-oss-120b |
| 8 | Cohere | trial key from [dashboard.cohere.com](https://dashboard.cohere.com/api-keys) | command-a-03-2025 |
| 9 | LLM7 | free token from [token.llm7.io](https://token.llm7.io) | gpt-4.1-nano-2025-04-14, gpt-4o-mini-2024-07-18 |
| 10 | OVHcloud AI Endpoints | none (anonymous, about 2 requests/min per model) | gpt-oss-120b, Meta-Llama-3_3-70B-Instruct, Mistral-Small-3.2-24B-Instruct-2506 |
| 11 | Pollinations | none (anonymous, best effort) | openai, mistral, openai-fast |

Without any key the module works through OVHcloud and Pollinations. Every free key you add in **AI models** (tap a provider marked *needs a free key*) adds more capacity in front of them. A key is only ever sent to the server it was entered for. **AI models** shows each provider's state: ready, resting (and for how long) or needs a free key.

Switching rules: a rate limit rests that model for 1 minute (doubling up to 1 hour), used-up free quota for 1 hour (up to 12 hours), a rejected key or unreachable server rests the whole provider (12 hours / 30 seconds and up), a removed model rests for a day; the provider's `Retry-After` wins when given. A success resets the counter. One reply tries at most six models, two per provider, for at most two minutes. Your own providers are used only after every free route fails. Disable or remove the module to return to your own providers only.

Free plans have their own terms and some may use prompts to improve their models; protected AI processing still masks numbers, codes and addresses before sending. Free model names change – the module is updated without an app release.

### `freeAi` in `module.json`

```json
"settings": { "free_ai": true },
"freeAi": { "routes": [
  { "name": "Groq", "baseUrl": "https://api.groq.com/openai/v1", "models": ["openai/gpt-oss-120b"], "key": true, "keyUrl": "https://console.groq.com/keys" },
  { "name": "OVHcloud", "baseUrl": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1", "model": "gpt-oss-120b", "key": false }
] }
```

`free_ai: true` (or `"first"`) uses free routes before the owner's providers; `"backup"` uses them only after the owner's providers fail. `baseUrl` is an OpenAI-compatible HTTPS address without `/chat/completions`; only built-in known free-tier servers are accepted (`FreeAiCatalog.HOSTS` in the app), so a module can never send conversations to another server. `key: true` routes are skipped until the owner saves a key for a provider on the same server. Up to 60 routes.

## Reply suggestions — Messages AI 0.43.0/code 53+

[Reply suggestions](modules/reply-suggestions.mamod) shows three suggested replies in bubbles above an open chat. Tap a bubble to send that reply, tap **↻** for three new ones, **×** hides them until you open another chat. New suggestions are written by themselves when a message arrives. A reply is sent only if the chat and its last messages are still the same and the text field is empty; in the Google Play version it is typed into the field and you send it. Suggestions use your AI provider (or Free AI) and pass the same checks as every reply.

Its only setting is `reply_suggestions: true`.

## More reply languages — Messages AI 0.43.0/code 53+

[More reply languages](modules/more-languages.mamod) teaches the reply logic Finnish, Hungarian, Romanian and Swedish: the app recognizes questions, requests, bad and good news, thanks and goodbyes in those languages and checks that a reply really answers them. The words apply only to chats in that language. Since 0.43.0 the app itself also understands French, Portuguese, Dutch, Polish, Czech, Slovak, Russian, Ukrainian, Serbian and Turkish, and treats a question mark in any script as a question.

### `replyLogic` in `module.json`

```json
"replyLogic": { "fi": { "question": ["milloin"], "info": ["milloin", "missä"], "thanks": ["kiitos"], "goodbye": ["hyvää yötä"], "filler": ["joo"] } }
```

Categories: `question`, `info`, `howAreYou`, `confused`, `request`, `greeting`, `thanks`, `apology`, `bad`, `good`, `laugh`, `goodbye`, `filler`. Plain words or phrases (no regular expressions), case and accents ignored, whole words only; up to 2,000 words per module. See the [guide](GUIDE.md#6-reply-logic-for-any-language).

## What a module can change

| Section in `module.json` | What it does |
|---|---|
| `settings` | Overrides app settings while the module is on, for example `"style_length": "very_short"`, `"style_emoji": "often"`, `"split_messages": true`, `"min_delay": 5`, `"quiet_from": "22:00"`, follow-up timing. |
| `prompt` | Extra instructions for the AI. The app's rules about honesty, safety and privacy always win. |
| `rules` | `forbidden` and `allowed` text added to the user's rules, and `words` added to the forbidden words. |
| `topics` | Conversation topics added to the user's list. |
| `interventionPhrases` | Words that make the app hand the chat over to the user. |
| `apps` | Messaging apps added to **Apps**: `package`, `name`, `mode` (`NOTIFICATION` or `SCREEN`), `tip`. Built-in apps can't be replaced. |
| `strings` | Texts of the app by language: `{"en": {"home_master": "Auto-reply"}, "fr": {...}}`. Replace texts in an existing language or translate the app into a new one (since app 0.29.0). |
| `languages` | Names of new languages, in that language: `{"fr": "Français"}`. The language appears in **Settings → Languages → App language**. |
| `theme` | Colours for light and dark mode: `{"name": "Ocean", "light": {"ios_bg": "#EEF4FA"}, "dark": {...}}` (since app 0.29.0). |
| `freeAi` | Free AI routes tried in order with automatic switching, enabled by `"settings": {"free_ai": true}` (since app 0.40.0). Only known free-tier HTTPS servers; see [Free AI](#free-ai-automatic--messages-ai-0400code-50). |
| `replyLogic` | Words that teach the reply logic another language, by ISO 639 code (since app 0.43.0). |
| `settings.reply_suggestions` | Three suggested replies above an open chat; tap one to send it (since app 0.43.0). |
| `script.js` | Optional hooks, see below. |

## What a module can never change

Account credentials, stored consent and disclosure history, provider keys, chat retention, diagnostics, SMS and personal profile/notes stay separate. Since app 0.33.0, modules can configure automatic drafting/sending, reply scope, local length/rate/gap limits, AI review/privacy processing and protective rules in either direction. Since 0.39.0, `ai_reply_note: false` omits the automatic AI footer. Since 0.40.0, `free_ai` with `freeAi.routes` sends replies to the listed known free-tier AI servers with automatic switching; keys stay with the owner. Since 0.43.0, `reply_suggestions: true` shows suggested replies that the owner sends with a tap, and `replyLogic` adds reply-logic words for any language. Runtime overrides disappear when a module is disabled; they do not rewrite saved preferences. Locked settings are ignored and listed in the existing install summary.

Texts about consents, privacy, terms, data export, reports and modules themselves (keys starting with `disclosure_`, `auto_consent`, `terms_`, `account_privacy`, `account_delete`, `account_required`, `protect_`, `modules_`, `wipe_`, `report_`, `signin_privacy`, `signin_terms`, `send_changed`, `mydata_`, `oss_`, `backup_`, `privacy`) can't be changed: in a new language they stay in English so they are always accurate. A text whose placeholders (`%1$s`, `%2$d` …) differ from the original is ignored.

## Translations

Export every text of the app as a starting point, translate the values and keep the keys and placeholders:

```sh
python tools/mamod.py strings-template <messages-ai>/app/src/main/res/values/strings.xml fr src/french/strings.json
```

Put the result's `languages` and `strings` into your `module.json`. [`templates/strings-en.json`](templates/strings-en.json) holds the English texts of the current app version. Texts you don't translate stay in English.

## Colour themes

Themeable colours: `ios_bg` (screen), `ios_card` (cards), `ios_card_pressed`, `ios_label` (text), `ios_secondary`, `ios_tertiary`, `ios_separator`, `ios_fill`, `card_stroke`, `action_fill` and `action_text` (main buttons), `switch_active`, `switch_inactive`, `nav_active` (selected tab), `icon_ink`, `chevron`, `segment_track`, `trust_text`, and the accents `ios_blue`, `ios_green`, `ios_red`, `ios_orange`, `ios_yellow`, `ios_purple`, `ios_indigo`, `ios_teal`, `ios_pink`, `ios_gray`. The Google sign-in button keeps Google's colours.

A theme is used only if text stays readable (WCAG contrast): `ios_label` on `ios_bg` and `ios_card` at least 4.5:1, `action_text` on `action_fill` 4.5:1, `ios_secondary`, `nav_active` and `icon_ink` on `ios_card` 3:1. Otherwise the app ignores the theme for that mode. The floating panel keeps its own dark colours.

## Script hooks (`script.js`)

Plain JavaScript (ES6 subset, Mozilla Rhino). There is no `java`, `Packages`, network, files or timers. Each call has a 300 ms limit; errors and timeouts are ignored, and the app continues as if the script wasn't there. All functions are optional.

```js
// Before a reply: return "reply", "skip" or {handoff: "CUSTOM"} (or PHOTO, MONEY, PERSONAL_DATA, CALL, THREAT).
// A script can skip or hand over; it can never force a reply past the app's own checks.
function onIncoming(event) {        // {app, contact, message, history: [{me, text}], language}
  return "reply";
}

// Change the prompt before it goes to the AI (privacy masking still happens afterwards).
// kind: REPLY, FORCED, OPENER, FOLLOW_UP or SUGGESTIONS (reply suggestions, since 0.43.0).
function beforePrompt(prompt) {     // {system, user, app, contact, kind}
  return { system: prompt.system, user: prompt.user };
}

// Change the reply: return new text, false (don't reply) or undefined (keep it).
// The changed reply is checked again: it may never deny that AI helps, and forbidden words still apply.
function afterReply(reply) {        // {text, app, contact, language}
  return undefined;
}
```

## Make a module

The full reference is the [module author guide](GUIDE.md) ([slovensko](VODNIK.sl.md)). In short:

1. Create a folder with `module.json` (and optionally `script.js`):

```json
{
  "format": 1,
  "id": "my-style",
  "name": "My style",
  "version": "1.0.0",
  "author": "Your name",
  "license": "CC-BY-4.0",
  "description": "What it does, in one or two sentences.",
  "minAppVersion": 37,
  "settings": { "style_length": "short" },
  "prompt": "Write warmly and simply."
}
```

2. Pack it (requires Python and `pip install cryptography`):

```sh
python tools/mamod.py keygen my-key.pem            # once; keep the .pem private
python tools/mamod.py pack src/my-style modules/my-style.mamod --key my-key.pem
python tools/mamod.py verify modules/my-style.mamod
```

`id`: 3–64 characters of `a-z 0-9 . _ -`. Allowed files in a module: `module.json`, `script.js`, `signature.json` (created by `pack`). Size limits: 512 KB per file, 256 KB `module.json`, 64 KB `script.js`.

## Submit a module

Open a pull request that adds your source folder under `src/` and your packed module under `modules/`. Before a module is listed, it is reviewed, re-signed with the Messages AI key and added to `index.json`. By submitting you confirm that you have the rights to the content and that it may be published under the licence you state.

Modules are not accepted if they:
- break the law, Google Play's policies or the [Messages AI terms](https://messages-ai-77f66.web.app/terms.html);
- try to deceive the people the user chats with, for example by denying that AI helps or impersonating someone;
- collect or leak personal data, or try to get around the locked protections;
- contain hate, harassment, sexual content involving minors, or anything meant to cause harm.

## Report a module

Open an issue in this repository or write to tilenmatjasic6389@outlook.com. Modules that break the rules are removed from the list.

## Licence

Each module states its own licence in `module.json`. The documentation and tools in this repository are CC0-1.0.
