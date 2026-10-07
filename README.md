# Messages AI – community modules

Modules change how [Messages AI](https://github.com/TilenInter/messages-ai) writes and behaves: reply styles, rules, conversation topics, instructions for the AI, support for more messaging apps and small scripts. This repository is the reviewed list the app shows under **Settings → Modules → Community modules**.

A module is **data that the app reads**, never executable Android code. Scripts run in a closed JavaScript sandbox with no access to the phone, files, contacts or the internet. That keeps modules safe for users and allowed on Google Play.

## Install a module

In the app: **Settings → Modules → Community modules**, pick one and confirm. Or download a `.mamod` file from [`modules/`](modules) and use **Import from file**. Modules signed by the Messages AI developer show **Verified**. Other modules can be installed after a warning.

## What a module can change

| Section in `module.json` | What it does |
|---|---|
| `settings` | Overrides app settings while the module is on, for example `"style_length": "very_short"`, `"style_emoji": "often"`, `"split_messages": true`, `"min_delay": 5`, `"quiet_from": "22:00"`, follow-up timing. |
| `prompt` | Extra instructions for the AI. The app's rules about honesty, safety and privacy always win. |
| `rules` | `forbidden` and `allowed` text added to the user's rules, and `words` added to the forbidden words. |
| `topics` | Conversation topics added to the user's list. |
| `interventionPhrases` | Words that make the app hand the chat over to the user. |
| `apps` | Messaging apps added to **Apps**: `package`, `name`, `mode` (`NOTIFICATION` or `SCREEN`), `tip`. Built-in apps can't be replaced. |
| `script.js` | Optional hooks, see below. |

## What a module can never change

Terms and the user's consents; automatic sending and who it replies to; the one-time AI note and the reply length limit; protected AI processing; AI providers and keys; how long chats are kept; diagnostics; SMS; sending limits; safety hand-offs; the user's own description and notes about people. Protective rules (`rule_no_personal`, `rule_no_money`, `rule_no_links`, `rule_no_promises`, `rule_no_insults`, `review_replies`) can only be switched **on**. Locked settings in a module are ignored, and the app tells the user before installing.

## Script hooks (`script.js`)

Plain JavaScript (ES6 subset, Mozilla Rhino). There is no `java`, `Packages`, network, files or timers. Each call has a 300 ms limit; errors and timeouts are ignored, and the app continues as if the script wasn't there. All functions are optional.

```js
// Before a reply: return "reply", "skip" or {handoff: "CUSTOM"} (or PHOTO, MONEY, PERSONAL_DATA, CALL, THREAT).
// A script can skip or hand over; it can never force a reply past the app's own checks.
function onIncoming(event) {        // {app, contact, message, history: [{me, text}], language}
  return "reply";
}

// Change the prompt before it goes to the AI (privacy masking still happens afterwards).
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
