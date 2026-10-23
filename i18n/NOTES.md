# Translating the landing page

`en.json` maps a unit id to an English text; `<lang>.json` maps the same ids
to the translation. Some units are HTML: keep every tag and attribute exactly
as it is (only translate the text between tags).

Context and terms:

- The page sells the iPhone app Serai, a vocabulary word-search game. Same
  facts and wording as the App Store description of your language in
  `docs/branding/appstore/listing.csv` of the app repo
  (/Users/christianheuer/git/vocab-tool), which is the reference for tone.
- Terms as the app uses them: `content/ui/<lang>/` in the app repo
  (`glossary_<lang>.csv` if present, `badge.csv` for the six badge names and
  their "… badge" alt texts, `world.csv` for the six world names "The First
  Serai" … "The Keeper's Hall", `topic.csv` for Kitchen, `language.csv` for
  language names, `home.csv`/`hunt.csv` for "found").
- Brand names stay English: Serai, Daily Hunt, Game Center, App Store,
  iPhone, iOS. Level codes A1–C2 stay.
- The expeditions are named as in the app (`brand.csv`: brand.taklamakanCrossing,
  brand.jadeGate, brand.pamirPass); their story and unlock lines are the app's own
  (`expedition.csv`: expedition.taklamakan.*, expedition.jadeGate.*,
  expedition.pamirPass.*; "Word ladder" is the term of
  expedition.pamirPass.sample, singular).
- "Opposite of cold" is the Jade Gate's sample clue: the app's `hunt.opposite`
  (`hunt.csv`) with {word} = cold. "cold" and the answer HOT stay English (the
  clue word is in the language being learned).
- The Jade Gate has no price yet: never add one. The Pamir Pass costs €4.99.
- The Pamir Pass's sample ladder is English (BOOT, FOOT, FOOD, MOOD, MOON:
  the reader learns English), so its clues `Stiefel`, `Fuß`, `Essen`,
  `Laune`, `Mond` become the words for boot, foot, food, mood (state of
  mind), moon in YOUR language, like the demo board's clues.
- The demo board's answers are English (SPOON, BREAD, CUP, TEA): the reader
  of your page speaks your language and learns English. So the clue words
  `Löffel`, `Brot`, `Tasse`, `Tee` become the words for spoon, bread, cup,
  tea in YOUR language (lowercase or capitalised as your language writes a
  dictionary noun), and "Löffel · SPOON" becomes "<your spoon> · SPOON";
  "Brot · 5" keeps the 5 (letters of BREAD); "Tee · 3" keeps 3.
- "You eat soup with it" is the app's description clue of spoon: use the
  app's own one from `content/dictionary/desc/<lang>_NN.csv` (row id
  `spoon`), so the page matches the app.
- "2/4 found": keep "2/4".
- "Coming soon on the" + "App Store" form Apple's badge ("Coming soon on the
  App Store"): translate as Apple's localized badge does (e.g. German "Bald
  im" + "App Store").
- "Language" labels the list of the page's languages.
- Keep it natural for your market; no superlatives. Russia: the purchase
  cannot be bought there, but the text stays as is.
