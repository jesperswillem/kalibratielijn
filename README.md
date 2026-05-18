# Kalibratielijn onderwijsnotebooks

Deze repository bevat lesmateriaal waarmee studenten stap voor stap leren hoe je een kalibratielijn maakt, controleert en interpreteert.

De hoofdnotebook is bedoeld om rustig door te werken. Statistische begrippen zoals residuen, standaardfout, betrouwbaarheidsinterval, LOD, LOQ, goodness-of-fit en lack-of-fit worden onderweg uitgelegd.

## Snel starten

### Aanbevolen voor studenten: Google Colab

Zet deze map eerst in een GitHub-repository. Vervang daarna in onderstaande link `<organisatie>` en `<repository>` door je eigen GitHub-organisatie en repositorynaam:

[![Open hoofdnotebook in Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jesperswillem/kalibratielijn/blob/main/notebooks/01_kalibratielijn_studenten.ipynb)

Voor studenten kun je in Brightspace, Canvas, Teams of Moodle gewoon die link plaatsen.

Aanbevolen instructie voor studenten:

1. Open de Colab-link.
2. Kies eventueel `File > Save a copy in Drive`.
3. Kies `Runtime > Run all`.
4. Werk de notebook van boven naar beneden door.

De studentennotebook is zelfstandig te draaien. Studenten hoeven dus geen Python-bestanden uit `src/` te importeren.

### Eerst oefenen met notebooks

Voor studenten die nog nooit met notebooks hebben gewerkt, start met:

```text
notebooks/00_start_hier_werken_met_notebooks.ipynb
```

Daarin staat kort uitgelegd:

- wat tekstcellen en codecellen zijn;
- hoe je een cel uitvoert;
- wat `[*]` betekent;
- wat je doet bij een foutmelding;
- hoe je de hele notebook opnieuw draait.

## Structuur van de repository

```text
kalibratielijn_onderwijs_repo/
├── README.md
├── requirements.txt
├── data/
│   ├── voorbeelddata.csv
│   └── oefendata.csv
├── notebooks/
│   ├── 00_start_hier_werken_met_notebooks.ipynb
│   └── 01_kalibratielijn_studenten.ipynb
├── src/
│   ├── __init__.py
│   └── calibratie_helpers.py
└── tests/
    └── test_calibratie_helpers.py
```

## Wat staat waar?

### `notebooks/01_kalibratielijn_studenten.ipynb`

De hoofdnotebook voor studenten. Deze bevat:

- uitleg over de kalibratielijn;
- voorbeelddata;
- berekening van intercept en helling;
- residuen en residuenplot;
- standaardfout en betrouwbaarheidsintervallen;
- onder- en bovengrens in de grafiek;
- LOD en LOQ;
- goodness-of-fit;
- lack-of-fit;
- oefendata om zelf mee te experimenteren.

### `src/calibratie_helpers.py`

Losse helperfuncties voor docenten, gevorderde studenten of lokaal gebruik. De studentennotebook bevat de functies ook zelf, zodat Colab zo eenvoudig mogelijk blijft.

### `data/`

CSV-bestanden met dezelfde voorbeelddata als in de notebook. Die zijn handig als je later een versie wilt maken waarbij studenten zelf data uploaden of inlezen.

### `tests/`

Een paar eenvoudige tests om te controleren of de helperfuncties logisch werken.

## Lokaal draaien

Gebruik deze route als je de notebooks niet in Colab wilt draaien.

### 1. Repository clonen

```bash
git clone https://github.com/<organisatie>/<repository>.git
cd <repository>
```

### 2. Virtuele omgeving maken

Op Linux, macOS of WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Op Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Packages installeren

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Jupyter starten

```bash
jupyter lab
```

Open daarna:

```text
notebooks/01_kalibratielijn_studenten.ipynb
```

## Binder gebruiken

Je kunt ook Binder gebruiken als alternatief voor Colab. Vervang `<organisatie>` en `<repository>`:

```text
https://mybinder.org/v2/gh/<organisatie>/<repository>/main?labpath=notebooks/01_kalibratielijn_studenten.ipynb
```

Binder voelt meer als JupyterLab. Colab is meestal eenvoudiger voor studenten die nog weinig ervaring hebben.

## Tests draaien

Voor lokaal gebruik kun je de helperfuncties testen met:

```bash
pytest
```

Als alles goed werkt, eindigt de output met iets als:

```text
2 passed
```

## Advies voor gebruik in onderwijs

Gebruik bij voorkeur deze volgorde:

1. Laat studenten eerst `00_start_hier_werken_met_notebooks.ipynb` bekijken.
2. Laat ze daarna `01_kalibratielijn_studenten.ipynb` openen in Colab.
3. Laat ze de notebook eerst volledig draaien zonder iets te veranderen.
4. Laat ze daarna pas de oefendata aanpassen.
5. Bespreek vooral de interpretatie van residuen, onzekerheid, LOD/LOQ en lack-of-fit.

## Docentnotitie

De notebook vermijdt bewust verwijzingen naar de oorspronkelijke spreadsheet. Het materiaal is opgezet als zelfstandig onderwijsdocument dat de statistische en analytisch-chemische begrippen uitlegt zonder afhankelijkheid van Excel.
