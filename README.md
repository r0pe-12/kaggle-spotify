# Spotify Global Trends 2026 - Napredna analiza dataseta

## O projektu

Ovaj projekat predstavlja sveobuhvatnu analizu dataseta **Spotify Global Trends 2026** koji sadrži podatke o 178 trending pjesama sa Spotify platforme. Dataset uključuje informacije o streamovima, viralnosti, trendovima, žanrovima, zemljama porijekla i dugovječnosti pjesama na listi.

Analiza je realizovana u programskom jeziku **Python** korišćenjem biblioteka `pandas`, `numpy`, `matplotlib` i `seaborn`, a podijeljena je u 9 glavnih sekcija koje pokrivaju sve aspekte obrade podataka - od čišćenja i eksploracije do napredne statističke analize i vizualizacije.

Cilj projekta je demonstrirati kako se od sirovih podataka (CSV fajla) dolazi do korisnih zaključaka i vizuelnih prikaza, prolazeći kroz kompletan pipeline obrade podataka koji se koristi u industriji i akademskom istraživanju.

---

## Struktura dataseta

Dataset (`spotify_global_trends_2026.csv`) sadrži **178 redova** (svaki red je jedna pjesma) i **13 kolona**. U nastavku je objašnjenje svake kolone, njenog tipa podataka i šta ta kolona konkretno predstavlja:

| Kolona | Tip | Detaljno objašnjenje |
|--------|-----|----------------------|
| `track_name` | string | Naziv pjesme onako kako je prikazan na Spotify platformi. Ovo je tekstualni podatak koji služi kao identifikator pjesme. |
| `artist_name` | string | Ime izvođača ili benda koji je objavio pjesmu. Jedan artist može imati više pjesama u datasetu (npr. BTS ima 15 pjesama). |
| `streams` | int | Trenutni ukupni broj streamova (reprodukcija) koje je pjesma ostvarila. Ovo je ključna metrika popularnosti - svaki put kad neko pusti pjesmu na Spotify, to se broji kao jedan stream. Vrijednosti u datasetu se kreću od 1,191,777 do 11,273,830. |
| `stream_change` | int | Promjena broja streamova u odnosu na prethodni period. Pozitivna vrijednost znači da pjesma dobija nove streamove brže nego prije (raste), a negativna vrijednost znači da gubi popularnost (opada). Na primjer, vrijednost -3,370,522 znači da je pjesma izgubila toliko streamova u odnosu na prethodni mjereni period. |
| `7day` | int | Ukupan broj streamova koje je pjesma ostvarila u poslednjih 7 dana. Ova metrika je korisna jer pokazuje trenutnu popularnost pjesme, za razliku od ukupnih streamova koji su kumulativni. Npr. pjesma koja ima 5 miliona ukupnih streamova ali samo 100,000 u poslednjih 7 dana vjerovatno gubi popularnost. |
| `genre` | string | Muzički žanr kojim je pjesma klasifikovana. U datasetu postoji 39 različitih žanrova - od masovnih (Pop, Rock, K-Pop) do nišnih (Swamp Rock, Nu Metal, Dolby Atmos). Žanr je kategorička varijabla koja nam omogućava grupnu analizu. |
| `country` | string | Zemlja porijekla izvođača, označena ISO kodom (US, GB, KR...) ili punim imenom (England, Florida). U datasetu je zastupljeno 19 različitih zemalja/regija. Ovo nam omogućava geografsku analizu muzičkih trendova. |
| `pos` | int | Trenutna pozicija pjesme na Spotify trending listi. Vrijednost 1 znači da je pjesma na prvom mjestu (najpopularnija), a 200 je najniža pozicija u datasetu. Niža vrijednost = bolja pozicija. |
| `days` | int | Broj dana koliko je pjesma neprekidno prisutna na trending listi. Ova metrika direktno mjeri dugovječnost - pjesma sa 2 dana je tek stigla na listu, dok pjesma sa 3,070 dana je na listi više od 8 godina. |
| `viral_score` | int | Kompozitni skor viralnosti koji Spotify računa na osnovu brzine širenja pjesme, dijeljenja, dodavanja na playliste i drugih faktora. Viši viral_score znači da se pjesma brže širi među korisnicima. Vrijednosti se kreću od 3,774,959 do 42,333,693. |
| `trend` | string | Smjer u kom se kreće popularnost pjesme. Ima samo dvije moguće vrijednosti: **Rising** (pjesma raste u popularnosti, dobija sve više streamova) i **Falling** (pjesma gubi popularnost, streamovi opadaju). |
| `popularity_category` | string | Kategorija popularnosti koju Spotify dodjeljuje na osnovu ukupnih performansi. **Trending** znači da je pjesma trenutno u eksplozivnom rastu i privlači masovnu pažnju, dok **Average** znači da je na standardnom nivou popularnosti za trending listu. |
| `longevity` | string | Klasifikacija dugovječnosti pjesme na listi. **New** - pjesma je tek stigla (obično manje od 30 dana), **Stable Hit** - pjesma je stabilno prisutna srednje dugo, **Evergreen** - pjesma je na listi već veoma dugo i kontinuirano privlači slušaoce. |

---

## Detaljno objašnjenje svake sekcije analize

### 1. Učitavanje i čišćenje podataka

**Šta radimo i zašto je to važno:**

