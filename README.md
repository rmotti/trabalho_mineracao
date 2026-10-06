# Exploração da API AISWEB (DECEA)

Notebooks para explorar as rotas da API do [AISWEB](https://aisweb.decea.mil.br/), o portal de informação aeronáutica do DECEA, e procurar uma situação-problema de ML cruzando esses dados com METAR histórico (IEM) e os voos da ANAC (VRA).

## Setup

```bash
make requirements      # = uv sync: cria a .venv e instala o pacote module_decea
cp .env.example .env   # e preencha AISWEB_API_KEY e AISWEB_API_PASS
```

Depois abra os notebooks em `notebooks/` e selecione o kernel `.venv`:

1. `01_explorar_aisweb.ipynb`: mapa das rotas da API AISWEB.
2. `02_insights_ml.ipynb`: exploração dos dados em busca de uma situação-problema de ML. Cruza a AISWEB com METAR histórico (IEM) e os voos da ANAC (VRA) de 2025. Na primeira execução baixa ~330 MB para `data/raw/` (pasta ignorada pelo git).

Outros comandos: `make test`, `make lint`, `make format`, `make clean` (`make` sozinho lista todos).

## Organização

```
├── data
│   ├── external       <- PDFs de cartas baixados no notebook 01
│   ├── interim        <- dados intermediários, já transformados
│   ├── processed      <- bases finais para modelagem
│   └── raw            <- downloads originais: aisweb/, metar/, vra/
├── docs
├── models             <- modelos treinados
├── module_decea       <- código Python do projeto
│   ├── config.py      <- caminhos do projeto e leitura do .env
│   ├── aisweb.py      <- cliente da API AISWEB
│   ├── dataset.py     <- downloads com cache (AISWEB, METAR/IEM, VRA/ANAC)
│   ├── metar.py       <- decodificação de METAR
│   └── vra.py         <- leitura do VRA
├── notebooks          <- numerados na ordem de leitura
├── references         <- dicionários de dados, manuais, ICAs
├── reports
│   └── figures        <- gráficos gerados para o relatório
├── tests
├── .env.example
├── Makefile
└── pyproject.toml
```

## Rotas disponíveis

`localidades`, `rotaer`, `met`, `sol`, `notam`, `cartas`, `suplementos`, `infotemp`, `pub` e `waypoints`. O notebook 01 detalha os parâmetros de cada uma.

> Os links de download das cartas contêm a `apiKey`. Limpe os outputs do notebook antes de commitar.
