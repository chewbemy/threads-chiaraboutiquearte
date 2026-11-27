# Bot Threads – ChiaraBoutiqueArte

Pubblica **un post originale ogni 30 minuti** nella fascia di punta (mindfulness, journaling, manifestazione), scritto da Claude e pubblicato con l'API ufficiale di Threads.

- I post si alternano: uno **sul profilo** (senza tag) e uno **in una community** (con il tag della community: Mindfulness, Meditation, Manifestation, Law of Assumption, Astrology Threads).
- **Avvio graduale**: 5 post il primo giorno, poi 8, 11, 14, 17, 20 e dal settimo giorno 24, sempre distribuiti su tutta la fascia. Nei primi due giorni nessun link nei commenti.
- A regime, **un post su tre** riceve un **primo commento** dello stesso account con il link a un prodotto Etsy e il codice **CHIARA20**. Il link non sta mai nel post principale; quello fisso sta in bio.
- **Una volta ogni 24 ore** esce anche un **post fantasma** con una domanda: Threads lo archivia da solo dopo 24 ore e le risposte arrivano nei messaggi privati.
- **Emoji del marchio**: da 1 a 3 per post, solo 💜 🔮 ✨ ⭐ 🌟 💫, variate di volta in volta.
- I capybara sono esclusi.

## File

| File | A cosa serve |
|---|---|
| `bot.py` | Il bot: sceglie tema e formato, fa scrivere il post a Claude, lo controlla, lo pubblica |
| `config.json` | Tutto ciò che puoi cambiare senza toccare il codice: voce, regole, temi, prodotti, codice sconto, frequenza dei link |
| `state/posted.json` | Memoria dei post già usciti (evita doppioni e ripetizioni). La aggiorna il bot da solo |
| `.github/workflows/post.yml` | Avvio del bot (da cron-job.org o a mano) |
| `.github/workflows/refresh-token.yml` | Rinnovo settimanale automatico del token Threads |
| `cleanup.py` + `.github/workflows/cleanup.yml` | Pulizia una tantum dei vecchi post e risposte (solo a mano) |

## Installazione

### 1. Repository
Crea un repository **privato** su GitHub (es. `threads-chiaraboutiquearte`) e carica tutti i file, comprese le cartelle `.github` e `state`.

### 2. App Meta e token Threads
1. Vai su developers.facebook.com → **Crea app** → caso d'uso **Accedi all'API di Threads**.
2. Nel caso d'uso attiva i permessi `threads_basic`, `threads_content_publish` e, per la pulizia iniziale, `threads_delete` e `threads_read_replies`.
3. In **Ruoli dell'app** aggiungi l'account Threads di ChiaraBoutiqueArte come **Tester di Threads**, poi accetta l'invito dall'app Threads (Impostazioni → Account → Autorizzazioni dei siti web → Inviti).
4. Nelle impostazioni del caso d'uso usa il **generatore di token utente** per quell'account e copia il token.

Con l'app in modalità sviluppo e l'account come tester non serve la revisione di Meta. I nomi dei menu di Meta cambiano spesso: se non corrispondono, cerca le stesse voci.

Se il token generato fosse di breve durata (1 ora), convertilo in uno da 60 giorni:

```
curl -G "https://graph.threads.net/access_token" \
  -d grant_type=th_exchange_token \
  -d client_secret=APP_SECRET_DI_THREADS \
  -d access_token=TOKEN_BREVE
```

### 3. Secrets del repository
In **Settings → Secrets and variables → Actions** crea:

| Secret | Valore |
|---|---|
| `ANTHROPIC_API_KEY` | La tua chiave API Anthropic |
| `THREADS_ACCESS_TOKEN` | Il token Threads da 60 giorni |
| `GH_PAT` | Un token GitHub *fine-grained* limitato a questo solo repository, con permesso **Secrets: Read and write**. Serve al rinnovo automatico del token Threads |

Non scrivere mai chiavi o token nei file del repository.

### 4. Prova senza pubblicare
Tab **Actions → Threads post → Run workflow**, spunta **dry_run**. Nel log vedi il post che sarebbe uscito, senza pubblicare nulla.

### 5. Pulizia iniziale (facoltativa, definitiva)
Da fare **prima** di accendere l'orologio. Tab **Actions → Pulizia vecchi post → Run workflow**:

1. Primo avvio con il campo conferma **vuoto**: il log elenca post e risposte che verrebbero cancellati, senza toccare nulla.
2. Se l'elenco è giusto, secondo avvio scrivendo **CANCELLA** nel campo conferma.

La cancellazione non si può annullare. Ogni avvio cancella al massimo 95 elementi, perché Threads limita le cancellazioni giornaliere: se ne restano, il log lo dice e si rilancia il giorno dopo. I post pubblicati dal bot non vengono mai toccati.

### 6. Orario (cron-job.org)
Crea un job come quello dei canali Telegram, che chiama:

```
POST https://api.github.com/repos/TUO_UTENTE/threads-chiaraboutiquearte/actions/workflows/post.yml/dispatches
Header: Authorization: Bearer TOKEN_GITHUB   (permesso Actions: Read and write su questo repository)
Header: Accept: application/vnd.github+json
Body:   {"ref":"main"}
```