Prije bilo kakve analize, moramo podatke učitati u memoriju i provjeriti njihov kvalitet. Ovo je najvažniji korak jer sve ostale analize zavise od kvaliteta ulaznih podataka - ako su podaci nepotpuni, duplirani ili nekonzistentni, svi rezultati koji slijede biće nepouzdani. U industriji se procjenjuje da data science stručnjaci provode 60-80% svog vremena upravo na čišćenju podataka.

**Kako to radimo korak po korak:**

1. **Učitavanje CSV fajla** - Koristimo `pd.read_csv()` funkciju iz pandas biblioteke. Ova funkcija čita CSV (Comma-Separated Values) fajl i pretvara ga u DataFrame - tabelarnu strukturu podataka u memoriji sa kojom možemo raditi. Pandas automatski prepoznaje tipove podataka (brojeve, stringove) na osnovu sadržaja svake kolone.

2. **Provjera dimenzija** - Sa `df.shape` provjeravamo koliko redova i kolona ima dataset. Ovo je osnovna sanitarna provjera - da li smo učitali onoliko podataka koliko očekujemo. U našem slučaju to je 178 redova × 13 kolona.

3. **Provjera tipova podataka** - Sa `df.dtypes` provjeravamo da li je pandas ispravno prepoznao tipove. Na primjer, kolona `streams` treba biti `int64` (cijeli broj), a `genre` treba biti `str` (string/tekst). Pogrešan tip može uzrokovati greške u računanju - ako bi streams bio učitan kao string "1234" umjesto broja 1234, ne bismo mogli računati prosjek.

4. **Detekcija null (nedostajućih) vrijednosti** - Sa `df.isnull().sum()` brojimo koliko null vrijednosti postoji u svakoj koloni. Null vrijednost znači da podatak nedostaje - npr. da pjesma nema upisan žanr ili broj streamova. Null vrijednosti mogu uzrokovati greške u računanju (npr. prosjek kolone koja sadrži null neće biti tačan) pa ih moramo identificirati i odlučiti kako ih tretirati (izbrisati red, popuniti prosječnom vrijednošću, itd.). U našem datasetu nema null vrijednosti, što je idealan scenario.

5. **Detekcija duplikata** - Sa `df.duplicated().sum()` provjeravamo da li postoje potpuno identični redovi. Duplikati mogu nastati greškom pri prikupljanju podataka i iskrivili bi rezultate - npr. ako je ista pjesma dva puta u datasetu, njen žanr bi bio prebrojat dvostruko. Ako pronađemo duplikate, uklanjamo ih sa `df.drop_duplicates()`.

6. **Čišćenje stringova** - Sa `str.strip()` uklanjamo nepotrebne razmake (whitespace) sa početka i kraja svih tekstualnih vrijednosti. Ovo je važno jer "Pop" i " Pop" (sa razmakom) bi bili tretirani kao dva različita žanra pri grupiranju, iako su zapravo isti.

7. **Validacija logike** - Provjeravamo da li postoje logički nemogući podaci, poput negativnih streamova. Negativan broj streamova nema smisla u realnom svijetu i bio bi indikator greške u podacima.

**Rezultat:** Nakon ovog koraka imamo čist, validiran dataset spreman za analizu. U našem slučaju, dataset je bio u odličnom stanju - bez null vrijednosti, bez duplikata, sa ispravnim tipovima podataka.

---

### 2. Eksplorativna analiza podataka (EDA)

**Šta radimo i zašto je to važno:**

EDA (Exploratory Data Analysis) je sistematičan pristup razumijevanju dataseta prije nego što krenemo u specifične analize. Cilj je stvoriti "mentalnu mapu" podataka - razumjeti raspon vrijednosti, identificirati obrasce i anomalije, i formulisati hipoteze koje ćemo kasnije testirati. Bez EDA bismo radili analize naslijepo, bez razumijevanja sa čime radimo.

**Kako to radimo korak po korak:**

1. **Deskriptivna statistika numeričkih kolona** - Koristimo `df.describe()` koji za svaku numeričku kolonu računa 8 ključnih statističkih mjera:
   - **count** - ukupan broj ne-null vrijednosti (178 za sve kolone)
   - **mean** (aritmetička sredina) - prosjek svih vrijednosti. Za streams je 2,093,366 što znači da prosječna trending pjesma ima oko 2 miliona streamova
   - **std** (standardna devijacija) - mjera raspršenosti podataka oko prosjeka. Za streams je 1,277,789 što je relativno visoko u odnosu na prosjek, ukazujući na veliku varijabilnost
   - **min** i **max** - najniža i najviša vrijednost. Streams ide od 1,191,777 do 11,273,830 - razlika od skoro 10×
   - **25%** (Q1), **50%** (medijan/Q2), **75%** (Q3) - kvartili koji dijele podatke na četiri jednaka dijela. Medijan streamova (1,590,738) je znatno manji od prosjeka (2,093,366), što ukazuje na pozitivno iskrivljenu distribuciju (mali broj pjesama sa ekstremno visokim streamovima povlači prosjek naviše)

2. **Frekvencijska analiza kategoričkih kolona** - Za svaku kategoričku kolonu (genre, country, trend, popularity_category, longevity) koristimo `value_counts()` koji broji koliko puta se svaka vrijednost pojavljuje i sortira opadajuće. Dodajemo i procenat da bismo razumjeli relativnu zastupljenost. Na primjer, otkrivamo da:
   - **Pop** dominira sa 53 pjesme (29.8%), dok mnogi žanrovi imaju samo 1-2 pjesme
   - **US** je ubjedljivo najzastupljenija zemlja sa 79 pjesama (44.4%)
   - **Falling** trend ima 137 pjesama (77%) vs samo 41 Rising (23%)
   - **Average** popularity kategorija ima 173 od 178 pjesama (97.2%) - samo 5 je Trending
   - **Evergreen** longevity ima 128 pjesama (71.9%) - većina trending pjesama je dugotrajna

