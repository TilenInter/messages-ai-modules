# Vodnik za avtorje modulov

Vse, kar zmore modul za Messages AI, od aplikacije 0.43.0 (versionCode 53) naprej. Podrobnejša angleška različica: [GUIDE.md](GUIDE.md).

## Moduli skupnosti zmorejo vse, kar uradni

Messages AI ima **en** sistem modulov. Uradni moduli (Samodejno pošiljanje, Brezplačni AI, Predlogi odgovorov, Več jezikov odgovorov …) uporabljajo iste razdelke `module.json` in iste nastavitve kot vsak modul skupnosti. Nič ni rezervirano zanje:

| | Uradni (ključ razvijalca) | Skupnost (tvoj ključ) | Nepodpisan |
|---|---|---|---|
| Vsi razdelki in nastavitve iz tega vodnika | ✓ | ✓ | ✓ |
| Zaklenjene nastavitve in besedila (računi, privolitve, ključi, pogoji …) | ✗ | ✗ | ✗ |
| Pred namestitvijo | *Preverjeno* | *Drug avtor* + prstni odtis | opozorilo *Nepodpisano* |

Podpis samo dokaže, kdo je modul objavil in da ni spremenjen – nobene zmožnosti ne odklene in ne zaklene. Podpis, ki se ne ujema z datotekami, aplikacija zavrne. Testi aplikacije (`V43ModulesTest`) preverjajo, da nepodpisan modul in modul s tujim ključem dobita iste zmožnosti kot modul, podpisan s ključem razvijalca.

Za seznam **Moduli skupnosti** v aplikaciji odpri pull request v tem repozitoriju. Po pregledu se modul podpiše s ključem Messages AI in je tudi *Preverjen*.

## 1. Prvi modul

```sh
git clone https://github.com/TilenInter/messages-ai-modules && cd messages-ai-modules
pip install cryptography
mkdir -p src/moj-slog
```

`src/moj-slog/module.json`:

```json
{
  "format": 1,
  "id": "moj-slog",
  "name": "Moj slog",
  "version": "1.0.0",
  "author": "Tvoje ime",
  "license": "CC-BY-4.0",
  "description": "Kratki, topli odgovori, občasno z emojijem.",
  "minAppVersion": 53,
  "settings": { "style_length": "short", "style_emoji": "rare" },
  "prompt": "Piši toplo in preprosto."
}
```

```sh
python tools/mamod.py keygen moj-kljuc.pem                                  # enkrat – ključ obdrži zase
python tools/mamod.py pack src/moj-slog modules/moj-slog.mamod --key moj-kljuc.pem
python tools/mamod.py verify modules/moj-slog.mamod
```

Datoteko `.mamod` prenesi na telefon: **Nastavitve → Moduli → Uvozi iz datoteke**. Povzetek pred namestitvijo pokaže vse, kar modul spremeni. Izklop ali odstranitev modula vse povrne; shranjenih nastavitev modul nikoli ne prepiše.

## 2. Oblika paketa

- `.mamod` je ZIP z `module.json`, po želji `script.js` in `signature.json` (naredi ga `pack`). Druge datoteke (koda, knjižnice) so zavrnjene.
- Omejitve: 512 KB na datoteko, 256 KB `module.json`, 64 KB `script.js`.
- `id`: 3–64 znakov `a-z 0-9 . _ -`; modul z istim `id` posodobi prejšnjega. `format` je `1`, `minAppVersion` je **versionCode** aplikacije (0.43.0 = 53).

## 3. Kaj lahko modul spremeni

