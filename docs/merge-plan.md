# Merge-plan: runner v2

Plan för att bygga om runnern efter `MERGE_SPEC.md`. UI och interaktion kommer från
`ccna-ovningsprov.html`. Allt arbete sker i `~/kod/ccnatester-v2` på grenen `v2`.
Originalmappen och den publicerade sajten rörs inte.

Banken (`bank/`), generatorerna, `validate.py` och `stats.py` skrivs inte om. De enda
ändringarna i `validate.py` är de som står under *Schemaändringar*.

---

## 1. Befintliga funktioner i nuvarande runner (`app/app.js`, `index.html`)

| # | Funktion | Detalj |
|---|---|---|
| E1 | Laddar `bank.json` via `fetch()` | Visar felruta med instruktion när sidan öppnas via `file://` |
| E2 | Startsida med bankens täckning | Tabell per domän: vikt, antal items, per 100 |
| E3 | Partiell bank | Notis och omnormaliserade vikter när domäner saknas. Används inte längre eftersom banken är komplett |
| E4 | Provlängd | 10/25/50/75/100 och max som banken klarar. 1,2 min per fråga, 100 frågor = 120 min |
| E5 | Domänviktat urval | Largest-remainder-allokering per blueprintvikt. Slumpat inom domän och därefter slumpad ordning |
| E6 | Slumpad alternativordning | Per item och försök. Bokstäverna A–E sätts efter position |
| E7 | Timer | Pausar aldrig. Bärnsten vid ≤10 min, röd vid ≤2 min. Försöket lämnas in automatiskt vid 0 |
| E8 | Inget back, ingen skip | Ett bekräftat svar är slutgiltigt |
| E9 | Bekräfta-knapp | Aktiv först när exakt `select_count` alternativ är valda. Vid multi avmarkeras det äldsta valet om man väljer för många |
| E10 | Multi | Kryssrutor med texten "Choose N". Rättas allt-eller-inget |
| E11 | Ingen feedback under provet | Bara räknaren "Question X of Y" |
| E12 | **Unsure-markering** | Kryssruta och tangenten `U`. Påverkar inte poängen och styr bara vad granskningen förklarar |
| E13 | Exhibit | `cli_output`/`config`/`topology` i `<pre>` med rubrik. Scroll återställs per fråga |
| E14 | Kommandon i monospace | `looksLikeCommand()`, en prefixlista med `ip `, `show `, `R1(`… |
| E15 | Tangentbord | `1–5`/`A–E` väljer, `U` växlar unsure, `Enter` bekräftar |
| E16 | Skydd mot att lämna sidan | `beforeunload` medan ett försök pågår |
| E17 | Resultat: poäng | Procent, "X of Y correct", "time expired", antal unsure, förfluten tid och sluttid |
| E18 | Resultat per domän | Tabell med frågade, kvot, rätt och andel med mätare |
| E19 | Resultat per objektiv | Tabell sorterad efter objektiv-id |
| E20 | Granskning i tre nivåer | Missade, rätt men unsure, och en hopfälld "Every item" som byggs lat |
| E21 | Granskningskort i bankordning | Alternativen visas i bankens ordning med `id` som bokstav så att förklaringarnas "Option C" stämmer. Markeringarna `correct ✓` / `you ✗` och en notis om att bokstäverna skiljer sig från provet |
| E22 | Export JSON | `run.report`: timestamp, duration, score{correct,total,percent,marked_unsure}, per_domain, per_objective, missed[], unsure_correct[] |
| E23 | Export Markdown | Kopieras till urklipp med fallback via `execCommand`. Tabeller per domän och objektiv samt listor över missade och unsure |
| E24 | Nytt försök | `location.reload()` |
| E25 | Tema | Ljust och mörkt via `prefers-color-scheme` och `prefers-reduced-motion` |
| E26 | Ingen lagring | Uttalat i `app.js`-headern: kärnflödet fungerar med lagring avstängd |
| E27 | `app/lab-tasks.md` | Packet Tracer-uppgifter. Ligger kvar och länkas från startsidan |

**Saknas, trots att specen antar att de finns:** *flaggning* (startsidan säger uttryckligen
"no flagging") och *poängskala*, eftersom bara procent visas. Se K1 och K2.

## 2. Funktioner från referensfilen som ska in