**Rezultat:** Sada imamo jasnu sliku dataseta. Znamo da je distribucija neravnomjerna (malo pjesama sa mnogo streamova, mnogo pjesama sa manje), da je većina pjesama u padu, da Pop i US dominiraju, i da je većina pjesama na listi već dugo vremena.

---

### 3. Analiza po žanrovima

**Šta radimo i zašto je to važno:**

Žanr je jedna od najvažnijih kategoričkih varijabli u muzičkim podacima jer direktno utiče na ciljanu publiku, marketing strategije i predviđanje trendova. Želimo razumjeti ne samo koji žanrovi imaju najviše streamova, već i koji žanrovi rastu, a koji opadaju - što je mnogo korisnije za predviđanje budućih trendova.

**Kako to radimo korak po korak:**

1. **Grupna agregacija** - Koristimo `df.groupby('genre').agg()` koji grupiše sve pjesme istog žanra zajedno i za svaku grupu računa višestruke statistike:
   - `broj_pjesama` (count) - koliko pjesama ima svaki žanr
   - `ukupni_streamovi` (sum) - zbir svih streamova za taj žanr
   - `prosjecni_streamovi` (mean) - prosjek streamova po pjesmi unutar žanra
   - `prosjecni_viral` (mean) - prosječna viralnost žanra
   - `prosjecni_stream_change` (mean) - da li žanr u prosjeku raste ili pada
   - `max_streams` (max) - najpopularnija pjesma žanra

   Razlika između ukupnih i prosječnih streamova je ključna: Pop ima najviše ukupnih streamova (96.8M) jer ima najviše pjesama (53), ali K-Pop ima daleko veći prosjek po pjesmi (4.85M vs 1.83M za Pop) jer ima samo 15 ali izuzetno popularnih pjesama.

2. **Identifikacija rastućih žanrova** - Sortiramo žanrove po prosječnom `stream_change` opadajuće da nađemo koji žanrovi dobijaju sve više slušalaca. Rezultat: Special Purpose Artist, Contemporary R&B i Girl Group su u najvećem rastu.

3. **Identifikacija opadajućih žanrova** - Sortiramo rastući da nađemo žanrove u najvećem padu. K-Pop je daleko ispred sa prosječnim padom od -2,568,046, što je posljedica toga da su sve BTS pjesme tek 2 dana na listi i u fazi prirodnog opadanja nakon inicijalnog eksplozivnog starta.

**Rezultat:** Pop dominira volumenom ali ne intenzitetom. K-Pop ima najveći intenzitet ali je u najvećem padu. Regional Mexicano i Contemporary R&B su žanrovi u usponu. Ovi uvidi bi bili korisni za muzičke etikete i playlist kuratora.

---

### 4. Analiza po zemljama

**Šta radimo i zašto je to važno:**

Muzika je globalni fenomen, ali različite regije proizvode različite tipove muzike i imaju različite nivoe uticaja na globalnu scenu. Geografska analiza otkriva kulturološke muzičke identitete i pokazuje koji muzički centri dominiraju globalno.

**Kako to radimo korak po korak:**

1. **Grupna agregacija po zemlji** - Identičan pristup kao za žanrove, ali grupisano po `country` koloni. Računamo broj pjesama, ukupne i prosječne streamove, i prosječnu viralnost za svaku zemlju.

2. **Identifikacija dominantnog žanra po zemlji** - Za svaku od top 10 zemalja filtriramo dataset na samo tu zemlju (`df[df['country'] == country]`), zatim sa `value_counts()` pronalazimo koji žanr se najčešće pojavljuje. Ovo otkriva kulturološke veze:
   - **US → Pop** (34 od 79 pjesama) - Amerika proizvodi dominantno pop muziku
   - **KR → K-Pop** (15 od 17) - Južna Koreja je gotovo isključivo K-Pop
   - **GB → Rock** (8 od 25) - Britanija ima jaku rock tradiciju
   - **PR → Reggaeton** (7 od 9) - Portoriko je centar Reggaetona
   - **MX → Regional Mexicano** (6 od 8) - Meksiko sa svojim regionalnim žanrom
   - **CA → R&B** (4 od 10) - Kanada sa R&B (Drake, The Weeknd efekat)

3. **Poređenje ukupnih vs prosječnih streamova** - Važna distinkcija: US ima ubjedljivo najviše ukupnih streamova (144M), ali KR ima mnogo veći prosjek po pjesmi (4.48M vs 1.82M). To znači da Južna Koreja ima manje pjesama na listi, ali su one u prosjeku mnogo popularnije. Florida (samo 2 pjesme) ima čak 4.13M prosjek - ali to je previše mali uzorak za pouzdane zaključke.

**Rezultat:** US je globalni muzički centar po volumenu, ali po intenzitetu (prosječni streamovi) prednjače Južna Koreja i Portoriko. Svaka zemlja ima jasno prepoznatljiv žanrovski identitet.

---

### 5. Trend analiza

**Šta radimo i zašto je to važno:**

