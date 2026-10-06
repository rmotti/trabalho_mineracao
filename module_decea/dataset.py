"""Download com cache local (pasta data/raw/) das três fontes usadas no notebook 02."""
import time

import requests

from module_decea.aisweb import aisweb, itens, listar_paginado, para_df
from module_decea.config import RAW_DATA_DIR

# Rotas da AISWEB usadas na exploração. A coluna "link" das cartas contém a apiKey e nunca é salva.
ROTAS_AISWEB = {
    "localidades": lambda: para_df(itens(aisweb("localidades"))),
    "notam": lambda: para_df(itens(aisweb("notam"))),
    "cartas": lambda: para_df(itens(aisweb("cartas"))).drop(columns=["link"], errors="ignore"),
    "rotaer_lista": lambda: para_df(listar_paginado("rotaer")),
}


def baixar_aisweb(forcar=False):
    """Retrato do momento: NOTAMs vigentes, cartas e aeródromos. Rodar de novo outro dia dá outro retrato."""
    pasta = RAW_DATA_DIR / "aisweb"
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, fn in ROTAS_AISWEB.items():
        destino = pasta / f"{nome}.csv"
        if forcar or not destino.exists():
            fn().to_csv(destino, index=False)
            print("baixado:", destino)


def baixar_metar_iem(estacoes, ano):
    """METAR histórico do Iowa Environmental Mesonet (espelho público dos boletins do GTS)."""
    pasta = RAW_DATA_DIR / "metar"
    pasta.mkdir(parents=True, exist_ok=True)
    for icao in estacoes:
        destino = pasta / f"{icao}.csv"
        if destino.exists():
            continue
        url = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
               f"?station={icao}&data=metar&year1={ano}&month1=1&day1=1&year2={ano + 1}&month2=1&day2=1"
               "&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3&report_type=4")
        resp = requests.get(url, timeout=300)
        resp.raise_for_status()
        destino.write_bytes(resp.content)
        print("baixado:", destino)
        time.sleep(2)  # o IEM pede uso moderado


def baixar_vra(ano, meses=range(1, 13)):
    """VRA da ANAC: um CSV por mês (~25 MB cada)."""
    pasta = RAW_DATA_DIR / "vra"
    pasta.mkdir(parents=True, exist_ok=True)
    for mes in meses:
        destino = pasta / f"VRA_{ano}_{mes:02d}.csv"
        if destino.exists():
            continue
        url = f"https://siros.anac.gov.br/siros/registros/diversos/vra/{ano}/{destino.name}"
        resp = requests.get(url, timeout=600)
        resp.raise_for_status()
        destino.write_bytes(resp.content)
        print("baixado:", destino)
