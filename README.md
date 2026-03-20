**[Polski](README.md)** | **[English](README.en.md)**

# olx-agentic-cli

> **Stworzone dla agentow AI.** Podaj to repozytorium Claude Code, OpenClaw lub dowolnemu agentowi LLM — sam zajmie sie konfiguacja OLX, wdrozeniem i codziennymi operacjami. Czlowiek musi tylko raz kliknac "Autoryzuj".

Narzedzie CLI w Pythonie oraz skill dla agentow AI do [OLX Partner API v2.0](https://developer.olx.pl/api/doc). 30 komend obslugujacych kazdy endpoint API. Zaprojektowane do wdrozenia przez agenta — agent wdraza callback OAuth, konfiguruje dane logowania i autonomicznie zarzadza Twoim kontem OLX.pl po jednorazowej autoryzacji w przegladarce.

## Po co to jest

Reczne zarzadzanie ogloszeniami na OLX jest wolne. To narzedzie pozwala agentowi AI to robic — wystawianie ogloszen, odpowiadanie na wiadomosci, promowanie, sprawdzanie platnosci — wszystko z terminala ze strukturalnym wyjsciem JSON, ktory agenci parsuja natywnie.

**Co agent moze robic autonomicznie (po jednorazowej konfiguracji):**
- Wyswietlac, tworzyc, edytowac, usuwac, aktywowac, dezaktywowac ogloszenia
- Czytac i odpowiadac na watki wiadomosci
- Wyszukiwac kategorie, atrybuty, lokalizacje
- Stosowac platne promocje
- Sprawdzac saldo konta i historie platnosci
- Zarzadzac dostawa i przesylkami

**Co wymaga czlowieka (jednorazowo):**
- Zalozyc darmowe konto Cloudflare (2 min)
- Zarejestrowac sie na developer.olx.pl (5 min + oczekiwanie na zatwierdzenie)
- Kliknac "Autoryzuj" w przegladarce raz

## Funkcje

- **Projektowanie pod agentow** — strukturalny JSON, interfejs CLI, SKILL.md do integracji
- **Automatyczne wdrozenie** — `deploy.sh` wdraza callback OAuth przez API Cloudflare (tylko curl, bez npm)
- **OAuth 2.0** z automatycznym odswiezaniem tokenow — autoryzuj raz, nigdy wiecej o tym nie mysl
- **Pelne pokrycie API** — 30 komend w 7 grupach endpointow
- **Wieloplatformowe** — dziala z Claude Code, OpenClaw lub dowolnym LLM
- Ogloszenia: lista, szczegoly, tworzenie, edycja, usuwanie, aktywacja, dezaktywacja
- Wiadomosci: watki, odczyt, odpowiedz, oznacz przeczytane, ulubione
- Kategorie + atrybuty, lokalizacje (regiony/miasta/dzielnice)
- Platnosci: platne funkcje, pakiety promocyjne, historia
- Dostawa: metody, informacje o przesylce, tworzenie przesylek

## Instrukcja konfiguracji

Konfiguracja wymaga **5 krokow**. Kroki oznaczone **[UZYTKOWNIK]** wymagaja dzialania w przegladarce. Kroki oznaczone **[AGENT]** moga byc wykonane automatycznie przez agenta AI.

> **Dlaczego te kroki?** OLX wymaga prawdziwego adresu HTTPS jako callback URI (localhost nie jest akceptowany). Darmowy Cloudflare Worker zapewnia taki adres — agent moze go wdrozyc automatycznie, jesli podasz token API.

### Przeglad

```
Krok 1  [UZYTKOWNIK]  Zaloz darmowe konto Cloudflare + token API
Krok 2  [AGENT]       Wdroz strone callback (jedna komenda)
Krok 3  [UZYTKOWNIK]  Zarejestruj sie jako Partner OLX na developer.olx.pl
Krok 4  [AGENT]       Sklonuj repo, zainstaluj, skonfiguruj CLI
Krok 5  [UZYTKOWNIK]  Uruchom `olx login` i autoryzuj w przegladarce
```

Po kroku 5 agent moze uzywac wszystkich 30 komend autonomicznie.

---

### Krok 1: Zaloz konto Cloudflare + token API

**Kto:** Uzytkownik (jednorazowo, 3 minuty)
**Pomin jesli:** Masz juz konto Cloudflare z tokenem API dla Workers

1. Wejdz na [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up) — zaloz darmowe konto (bez karty kredytowej)
2. Przejdz do **My Profile > API Tokens** ([bezposredni link](https://dash.cloudflare.com/profile/api-tokens))
3. Kliknij **Create Token**
4. Uzyj szablonu **"Edit Cloudflare Workers"**
5. Kliknij **Continue to summary > Create Token**
6. **Skopiuj token** oraz **Account ID** (widoczny na prawym pasku bocznym dowolnej strony domeny lub na gorze dashboardu Workers)

Podaj agentowi te dwie wartosci:
- **API Token** (zaczyna sie od `cfat_...` lub podobnie)
- **Account ID** (32-znakowy ciag hex)

> **Bez Cloudflare?** Zobacz [Alternatywne opcje hostingu](#alternatywne-opcje-hostingu) na dole strony.

---

### Krok 2: Wdroz strone callback

**Kto:** Agent (lub uzytkownik w terminalu)
**Czas:** 10 sekund
**Wymaga:** Token API i Account ID z kroku 1

```bash
cd callback
./deploy.sh <API_TOKEN> <ACCOUNT_ID>
```

To wszystko. Skrypt:
1. Weryfikuje token
2. Wdraza Worker callback przez API Cloudflare (bez wrangler/npm)
3. Wyswietla URL callbacka (np. `https://olx-oauth-callback.twojanazwa.workers.dev`)

Zapisz ten URL — bedzie potrzebny w krokach 3 i 4.

**Weryfikacja:** Otworz URL w przegladarce — powinienes zobaczyc ciemna strone z napisem "OLX OAuth Callback".

---

### Krok 3: Zarejestruj sie jako Partner OLX + stworz aplikacje

**Kto:** Uzytkownik (jednorazowo, 5 minut + oczekiwanie na zatwierdzenie)

1. Wejdz na [developer.olx.pl](https://developer.olx.pl) i wypelnij formularz rejestracji:

| Pole | Co wpisac |
|------|-----------|
| Nazwa firmy | Nazwa Twojej firmy |
| Cel tworzenia integracji | np. "Zarzadzanie ogloszeniami przez CLI" |
| Glowna kategoria dzialalnosci | Twoja glowna kategoria biznesowa |
| Adres strony WWW firmy | URL Twojej strony |
| NIP | Twoj numer NIP |
| Wlasciciel aplikacji | Twoje imie i nazwisko |
| Email do kontaktow biznesowych | Twoj email biznesowy |
| Email do kontaktow technicznych | Twoj email techniczny |
| Numer telefonu | Twoj telefon z kodem kraju (+48...) |

2. Zaakceptuj Regulamin i Polityke Prywatnosci, wyslij, czekaj na zatwierdzenie

3. Po zatwierdzeniu przejdz do **"Dodaj aplikacje"**:

| Pole | Co wpisac |
|------|-----------|
| Nazwa aplikacji | Dowolna nazwa (np. "OLX CLI") |
| Adres strony WWW firmy | URL Twojej strony |
| **URI wywolania zwrotnego** | **URL callbacka z kroku 2** |
| Application description | np. "Narzedzie CLI do zarzadzania ogloszeniami OLX" |

4. Zapisz swoj **Client ID** i **Client Secret**

---

### Krok 4: Instalacja i konfiguracja

**Kto:** Agent (lub uzytkownik w terminalu)
**Czas:** 1 minuta

```bash
git clone https://github.com/sonusflow/olx-agentic-cli.git
cd olx-agentic-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python cli.py setup
# Client ID:    <z kroku 3>
# Client Secret: <z kroku 3>
# Redirect URI:  <URL callbacka z kroku 2>
```

---

### Krok 5: Uwierzytelnienie

**Kto:** Uzytkownik (wymaga przegladarki, jednorazowo)
**Czas:** 1 minuta

```bash
python cli.py login
```

1. Przegladarka otwiera strone autoryzacji OLX
2. Autoryzuj aplikacje
3. Przekierowanie na strone callback — kliknij **"Copy URL to Clipboard"**
4. Wklej URL do terminala, nacisnij Enter

```
Login successful! Tokens saved.
```

**Weryfikacja:**
```bash
python cli.py status
# Authenticated: yes
# Token expires: <~24 godziny od teraz>
```

---

### Gotowe!

Tokeny odswiezaja sie automatycznie po wygasnieciu. Agent moze teraz uzywac wszystkich 30 komend bez interakcji z przegladarka.

---

### Wymagania systemowe

- Python 3.10+
- curl (do skryptu wdrozenia callbacka — bez Node.js ani npm)


## Wszystkie komendy

### Autoryzacja
```
olx setup                                Konfiguracja danych logowania + redirect URI
olx login                                Autoryzacja OAuth przez przegladarke
olx logout                               Usun zapisane tokeny
olx status                               Status autoryzacji i wygasniecie tokena
```

### Ogloszenia
```
olx adverts list [--offset N --limit N]  Lista Twoich ogloszen
olx adverts get <id>                     Szczegoly ogloszenia
olx adverts create --file ad.json        Utworz ogloszenie z pliku JSON
olx adverts update <id> --file ad.json   Aktualizuj ogloszenie z pliku JSON
olx adverts delete <id>                  Usun ogloszenie (z potwierdzeniem)
olx adverts activate <id>               Aktywuj szkic/dezaktywowane ogloszenie
olx adverts deactivate <id>             Dezaktywuj aktywne ogloszenie
```

### Wiadomosci
```
olx messages list [--offset N --limit N] Lista watkow wiadomosci
olx messages get <thread_id>             Odczytaj wiadomosci w watku
olx messages thread <thread_id>          Metadane watku
olx messages send <thread_id> "tekst"    Odpowiedz w watku
olx messages mark-read <thread_id>       Oznacz watek jako przeczytany
olx messages favourite <thread_id>       Dodaj do ulubionych
olx messages favourite <id> --remove     Usun z ulubionych
```

### Kategorie
```
olx categories list [--parent N]         Lista kategorii
olx categories get <id>                  Szczegoly kategorii
olx categories attributes <id>          Wymagane pola dla kategorii
```

### Uzytkownik
```
olx user me                              Twoj profil
olx user get <id>                        Publiczny profil uzytkownika
olx user balance                         Saldo konta
```

### Lokalizacje
```
olx locations regions                    Wszystkie 16 wojewodztw
olx locations cities [--region N]        Lista miast
olx locations get-city <id>              Szczegoly miasta
olx locations districts <city_id>        Dzielnice miasta
```

### Platnosci i promocje
```
olx payments features <advert_id>        Platne funkcje dla ogloszenia
olx payments apply-feature <id> <typ>    Zastosuj promowanie/pilne/top
olx payments packets                     Dostepne pakiety promocyjne
olx payments history [--offset --limit]  Historia platnosci
```

### Dostawa
```
olx delivery methods                     Dostepne metody dostawy
olx delivery get-shipment <advert_id>    Informacje o przesylce
olx delivery create-shipment <id> --file Utworz przesylke z pliku JSON
```

## Przyklady

### Utworz nowe ogloszenie

```bash
# 1. Znajdz odpowiednia kategorie
python cli.py categories list --parent 0
python cli.py categories list --parent 99
python cli.py categories attributes 165

# 2. Znajdz lokalizacje
python cli.py locations regions
python cli.py locations cities --region 2
python cli.py locations districts 17871
```

Utworz plik `ad.json`:

```json
{
  "title": "iPhone 14 Pro 256GB",
  "description": "Jak nowy, z pudelkiem i ladowarka. Bateria 96%.",
  "category_id": 165,
  "contact": { "name": "Jan", "phone": "+48500000000" },
  "location": { "city_id": 10609, "district_id": null },
  "images": [
    {"url": "https://example.com/photo1.jpg"},
    {"url": "https://example.com/photo2.jpg"}
  ],
  "price": { "value": 4200, "currency": "PLN", "negotiable": true },
  "attributes": {}
}
```

```bash
python cli.py adverts create --file ad.json
```

### Zaktualizuj cene ogloszenia

```bash
# update.json: { "price": { "value": 3900, "currency": "PLN", "negotiable": true } }
python cli.py adverts update 12345 --file update.json
```

### Zarzadzaj wiadomosciami

```bash
python cli.py messages list --limit 5
python cli.py messages get 12345
python cli.py messages send 12345 "Wciaz dostepne! Moge sie spotkac jutro."
python cli.py messages mark-read 12345
```

### Promuj ogloszenie

```bash
python cli.py payments features 12345
python cli.py payments apply-feature 12345 promote
```

## Jak dziala przepyw OAuth

```
CLI uruchamia "olx login"
       |
       v
Przegladarka otwiera strone autoryzacji OLX
       |
       v (uzytkownik autoryzuje)
OLX przekierowuje na URL Twojego Cloudflare Workera
  ?code=XXXXX&state=YYYYY
       |
       v
Strona callback wyswietla "Copy URL to Clipboard"
       |
       v (uzytkownik wkleja do terminala)
CLI waliduje parametr state (ochrona CSRF)
       |
       v
CLI wymienia kod na tokeny przez OLX API
       |
       v
Tokeny zapisane w ~/.olx-integration/tokens.json
(chmod 600, automatyczne odswiezanie)
```

- Strona callback jest **czysto statyczna** — zadne dane nie sa przechowywane, logowane ani przesylane
- Kody autoryzacyjne sa **jednorazowe** i wygasaja w sekundy
- Tokeny dostepu wygasaja po ~24h i automatycznie sie odswiezaja

## Monitorowanie wiadomosci

API OLX nie obsluguje webhookow ani powiadomien push. Aby monitorowac przychodzace wiadomosci, skonfiguruj cron job, ktory odpytuje o nieprzeczytane wiadomosci:

```bash
# Sprawdzaj co 5 minut czy sa nowe wiadomosci
*/5 * * * * cd /sciezka/do/olx-agentic-cli && .venv/bin/python cli.py messages list 2>/dev/null | grep -q '"unread_count": [1-9]' && notify-send "OLX" "Nowa wiadomosc" || true
```

Dostosuj komende powiadomienia do swojego srodowiska (powiadomienie na pulpicie, Slack webhook, email, itp).

## Alternatywne opcje hostingu

Jesli nie mozesz uzyc Cloudflare, mozesz hostowac strone callback wszedzie, gdzie serwowane sa statyczne pliki HTML przez HTTPS:

### GitHub Pages (darmowe)
1. Zforkuj to repozytorium
2. Przejdz do **Settings > Pages** w swoim forku
3. Ustaw zrodlo: branch `main`, folder `/callback/github-pages`
4. Twoj URL: `https://<nazwa-uzytkownika>.github.io/olx-agentic-cli/callback/github-pages/`

### Dowolny hosting statyczny
Wgraj `callback/index.html` na Vercel, Netlify, Render, S3+CloudFront lub dowolny host obslugujacy HTTPS. Uzyj otrzymanego URL jako callback URI.

## Struktura projektu

```
cli.py            Punkt wejscia CLI (Click) — 30 komend
config.py         Zarzadzanie konfiguracja (~/.olx-integration/)
olx_api/          Moduly klienta API
  auth.py           OAuth 2.0 (authorization code + odswiezanie tokenow)
  client.py         Bazowy klient HTTP (httpx) z typowanymi bledami
  adverts.py        CRUD ogloszen + aktywacja/dezaktywacja
  messages.py       Watki, wiadomosci, oznacz przeczytane, ulubione
  categories.py     Drzewo kategorii + atrybuty
  users.py          Profil uzytkownika + saldo
  locations.py      Regiony, miasta, dzielnice
  payments.py       Platne funkcje, pakiety, historia platnosci
  delivery.py       Metody dostawy + przesylki
callback/         Strona callback OAuth (Cloudflare Worker / GitHub Pages / dowolny host)
tests/            Testy (pytest)
references/       Szybki przeglad API
SKILL.md          Definicja skilla dla agentow AI
```

## Testy

```bash
pip install pytest
pytest tests/ -v
```

## Bezpieczenstwo

- Dane logowania: `~/.olx-integration/config.json` (chmod 600)
- Tokeny: `~/.olx-integration/tokens.json` (chmod 600)
- Katalog konfiguracji: chmod 700
- Walidacja parametru state OAuth (ochrona CSRF)
- Brak sekretow w kodzie zrodlowym
- Strona callback: statyczny HTML, bez przetwarzania po stronie serwera, bez logowania

## Licencja

MIT — zobacz [LICENSE](LICENSE).

## Autor

**sonusflow** — [github.com/sonusflow](https://github.com/sonusflow)