Ovo je možda najkompleksnija sekcija jer kombinuje više dimenzija analize. Trend (Rising vs Falling) je ključna varijabla za razumijevanje dinamike muzičkog tržišta - ne samo koliko je nešto popularno SADA, već u kom SMJERU se kreće. Dodatno analiziramo longevity (dugovječnost) i popularity_category da stvorimo kompletnu sliku životnog ciklusa trending pjesama.

**Kako to radimo korak po korak:**

1. **Poređenje Rising vs Falling** - Grupišemo po `trend` koloni i računamo prosjeke svih ključnih metrika. Otkrivamo bitne razlike:
   - Falling pjesme imaju veće prosječne streamove (2,150,032 vs 1,904,022) - to je zato što pjesme obično dostignu vrhunac pa onda počnu padati, tako da pjesme u padu su već na visokom nivou
   - Rising pjesme imaju pozitivan prosječni stream_change (+56,444) dok Falling imaju negativan (-370,277) - ovo je očekivano po definiciji
   - Rising pjesme imaju nešto veći prosječan broj dana na listi (573 vs 525) - duže prisutne pjesme koje još uvijek rastu su pravi Evergreen hitovi

2. **Žanrovi sa najviše Rising pjesama** - Ne gledamo samo apsolutni broj Rising pjesama po žanru, već i procenat. Ovo je važno jer Pop ima najviše Rising pjesama (11), ali to je samo 21% od svih Pop pjesama. Sa druge strane, Regional Mexicano ima 7 Rising od ukupno 8 pjesama (88%) i New Wave ima 3 od 3 (100%). Procenat daje mnogo bolju sliku od apsolutnog broja jer normalizuje za veličinu žanra.

3. **Longevity analiza** - Grupišemo po longevity kategoriji i otkrivamo fascinantne razlike:
   - **New** pjesme (30) imaju daleko najveći prosjek streamova (3,393,800) jer su u fazi eksplozivnog rasta, ali su na listi samo prosječno 11 dana
   - **Stable Hit** pjesme (20) imaju umjerene streamove (1,889,014) i prosječno 67 dana na listi
   - **Evergreen** pjesme (128) imaju najniži prosjek (1,820,507) ali su na listi prosječno 733 dana - gotovo 2 godine

   Ovo otkriva životni ciklus trending pjesme: eksplozivan start sa visokim streamovima, zatim postepeni pad na stabilan nivo koji može trajati godinama.

4. **Popularity category analiza** - Samo 5 od 178 pjesama je klasifikovano kao Trending (sa prosječno 6.87M streamova), dok je 173 Average (1.96M prosječno). To znači da Spotify ima izuzetno stroge kriterijume za Trending status.

**Rezultat:** Većina trending pjesama je zapravo u padu (77%), što je prirodno jer pjesme obično eksplodiraju pa opadaju. Regional Mexicano je žanr sa najjačim momentum-om rasta. Životni ciklus trending pjesme slijedi predvidiv obrazac: eksplozivan start → postepeni pad → dugotrajna stabilnost.

---

### 6. Korelaciona analiza

**Šta radimo i zašto je to važno:**

Korelaciona analiza mjeri jačinu i smjer linearnog odnosa između dva numerička podatka. Pearsonov koeficijent korelacije (r) se kreće od -1 do +1:
- **r = +1** znači savršenu pozitivnu korelaciju (kad jedno raste, i drugo raste)
- **r = -1** znači savršenu negativnu korelaciju (kad jedno raste, drugo pada)
- **r = 0** znači da nema linearne veze

Ova analiza je ključna jer otkriva koje varijable su međusobno povezane, što pomaže u razumijevanju šta utiče na šta i koje varijable eventualno mjere istu stvar.

**Kako to radimo korak po korak:**

1. **Kreiranje korelacione matrice** - Sa `df[numeric_cols].corr()` računamo Pearsonov koeficijent korelacije između svakog para od 6 numeričkih kolona. Rezultat je matrica 6×6 gdje svaka ćelija sadrži korelacijski koeficijent. Dijagonala je uvijek 1.000 (svaka varijabla savršeno korelira sama sa sobom) i matrica je simetrična (korelacija A-B = korelacija B-A).

2. **Rangiranje korelacija** - Prolazimo kroz sve jedinstvene parove (izbjegavajući dijagonalu i duplikate, kojih ima 15 od ukupno 36 ćelija) i sortiramo po apsolutnoj vrijednosti korelacije. Klasifikujemo ih u tri kategorije:
   - **JAKA** korelacija: |r| > 0.7 - varijable su snažno povezane
   - **SREDNJA** korelacija: |r| > 0.4 - postoji primjetna veza
   - **SLABA** korelacija: |r| ≤ 0.4 - veza je slaba ili ne postoji