Pianificazione: **ogni 30 minuti (:00 e :30), dalle 13:00 alle 00:30, fuso Europe/Madrid**. Va impostata così fin dal primo giorno: è il bot a decidere, a ogni avvio, se pubblicare o saltare in base al giorno dell'avvio graduale.

Il bot controlla anche da solo la fascia (12:00–24:00 UTC in `config.json`): un avvio fuori orario non pubblica nulla. Al cambio dell'ora legale sposta `active_hours_utc` di un'ora.

| Zona | La fascia in ora locale (inverno) |
|---|---|
| Los Angeles | 04:00 – 16:00 |
| Città del Messico, Chicago | 06:00 – 18:00 |
| New York, Bogotá, Lima | 07:00 – 19:00 |
| San Paolo, Buenos Aires | 09:00 – 21:00 |
| Londra | 12:00 – 24:00 |
| Madrid, Roma, Berlino | 13:00 – 01:00 |
| Dubai | 16:00 – 04:00 |
| India | 17:30 – 05:30 |
| Singapore, Manila | 20:00 – 08:00 |
| Tokyo, Seul | 21:00 – 09:00 |

**Minuti di GitHub Actions**: 24 avvii al giorno (anche quelli che saltano contano circa un minuto) sono circa 750–1.500 minuti al mese, e un repository privato ne ha 2.000 gratuiti condivisi con il bot Telegram. Controlla il consumo in Settings → Billing dopo la prima settimana.

## Modifiche frequenti (`config.json`)

- **Fascia oraria**: `active_hours_utc` (ore UTC di inizio e fine).
- **Avvio graduale**: `ramp.posts_per_day` è il numero di post per ciascuno dei primi giorni; finito l'elenco vale `max_posts_per_24h` (24). `ramp.links_from_day` (3) è il giorno da cui partono i commenti con link. `"enabled": false` lo spegne. Il conteggio dei giorni parte dal primo post vero (campo `started` in `state/posted.json`).
- **Rallentare**: se la visibilità cala, abbassa `max_posts_per_24h` o allunga l'elenco di `ramp.posts_per_day`.
- **Codice sconto**: `coupon.code` (ora `CHIARA20`). Il codice deve esistere su Etsy prima del primo avvio vero.
- **Frequenza dei link**: `link_every` (ora 3 = primo commento con link su un post ogni 3; 1 = su ogni post; 0 = mai).
- **Emoji**: `emoji.palette` è l'elenco ammesso, `min` e `max` quante per post. Un post con emoji fuori elenco viene riscritto.
- **Post fantasma**: `ghost.enabled`, `ghost.every_hours` e `ghost.brief` (il tipo di domanda).
- **Community**: `community_every` (2 = un post su due va in una community). L'elenco è in `communities`: `topic_tag` è il nome esatto del tag su Threads, `"active": false` la esclude. "Affirmation" e "Witch Threads" sono già pronte ma spente. Il nome deve coincidere con quello che vedi su Threads.
- **Prodotti**: aggiungi o togli voci in `products`. Ora è escluso l'ebook Grabovoi.
- **Voce e regole**: `voice` e `rules` sono le istruzioni date a Claude.
- **Modello**: `model`.

## Sicurezze incluse

- Fuori dalla fascia oraria, a meno di 20 minuti dall'ultimo post o oltre il tetto del giorno il bot non pubblica, anche se viene avviato più volte.
- Ogni post è confrontato con gli ultimi 40: se è troppo simile, viene riscritto.
- Scartati i post con link, più di un hashtag, frasi da "engagement bait" o oltre 420 caratteri.
- Se il primo commento fallisce, il post resta registrato e non viene ripubblicato.
- Solo API ufficiale: nessun follow, like o messaggio automatico.

## Post animati (dal 27 novembre 2026)

Con `"visual": {"enabled": true}` in `config.json` ogni post normale diventa un video di 8 secondi in loop, viola prugna e oro. I soggetti sono segni zodiacali, Arcani Maggiori, costellazioni, fasi lunari, elementi e pianeti. Il video è fatto interamente dal codice (`visuals/`) e la didascalia nasce da modelli di testo: **costo 0**, niente crediti AI e niente API Claude. Restano attivi solo il post fantasma quotidiano e, se torni ai post di testo, la scrittura dei testi.

- Il ritmo resta quello di prima: la rampa, 24 post al giorno a regime, le community a post alterni (Astrology Threads o Manifestation, in base al soggetto) e il primo commento con link Etsy e CHIARA20 ogni 3 post.
- Non finisce mai: lo stesso soggetto non torna prima di 30 post e ogni video ha una composizione nuova. Il segno di cui è la stagione esce più spesso.
- I video vengono salvati in `media/` e pubblicati tramite jsDelivr, quindi **il repository deve essere pubblico**. I file più vecchi di 3 giorni si cancellano da soli.
- Se un video non si può fare o pubblicare, quel giro esce un post di testo: il bot non si ferma.
- Per tornare ai soli testi: `"enabled": false`.