| # | Funktion |
|---|---|
| R1 | Design-tokens: ljust och mörkt tema med `data-theme`-override, Barlow, Barlow Semi Condensed och JetBrains Mono, max 760 px, vänsterställt |
| R2 | Portpanel: en "lampa" per fråga (grå/grön/röd/aktuell). Rubriken visar "Fråga X av Y" och "Poäng" |
| R3 | Frågekort: tagg, frågenummer, alternativ som knappar med bokstavscirkel |
| R4 | Direkt feedback: rätt alternativ grönt, fel val rött, övriga nedtonade. Feedbackruta med vänsterkant och förklaring |
| R5 | Rutan "Korrigerad fråga" (`.fix`, gul) |
| R6 | Föregående, Nästa, "Avsluta och visa resultat" |
| R7 | Tangentbord: A–D/1–4 svarar direkt, Enter går till nästa |
| R8 | `isCode()` för monospace i alternativ |
| R9 | localStorage med resume: "Fortsätt (X av Y besvarade)" |
| R10 | Kryssrutan "Blanda frågornas ordning" |
| R11 | Resultat: stor poäng, verdict-text, rutan "Områden att förbättra", staplar per område sorterade svagast först med 70 % som gräns |
| R12 | Granskningslista "Alla svar" med filtret "Visa bara felsvar" och utfällbar förklaring |
| R13 | "Öva på de N felsvarade" och "Börja om" |

Referensfilens **frågor** tas inte in. De kommer från en kommersiell kurs (Kevin
Wallace Training), och README:n lovar "Nothing is copied". Filen används bara som
mall för UI och beteende.

## 3. Nytt enligt specen (finns i ingen av de två)

Filter för övningsläget (domän/objektiv och svårighetsgrad), drag-and-drop, `note`-fältet,
F för flagga, klickbara portar, poäng per objektiv under varje domän, de skills med flest
fel, fördelning per svårighetsgrad, historik med trend, icke-repeterande provurval,
Markdown med frontmatter och layout ned till 360 px.

---

## 4. Konflikter och förslag

**K1. Flaggning finns inte, men unsure gör.** Med no-back går det inte att återvända
till en flaggad fråga, så en separat flagga vore samma sak som unsure.
→ *Förslag:* slå ihop dem till **en** markering som heter "flaggad / osäker". Både `F`
och `U` växlar den. Portpanelen visar den som flaggad. I JSON-exporten behålls
fältnamnen `marked_unsure`/`unsure` så att formatet inte bryts.

**K2. Poängskalan finns inte.** Cisco publicerar varken skala eller gräns, och
referensfilen säger det själv. En påhittad skala som 825/1000 går emot bankens
ärlighetsprincip.
→ *Förslag:* ingen skala. Provläget visar procent, referensfilens verdict-text och
"sikta på 85 %". Om du vill ha en skala ändå bygger jag den som en uttryckligen
*inofficiell* linjär 300–1000-skala.

**K3. Bokstäverna i förklaringarna gäller bankordningen.** 296 av 300 förklaringar
säger "Option C …". Övningsläget visar förklaringen direkt under frågan, så med
blandade alternativ skulle den peka på fel rad.
→ *Förslag:* **övningsläget visar alltid alternativen i bankordning** och bokstaven är
`option.id`. "Blanda" gäller bara frågornas ordning. Provläget blandar alternativen
som idag, och granskningen använder bankordning som idag (E21).

**K4. Ett klick svarar direkt, men ett svar i provläget är slutgiltigt.** Ett felklick
eller en tangent av misstag kan inte ångras under provet.
→ *Förslag:* i övningsläget svarar ett klick eller A–E/1–5 direkt, som i referensen. I
provläget väljer klick och tangent, och sedan bekräftar `Enter` eller *Svara*. Det
behåller E9.

**K5. Drag-and-drop.** Banken har 0 sådana items, och `validate.py` avvisar typen med
flit eftersom den inte gick att använda med tangentbord. Specens krav på en dropdown
per mål tar bort just den invändningen.
→ *Förslag:* schemat blir `type: "draganddrop"`, `options` (källorna), `targets:
[{id,text}]`, `correct: {targetId: optionId}` och `select_count = len(targets)`. Engine,
UI och tester bygger jag nu, och testerna körs mot fixtures i `tests/`.
`VALID_TYPES` utökas i samma commit som engine, med schemakontroller för typen.
**Banken får inga DnD-items i v2.** Att lägga till items bryter kvoterna, och att byta
ut befintliga är ett separat författarjobb (se bank-invarianterna).

**K6. "exhibit" är inte en typ** utan fältet `exhibit.kind`. Typerna i schemat är
`single`, `multi` och (nya) `draganddrop`. `topology` är ASCII och renderas i samma
`<pre>` som CLI.

**K7. A–D i referensen, men 31 items har 5 alternativ.** → Tangenterna gäller A–E/1–5,
som idag.

**K8. `isCode()` och `looksLikeCommand()` skiljer sig.** Referensens regex (`#` eller
`/` i början) missar nästan alla bankens kommandon. → Behåll `looksLikeCommand()` och
utöka listan med `R\d+#` och `switchport `.