3. **Interpretacija ključnih nalaza:**

   - **7day ↔ viral_score: r = 0.990** - Ovo je gotovo savršena korelacija. To znači da su sedmodnevni streamovi i viral score praktično ista metrika - ako znamo jednu, možemo sa 99% tačnosti predvidjeti drugu. Ovo sugeriše da se viral_score u velikoj mjeri računa na osnovu sedmodnevnih streamova. Za praktičnu analizu, ove dvije kolone su redundantne.

   - **pos ↔ viral_score: r = -0.784** - Jaka negativna korelacija. Pjesme sa višim viral score-om imaju nižu (bolju) poziciju na listi. Negativan predznak je očekivan jer niža pozicija (1, 2, 3...) znači bolji plasman. Ovo potvrđuje da viral_score značajno utiče na rangiranje.

   - **streams ↔ pos: r = -0.751** - Još jedna očekivana jaka negativna korelacija: više streamova = bolja (niža) pozicija. Ali korelacija nije savršena (-1.0), što znači da Spotify ne rangira samo po streamovima - viral_score i drugi faktori takođe igraju ulogu.

   - **streams ↔ stream_change: r = -0.736** - Ovo je iznenađujući nalaz. Očekivali bismo da popularne pjesme rastu, ali korelacija je negativna: što više streamova, to veći PAD. Ovo je posljedica "BTS efekta" - pjesme koje su eksplodirale sa ogromnim brojem streamova u prva 2 dana sada prirodno opadaju. To je tipičan obrazac za viralnu muziku.

   - **days ↔ streams: r = -0.252** - Slaba negativna korelacija. Duže prisustvo na listi ne znači više streamova - zapravo, New pjesme imaju veće streamove od Evergreen, ali su na listi kratko. Ovo potvrđuje da dugovječnost i trenutna popularnost su različiti koncepti.

**Rezultat:** Otkrili smo da su 7day i viral_score praktično ista metrika, da pozicija na listi zavisi i od streamova i od viralnosti, i da postoji kontraintuitivan obrazac gdje najstrimovanije pjesme zapravo gube streamove (jer su prošle fazu eksplozivnog rasta).

---

### 7. Napredna analiza

Ova sekcija predstavlja najsloženiji dio analize i podijeljena je na četiri podsekcije, svaka sa specifičnim ciljem i metodologijom.

#### 7.1 Feature Engineering (Kreiranje novih varijabli)

**Šta radimo i zašto je to važno:**

Feature engineering je proces kreiranja novih varijabli (feature-a) iz postojećih podataka. Sirovi podaci često ne daju potpunu sliku jer ne uzimaju u obzir kontekst. Na primjer, pjesma sa 5 miliona streamova koja je na listi 2 dana je mnogo impresivnija od one sa 5 miliona streamova koja je na listi 3 godine. Feature engineering nam omogućava da kreiramo metrike koje fer porede pjesme u različitim kontekstima.

**Kako to radimo korak po korak i šta svaka nova varijabla znači:**

1. **`streams_per_day = streams / days`** - Normalizujemo broj streamova po broju dana na listi. Koristimo `np.where(df['days'] > 0, df['streams'] / df['days'], df['streams'])` umjesto prostog dijeljenja jer moramo zaštititi od dijeljenja nulom - ako bi neka pjesma imala 0 dana (što teoretski može biti greška u podacima), dijeljenje nulom bi proizvelo beskonačnost (infinity) i srušilo dalju analizu. `np.where` funkcioniše kao IF/ELSE: ako je days > 0, podijeli; inako, vrati samo streams.

   **Praktičan uvid:** BTS dominira ovom metrikom sa 5.6M streamova/dan jer su sve njihove pjesme tek 2 dana na listi. To je daleko ispred svih ostalih i pokazuje eksplozivnu snagu K-Pop fanova.

2. **`efficiency_score = viral_score / streams`** - Mjeri koliko viralnosti generiše svaki stream. Visok efficiency_score znači da se pjesma organski širi (dijeli, dodaje na playliste) daleko više nego što se samo pasivno sluša. Pjesma sa niskim streamovima ali visokim efficiency_score je "skriveni dragulj" koji se brzo širi.

   **Praktičan uvid:** Harry Styles dominira ovom metrikom (9.92, 9.76, 9.61 za tri pjesme) što znači da njegove pjesme generišu izuzetno veliku viralnost po streamu - njegovi fanovi aktivno dijele i promoviraju muziku.

3. **`growth_rate = (stream_change / streams) * 100`** - Procentualna stopa rasta. Apsolutni stream_change može biti obmanjujući: gubitak od 100,000 streamova je katastrofalan za pjesmu sa 200,000 ukupno, ali zanemariv za pjesmu sa 10 miliona. Growth rate normalizuje ovo u procenat koji je uporediv.

4. **`weekly_avg = 7day / 7`** - Prosječni dnevni streamovi u poslednjih 7 dana. Ovo je jednostavna ali korisna metrika za procjenu trenutnog dnevnog performansa. Razlika između `streams_per_day` (ukupni prosjek) i `weekly_avg` (nedeljni prosjek) pokazuje da li pjesma trenutno performira bolje ili lošije od svog istorijskog prosjeka.

#### 7.2 Outlier detekcija (IQR metoda)

**Šta radimo i zašto je to važno:**

Outlier-i (izuzetne/ekstremne vrijednosti) su tačke podataka koje se značajno razlikuju od ostatka. Njihova identifikacija je važna iz dva razloga: (1) mogu biti greške u podacima koje treba ispraviti, ili (2) mogu biti legitimne ali ekstremne vrijednosti koje iskrivljuju statističke mjere kao što su prosjek i standardna devijacija.

**Kako to radimo korak po korak:**

Za svaku od tri ključne kolone (streams, viral_score, stream_change) primjenjujemo IQR (Interquartile Range) metodu:

1. **Računamo Q1 (25. percentil)** - Vrijednost ispod koje se nalazi 25% svih podataka. Za streams je to 1,350,051.
2. **Računamo Q3 (75. percentil)** - Vrijednost ispod koje se nalazi 75% svih podataka. Za streams je to 2,202,585.
3. **Računamo IQR = Q3 - Q1** - Interkvartilni raspon obuhvata srednjih 50% podataka. Za streams: 2,202,585 - 1,350,051 = 852,534.
4. **Donja granica = Q1 - 1.5 × IQR** - Sve ispod ovoga je outlier. Za streams: 1,350,051 - 1.5 × 852,534 = 71,248.
5. **Gornja granica = Q3 + 1.5 × IQR** - Sve iznad ovoga je outlier. Za streams: 2,202,585 + 1.5 × 852,534 = 3,481,387.
6. Sve pjesme sa streamovima ispod 71,248 ili iznad 3,481,387 su klasifikovane kao outlier-i.

Faktor 1.5 je standardna vrijednost u statistici (predložio ju je John Tukey 1977.) i odgovara otprilike 2.7 standardnih devijacija za normalnu distribuciju. Koristi se jer je dovoljno konzervativna da ne označi previše vrijednosti kao outlier-e, ali dovoljno stroga da uhvati zaista ekstremne vrijednosti.

**Zašto IQR a ne standardna devijacija:** IQR metoda je robusna (otporna na outlier-e) jer koristi samo kvartile, koji nisu osjetljivi na ekstremne vrijednosti. Metoda bazirana na standardnoj devijaciji koristi prosjek, koji je sam po sebi iskrivljen outlier-ima - to je cirkularan problem (koristimo mjeru iskrivljenu outlier-ima da bismo detektovali outlier-e).

**Rezultat:** Pronašli smo 24 outlier-a u streamovima (uglavnom BTS pjesme sa 4-11M streamova), 18 u viral_score-u, i 20 u stream_change-u. Ovo potvrđuje da dataset ima mali broj ekstremno popularnih pjesama koje značajno utiču na prosjeke.

#### 7.3 Pareto analiza (Pravilo 80/20)

**Šta radimo i zašto je to važno:**

Pareto princip (nazvan po italijanskom ekonomisti Vilfredu Paretu) kaže da u mnogim sistemima oko 80% efekata dolazi od 20% uzroka. U kontekstu muzike, pitanje je: da li mali broj artista proizvodi većinu streamova? Ovo je fundamentalno pitanje o strukturi tržišta i nejednakosti.

**Kako to radimo korak po korak:**

1. **Agregacija po artistu** - Sa `df.groupby('artist_name')['streams'].sum()` sabiramo sve streamove za svakog artista (jer jedan artist može imati više pjesama). BTS sa 15 pjesama dobija zbir svih 15, dok artisti sa jednom pjesmom dobijaju samo taj jedan iznos.
2. **Sortiranje opadajuće** - Stavljamo artiste od najpopularnijeg do najmanje popularnog.
3. **Računanje ukupnih streamova** - Sabiramo sve streamove svih artista (372.6 miliona).
4. **Uzimanje top 20%** - Od 104 artista, top 20% je 20 artista. Sabiramo njihove streamove.
5. **Računanje procenta** - Top 20 artista generiše 59.1% svih streamova.

Klasičan Pareto princip kaže 80/20, ali u praksi rijetko bude tačno 80%. Naš rezultat od 59.1% za top 20% pokazuje da nejednakost postoji, ali nije ekstremna kao u nekim drugim industrijama. Ipak, sam BTS sa 19.5% svih streamova pokazuje veliku koncentraciju na vrhu.

**Rezultat:** Pareto efekat je potvrđen - mali broj artista dominira. BTS sam čini petinu svih streamova, a top 10 artista čini oko 45%. Ovo je tipično za muzičku industriju gdje su superzvijezde nesrazmjerno popularne.

#### 7.4 Pivot analize (Dvodimenzionalno ukrštanje podataka)

**Šta radimo i zašto je to važno:**

Sve dosadašnje analize su bile jednodimenzionalne - grupišemo po jednoj varijabli (žanr ILI trend ILI zemlja). Pivot analiza ukršta DVIJE varijable istovremeno, stvarajući dvodimenzionalnu tabelu koja otkriva interakcije koje jednodimenzionalna analiza ne može prikazati.

**Kako to radimo korak po korak:**

1. **Pivot tabela: Žanr × Trend → Prosječni streamovi** - Koristimo `df.pivot_table(values='streams', index='genre', columns='trend', aggfunc='mean')`. Ovo za svaku kombinaciju žanra i trenda (npr. "Pop + Rising", "Pop + Falling", "Rock + Rising"...) računa prosječne streamove. Rezultat otkriva interesantne razlike:
   - Pop Rising pjesme imaju veće prosječne streamove (1.98M) od Pop Falling (1.79M) - Pop raste kvalitetno
   - Reggaeton Falling (2.33M) ima mnogo više od Reggaeton Rising (1.61M) - velike Reggaeton pjesme već opadaju
   - K-Pop nema Rising pjesama uopšte (sve su Falling) - NaN vrijednost u tabeli

2. **Crosstab: Popularity Category × Longevity → Broj pjesama** - Koristimo `pd.crosstab()` koji za svaku kombinaciju (npr. "Average + Evergreen", "Trending + New") broji broj pjesama. Ovo otkriva:
   - Trending status je skoro ekskluzivno vezan za New pjesme (4 od 5 Trending su New)
   - Niti jedna Stable Hit nije Trending - čim pjesma postane stabilna, gubi Trending status
   - Ogromna većina (127 od 128) Evergreen pjesama je Average