| Razdelek | Od | Kaj naredi |
|---|---|---|
| `settings` | 0.28 | Nastavitve, dokler je modul vklopljen ([seznam](#4-nastavitve)). |
| `prompt` | 0.28 | Dodatna navodila za AI (do 8.000 znakov); pravila aplikacije o poštenosti, varnosti in zasebnosti vedno zmagajo. |
| `rules` | 0.28 | `forbidden`, `allowed` in prepovedane besede `words`. |
| `topics`, `interventionPhrases` | 0.28 | Teme pogovora in besede, ob katerih pogovor prevzame lastnik. |
| `apps` | 0.28 | Dodatne aplikacije za sporočila (`package`, `name`, `mode`: `NOTIFICATION` ali `SCREEN`, `anonymous`, `tip`). |
| `strings`, `languages` | 0.29 | Besedila aplikacije in novi jeziki vmesnika. |
| `theme` | 0.29 | Barve za svetli in temni način. |
| `freeAi` | 0.40 | Brezplačni AI s samodejnim preklopom. |
| `replyLogic` | 0.43 | Logika odgovora v katerem koli jeziku. |
| `script.js` | 0.28 | Kljuke pred in po AI. |

## 4. Nastavitve

Najpogostejše: `style_length` (`natural`, `very_short`, `short`, `medium`, `long`, `like_me`), `style_emoji` (`never`, `rare`, `often`, `like_me`), `split_messages`, `split_max`, `min_delay`, `max_delay`, `realistic_typing`, `quiet_from`, `quiet_to`, `followup_*`, `rule_no_*`, `pause_*`, `memory_enabled`, `review_replies`, `protected_ai`.

Avtomatizacija: `on_screen_auto: true`, `auto_send: true`, `dismiss_google_ads: true`, `max_reply_tokens`, `max_per_hour`, `max_per_contact_day` (`0` = brez omejitve), `min_reply_gap_ms`. Opomba o AI: `ai_reply_note: false`. Brezplačni AI: `free_ai`. Predlogi odgovorov: `reply_suggestions: true`.

**Zaklenjeno** za vse module (se prezre in pokaže v povzetku): pogoji, privolitve, razkritja, prijava in računi, ključi in izbrani ponudnik, hramba podatkov, diagnostika, SMS, osebni opis in opombe, jeziki lastnika, jezik aplikacije ter seznami pravil, tem in besed (za te so razdelki modula). Celoten seznam je v [GUIDE.md](GUIDE.md#4-settings).

## 5. Predlogi odgovorov

```json
"settings": { "reply_suggestions": true }
```

Nad odprtim pogovorom se pokažejo trije oblački s predlogi odgovora. Ko pride novo sporočilo, se novi napišejo sami; **↻** napiše tri nove, **×** jih skrije do drugega pogovora. Dotik oblačka pošlje ta odgovor v isti pogovor – samo če so sporočila še ista in je polje za pisanje prazno. V različici za Google Play (brez modula za samodejno delo na zaslonu) se odgovor vpiše v polje, pošlješ ga sam. Predlogi gredo skozi ista preverjanja kot vsak odgovor (prepovedane besede, nikoli ne zanikajo AI, kljuka `afterReply`); pri sporočilih, ki potrebujejo lastnika (denar, slike, »si bot?«), predlogov ni.

## 6. Logika odgovora v katerem koli jeziku

Aplikacija pred pisanjem sama prebere, kaj vsako sporočilo potrebuje (odgovor da/ne, podatek, »kako si«, razlago, prošnjo, slabo ali dobro novico, zahvalo, opravičilo, pozdrav, slovo), in po pisanju preveri osnutek (»ok« ni odgovor na »kdaj?«). Vgrajeno: slovenščina, hrvaščina, srbščina, angleščina, nemščina, italijanščina, španščina, francoščina, portugalščina, nizozemščina, poljščina, češčina, slovaščina, ruščina, ukrajinščina, turščina; vprašaj v kateri koli pisavi (`?`, `¿`, `？`, `؟`, grški `;`) je vprašanje v vseh jezikih.

`replyLogic` doda besede za druge jezike (koda ISO 639):

```json
"replyLogic": { "fi": { "question": ["milloin"], "info": ["milloin", "missä"], "thanks": ["kiitos"], "filler": ["joo"] } }
```

Kategorije: `question` (besede, zaradi katerih je sporočilo vprašanje tudi brez `?`), `info` (vprašalnice po podatku), `howAreYou`, `confused`, `request`, `greeting` (samo na začetku kratkega sporočila), `thanks`, `apology`, `bad`, `good`, `laugh`, `goodbye`, `filler` (»ok«, »ja« – ni odgovor na vprašanje po podatku).

- Navadne besede ali fraze, nikoli regularni izrazi; velike črke in naglasi se ne upoštevajo, ujemajo se cele besede.
- Besede veljajo za pogovore v tem jeziku; ko jezik še ni znan (zelo kratka sporočila), veljajo besede vseh jezikov – izogibaj se kratkim besedam, ki so pogoste v drugih jezikih.
- Do 2.000 besed na modul, do 40 znakov na besedo. Jeziki se pokažejo tudi v **Nastavitve → Jeziki → Jeziki, ki jih govorim**.

Cel primer: [More reply languages](src/more-languages/module.json) (finščina, madžarščina, romunščina, švedščina).

## 7. Brezplačni AI, aplikacije, besedila, teme in skripte

Te razdelke podrobno opisujeta [GUIDE.md](GUIDE.md) in [README.md](README.md). Na kratko: brezplačni AI sme pošiljati samo na znane brezplačne strežnike HTTPS, ključ lastnika gre samo na strežnik, za katerega ga je shranil; prevod začneš z `python tools/mamod.py strings-template …`; besedila o privolitvah, zasebnosti in pogojih ostanejo v angleščini; tema z neberljivim besedilom se ne uporabi; skripte tečejo v zaprtem peskovniku (300 ms, brez omrežja in datotek), `beforePrompt` dobi `kind` `REPLY`, `FORCED`, `OPENER`, `FOLLOW_UP` ali `SUGGESTIONS`, `afterReply` pa vsak odgovor in vsak predlog.

## 8. Preizkus in oddaja

1. `python tools/mamod.py verify modules/<id>.mamod`.
2. Uvozi na telefon in preberi povzetek zmožnosti.
3. Preizkusi v **Test Chat** – nikoli na resničnih ljudeh.
4. **Dnevnik → 📋 Kopiraj podroben dnevnik** pokaže vrstice `module` (nameščeni moduli, napake skript).
5. Odpri pull request s `src/<id>/` in `modules/<id>.mamod`. Pravila so v [README.md](README.md#submit-a-module): brez zavajanja (nikoli zanikati AI), brez zbiranja osebnih podatkov, nič nezakonitega ali škodljivega.