**K9. Ingen lagring blir localStorage.** Det vänder E26. Specen styr: nyckeln
`ccna-runner-v2`, alla anrop i try/catch, och utan lagring fungerar allt utom resume
och historik.
**Resume i provläget:** klockan räknas från `startedAt`, alltså väggklocka, så den
fortsätter även när fliken är stängd. Det följer "the clock never pauses". Om tiden
har gått ut vid återupptagandet lämnas försöket in direkt.

**K10. Mobil.** `PLAN.md` säger att mobil uttryckligen inte är ett mål (88 % av
exhibits är bredare än en telefon). Specen kräver nu 360 px.
→ Specen styr. Exhibits får horisontell scroll och radbryts aldrig. Jag uppdaterar
avsnittet i `PLAN.md` så att beslutet inte står kvar som giltigt.

**K11. Export.** Båda formaten finns redan, så de behålls.
→ JSON behåller sina fält, och fälten `mode`, `per_skill` och `per_difficulty` läggs
till utan att något tas bort. Markdown behåller sin brödtext och får YAML-frontmatter
överst (datum, läge, poäng, missade objektiv). Kopiera finns kvar och knappen *Ladda ner
.md* läggs till för Obsidian.

**K12. Offline mot Google Fonts.** README lovar offline, och `file://` kan sakna nät.
→ Lägg fonterna lokalt som woff2 i `app/fonts/` (OFL-licens) och ta med licensfilen.

**K13. Skills.** Det finns 601 olika skills på 300 items, så "flest fel" blir mest
ettor. → Visa topp 5 skills med minst 2 fel inom domänen, och dölj listan om ingen
skill har det.

**K14. Språk.** Referensen är på svenska, runnern och banken på engelska, och sajten
är publik på engelska.
→ *Förslag:* UI-texten på **svenska**, som specens etiketter ("Välj N", "missad",
"Korrigerad fråga" …). Items stannar på engelska. Strängarna samlas i ett objekt i
`ui.js`, så att det går att lägga till engelska senare.

**K15. Portpanel och navigering.** Portarna är klickbara i övningsläget. I provläget
gäller no-back, så där är de aldrig klickbara och visar bara
besvarad/obesvarad/flaggad. Panelrubrikens "Poäng" döljs i provläget.
Med 100 portar blir det 4 rader à 25 kolumner, och 20 kolumner under 520 px.

**K16. Övningsläget, back och historik.** Referensen räknar bara besvarade frågor. Så
blir det i övningsläget. I provläget räknas obesvarade som fel, som idag.

**K17. Avsluta i förtid.** Referensen har "Avsluta och visa resultat". I provläget
lämnas försöket in efter en bekräftelsedialog, och obesvarade räknas som fel. Det är
nytt men ofarligt.

**K18. `beforeunload`** stannar kvar i provläget även med resume, eftersom klockan
fortsätter gå.

**K19. Icke-repeterande urval.** 300/100 ger exakt 3 prov utan överlapp i varje domän,
eftersom 60/20 = 75/25 = 30/10 = 45/15 = 3. Engine väljer per domän först items som
inte setts i provläget, därefter de som setts äldst. "Setts" sparas som `{itemId:
senast sedd}`. Övningsläget påverkar inte detta.

**K20. CI.** `build_bank.py` skriver både `app/bank.json` och `app/bank.js`.
`pages.yml` får steget `node --test` före bygget.

## 5. Arkitektur

- `engine.js` är ett **klassiskt script**, inte en ES-modul, eftersom Chrome blockerar
  moduler över `file://`. Det sätter `window.Engine` och avslutar med `if (typeof
  module !== 'undefined') module.exports = Engine` så att `node --test` kan `require`:a
  det.
- Urvalsfunktionerna tar en injicerbar RNG (`rng = Math.random`), så att test av kvoter
  och icke-repetition blir deterministiska.
- Rättning: single och multi som mängdlikhet, DnD som att varje mål har rätt källa.
  Allt-eller-inget.
- Ett state-objekt serialiseras med `version: 2` och läses tillbaka med validering.
  Ett trasigt eller okänt state kastas och påverkar inte appen.

### Schemaändringar (`validate.py`, samma commit som engine)

- `note` blir ett tillåtet men frivilligt fält: en sträng som inte får vara tom om den
  finns.
- `draganddrop` läggs till i `VALID_TYPES` med kontroller för `targets`,
  `correct`-mappningen och `select_count`. Kommentaren om varför typen togs bort
  ersätts.
- Alla befintliga kontroller är oförändrade, och hela banken ska vara grön före och
  efter.

## 6. Filstruktur efter ombyggnaden