**Rezultat:** Pivot analize otkrivaju da životni ciklus pjesme ima jasne obrasce: nove pjesme eksplodiraju (Trending + New), zatim prelaze u Average kategoriju, i neke od njih postaju Evergreen hitovi sa stabilnim ali umjerenim streamovima.

---

### 8. Vizualizacije

**Šta radimo i zašto je to važno:**

Vizualizacija podataka pretvara brojeve u slike koje ljudski mozak procesira mnogo brže i efikasnije. Dobro dizajniran graf može u sekundi prenijeti uvid za koji bi trebalo minut čitanja tabele. Generisano je 12 grafova, svaki sa specifičnim ciljem i pažljivo odabranim tipom prikaza.

**Detaljan opis svakog grafa:**

#### Graf 1: Top 15 pjesama po streamovima (Horizontalni bar chart)
- **Tip:** Horizontalni bar chart odabran jer su nazivi pjesama dugi pa se bolje čitaju na Y osi
- **Boje:** Zelena (#2ecc71) za Rising, crvena (#e74c3c) za Falling - intuitivne boje (zelena = rast, crvena = pad)
- **Dodatno:** Egzaktne brojke ispisane na kraju svake trake za preciznost
- **Šta otkriva:** BTS dominira prvih 10 pozicija ali su sve crvene (Falling). Babydoll od Dominic Fike je jedina zelena (Rising) u top 5.

#### Graf 2: Top 10 artista po ukupnim streamovima (Horizontalni bar chart)
- **Tip:** Horizontalni bar chart sa viridis paletom boja (nijanse od ljubičaste do žute)
- **Razlika od grafa 1:** Ovdje su agregirali streamovi PO ARTISTU, ne po pjesmi. BTS ima 72.7M jer se sabiraju svih 15 pjesama.
- **Šta otkriva:** Ogromna razlika između BTS (72.7M) i drugog artista Bad Bunny (19.1M) - gotovo 4× više.

#### Graf 3: Distribucija žanrova (Pie chart)
- **Tip:** Pie chart sa procentima za top 8 žanrova + "Ostali" kategorija. Grupisali smo manje žanrove u "Ostali" jer bi 39 isječaka bilo nečitljivo.
- **Paleta:** Set2 (pastelne boje) za jasno razlikovanje isječaka
- **Šta otkriva:** Pop čini skoro trećinu dataseta. Distribucija je neravnomjerna - mali broj žanrova dominira.

#### Graf 4: Korelaciona matrica (Heatmap)
- **Tip:** Heatmap sa RdBu_r (Red-Blue reverse) divergentnom paletom. Crvena = pozitivna korelacija, plava = negativna, bijela = nema korelacije.
- **Dodatno:** Numeričke vrijednosti ispisane u svakoj ćeliji. Prikazana samo donja trokutasta polovina matrice (gornja je identična jer je matrica simetrična).
- **Šta otkriva:** Intenzivno crveno polje za 7day↔viral_score (0.99) instant ukazuje na gotovo savršenu korelaciju. Intenzivno plava polja za pos↔viral_score (-0.78) pokazuju jaku negativnu vezu.

#### Graf 5: Streams vs Viral Score (Scatter plot)
- **Tip:** Scatter plot gdje je svaka tačka jedna pjesma. X osa = streams, Y osa = viral_score.
- **Boje:** Zelene tačke su Rising, crvene su Falling
- **Dodatno:** Isprekidana siva linija linearne regresije sa ispisanim koeficijentom korelacije
- **Šta otkriva:** Jasna pozitivna veza - više streamova znači viši viral score. BTS pjesme se jasno vide kao klaster u gornjem desnom uglu (visoki streamovi I visoka viralnost).

#### Graf 6: Box plot - Streamovi po popularity kategoriji
- **Tip:** Box plot koji prikazuje kompletnu distribuciju podataka za svaku kategoriju
- **Elementi box plota:** Linija u sredini kutije = medijan, kutija = IQR (25.-75. percentil), brkovi = raspon podataka, tačke izvan brkova = outlier-i
- **Šta otkriva:** Trending kategorija ima dramatično viši medijan i veći raspon od Average. Outlier-i u Average kategoriji su pjesme koje imaju visoke streamove ali nisu klasifikovane kao Trending (npr. jer su u padu).

#### Graf 7: Box plot - Viral score po longevity kategoriji
- **Tip:** Isti princip box plota, ali za viral_score grupisano po longevity
- **Šta otkriva:** New pjesme imaju najširi raspon i najviši medijan viral score-a - očekivano jer viralni sadržaj je obično nov. Evergreen pjesme imaju uži raspon i niži medijan - stabilne ali ne eksplozivne.

#### Graf 8: Rising vs Falling po žanrovima (Stacked bar chart)
- **Tip:** Stacked (naslagani) bar chart gdje je svaki stupac podijeljen na crveni (Falling) i zeleni (Rising) dio
- **Šta otkriva:** K-Pop je potpuno crven (sve Falling). Regional Mexicano je skoro potpuno zelen. Pop ima pomješano ali sa više crvenog.

#### Graf 9: Top 10 zemalja po broju pjesama (Bar chart)
- **Tip:** Vertikalni bar chart sa rocket paletom (tamne nijanse)
- **Šta otkriva:** US dominira sa 79 pjesama, više nego dvostruko od drugoplasiranog GB (25).

#### Graf 10: Histogram distribucije streamova
- **Tip:** Histogram sa 30 binova (intervala). Svaki bin pokazuje koliko pjesama ima streamove u tom rasponu.
- **Dodatno:** Crvena isprekidana linija za prosjek, narandžasta za medijan
- **Šta otkriva:** Distribucija je jasno pozitivno iskrivljena (skewed right) - velika koncentracija pjesama u nižem rasponu (1-2M) i dugačak rep udesno do 11M. Razlika između prosjeka i medijana vizuelno potvrđuje iskrivljenost.

#### Graf 11: Dani na listi vs Streams (Scatter plot)
- **Tip:** Scatter plot sa bojama po longevity kategoriji
- **Šta otkriva:** Jasno se vide tri klastera: New pjesme (crvene) su grupisane u donjem lijevom uglu (malo dana, razni streamovi), Evergreen (zelene) su razbacane po cijelom rasponu dana, a Stable Hit (narandžaste) su između.

#### Graf 12: Prosječni streamovi po žanru i trendu (Grouped bar chart)
- **Tip:** Grouped (grupisani) bar chart sa po dva stupca za svaki žanr (Rising i Falling)
- **Šta otkriva:** Direktno poređenje prosječnih streamova za Rising vs Falling unutar svakog žanra. Vidimo da Pop Rising imaju više prosječne streamove od Pop Falling, ali kod Reggaetona je obrnuto.

---

### 9. Ključni uvidi (Insights)

**Šta radimo i zašto je to važno:**

Završna sekcija automatski generiše 10 najvažnijih zaključaka iz kompletne analize. Ovo je "executive summary" - sažetak za nekoga ko nema vremena da čita cijelu analizu ali želi razumjeti ključne nalaze.

**Detaljno objašnjenje svakog uvida:**

1. **BTS dominacija (19.5% svih streamova)** - Jedan artist generiše petinu svih streamova u datasetu. Ovo je neuobičajena koncentracija koja pokazuje globalnu moć K-Pop fandoma. Ipak, sve BTS pjesme su Falling jer su tek 2 dana na listi - eksplozivan start koji prirodno opada.

2. **77% pjesama je u padu** - Na prvi pogled alarmantno, ali zapravo prirodno. Trending lista je snapshot - većina pjesama je prošla svoj vrhunac i polako opada. Samo 23% aktivno raste.

3. **Pop dominira volumenom, Regional Mexicano momentum-om** - Pop ima najviše ukupnih streamova, ali Regional Mexicano ima 88% Rising pjesama - to je žanr budućnosti na ovoj listi.

4. **US proizvodi 44.4% trending pjesama** - Gotovo polovina svih trending pjesama dolazi iz Amerike, potvrđujući dominaciju američke muzičke industrije.

5. **Pozitivno iskrivljena distribucija** - Prosjek (2.09M) je 31% veći od medijana (1.59M). To znači da mali broj izuzetno popularnih pjesama "vuče" prosjek naviše. Medijan je pouzdanija mjera "tipičnog" broja streamova.

6. **Pareto efekat** - Top 20% artista generiše 59.1% streamova. Nejednakost postoji ali je umjerenija od klasičnog 80/20.

7. **New vs Evergreen** - New pjesme imaju 86% veće prosječne streamove (3.39M vs 1.82M), ali Evergreen pjesme traju 66× duže (733 vs 11 dana). Kratak intenzivan eksplozivan uspjeh vs dugotrajni umjereni.

8. **7day ≈ viral_score** - Korelacija od 0.990 znači da su ove dvije metrike praktično iste. Ovo je važan nalaz za svakoga ko bi htio koristiti ove podatke za modeliranje - jedna od ovih kolona je redundantna.

9. **Kontraintuitvna korelacija streams↔stream_change** - Negativna korelacija (-0.736) znači da najpopularnije pjesme najviše gube streamove. Ovo je posljedica matematike viralnosti: što je viši vrhunac, to je strmiji pad.

10. **Ukupna statistika** - 178 pjesama, 104 artista, 39 žanrova, 19 zemalja daje kontekst za razumijevanje obima analize.

---

## Pokretanje programa

### Preduvjeti

Potreban je Python 3.8 ili noviji sa sljedećim bibliotekama:

```bash
pip install pandas numpy matplotlib seaborn
```

### Izvršavanje

```bash
python main.py
```

### Šta program proizvodi

1. **Konzolni output** - Kompletna tekstualna analiza sa formatiranim tabelama, statistikama i uvidima, podijeljeno u 9 jasno označenih sekcija
2. **12 PNG grafova** - Generisani u istom direktorijumu sa prefiksom `graf_XX_` za lako sortiranje

---

## Korišćene tehnologije

| Biblioteka | Verzija | Namjena u projektu |
|------------|---------|-------------------|
| `pandas` | 3.0+ | Učitavanje CSV-a, čišćenje podataka, groupby agregacija, pivot tabele, crosstab, statističke funkcije |
| `numpy` | 2.4+ | Numeričke operacije, zaštita od dijeljenja nulom (`np.where`), polinomijalna regresija (`np.polyfit`), generisanje nizova (`np.linspace`), kreiranje maski za heatmap (`np.triu`) |
| `matplotlib` | 3.10+ | Osnova za sve grafove - bar chartovi, scatter plotovi, histogrami, pie chartovi. Kontrola boja, fontoava, veličina, labela, legendi |
| `seaborn` | 0.13+ | Napredne statističke vizualizacije izgrađene nad matplotlib-om: heatmap sa anotacijama, box plotovi sa automatskim outlier prikazom, stilizacija svih grafova sa `set_theme()` |