```
app/
  index.html        skal: <script src="bank.js">, engine.js, ui.js
  styles.css        tokens och komponenter, portade från referensen (ersätter style.css)
  engine.js         rena funktioner, ingen DOM
  ui.js             rendering, event, tangentbord, lagring och export
  bank.json         byggd (som idag)
  bank.js           byggd: window.BANK = {...}
  fonts/            Barlow, Barlow Semi Condensed, JetBrains Mono (woff2) och LICENSE-*.txt (OFL)
  lab-tasks.md      oförändrad
tests/
  engine.test.js    node --test
  fixtures.js       små syntetiska items, inklusive DnD
docs/
  merge-plan.md     det här dokumentet
scripts/            oförändrat, utom build_bank.py (bank.js) och validate.py (schema)
```

`app/app.js` och `app/style.css` tas bort när v2 täcker allt. Git-historiken och mappen
`~/kod/ccnatester` har dem kvar.
`ccna-ovningsprov.html` och `MERGE_SPEC.md` hålls utanför git via `.gitignore`.
Referensfilen innehåller kommersiellt frågematerial och repot är publikt.

## 7. Commit-ordning

1. `engine.js` och tester, plus schemaändringen i `validate.py`
2. `build_bank.py` skriver `bank.js`, plus UI-skal, `styles.css` och fonter
3. Övningsläget, inklusive filter, feedback och DnD-UI
4. Provläget: timer, no-back, flagga/unsure och portpanel utan färger
5. Resultatsidan
6. Persistens: resume, historik, trend och icke-repeterande urval. Export: JSON, MD och
   frontmatter. Uppdatering av CI, README och PLAN.md

## 8. Beslut (2026-10-16)

1. **Publicering:** v2 får ett eget GitHub-repo med egen Pages-adress, och v1 lever kvar parallellt.
   Ingen push görs förrän repot finns och push är godkänd.
2. **K1:** flagga och unsure slås ihop. `F` och `U` styr samma markering.
3. **K2:** ingen poängskala, bara procent och verdict.
4. **K14:** UI-texten är på **engelska**, inte svenska. Specens svenska etiketter översätts:
   "Choose N", "missed", "Corrected question", "Resume (X of Y answered)",
   "Areas to improve", "Practise the N missed".
5. Övriga förslag (K3–K13, K15–K20) är godkända som de står.

## 9. Avstämning mot v1 (före sista commit)

Alla punkter i avsnitt 1 är kontrollerade mot v2. ✓ betyder att funktionen finns
kvar som den var. Övriga rader beskriver vad som har ändrats.

| # | Status i v2 |
|---|---|
| E1 | Ersatt: `bank.js` laddas via `<script>`, och om den saknas visas en instruktion |
| E2 | ✓ Under "Bank coverage" (hopfälld) |
| E3 | **Borttagen notis.** Urvalet hanterar fortfarande en partiell bank (`availableDomains`/`maxAttempt`), men den förklarande texten visas inte längre. Banken är komplett och bygget kräver det |
| E4–E11 | ✓ (E9: det äldsta valet släpps fortfarande vid multi) |
| E12 | ✓ Ihopslagen med flaggan (K1). `F` och `U` gör samma sak |
| E13 | ✓ Exhibits har dessutom tangentbordsfokus för att kunna scrollas |
| E14 | ✓ Utökad med de prefix banken använder |
| E15 | ✓ Plus `F` och ←/→ i övningsläget |
| E16 | ✓ |
| E17 | ✓ Antal flaggade står i metaraden |
| E18 | Ändrad: staplar med svagast först. **Kolumnen "Quota" (per 100) har tagits bort** från resultatet. Den står fortfarande under Bank coverage |
| E19 | ✓ Under varje domän, svagast först |
| E20 | Ändrad: tre nivåer har blivit en lista med filtren "only wrong" och "only flagged" (allt visas som standard). Förklaringarna byggs först när de fälls ut, som i v1 |
| E21 | ✓ Inklusive notisen om bokstäver i provläget |
| E22 | ✓ Samma fält. `mode`, `expired`, `score.unanswered`, `per_difficulty` och `per_skill` har lagts till |
| E23 | ✓ Samma brödtext, med frontmatter. Knappen *Download Markdown* har lagts till |
| E24 | ✓ "New attempt" går till startsidan i stället för att ladda om sidan |
| E25 | ✓ Plus en temaknapp (auto/light/dark) |
| E26 | Vänd (K9) |
| E27 | ✓ Länkad från startsidan |

### Kända begränsningar

- **Portarna är en genväg för mus och pekskärm** (`tabindex="-1"`). Med tangentbord
  går man mellan frågor med ←/→ eller Previous/Next, men det går inte att hoppa
  direkt till fråga N. Valet är medvetet: 100 tabbstopp före frågan vore värre.
- **DnD är bara testat med ett injicerat fixture-item** och syntetiska drag-events.
  Banken har inga DnD-items. En verklig musdragning har inte provats.
