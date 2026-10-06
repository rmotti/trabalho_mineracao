"""Cliente mínimo da API AISWEB (mesmas funções do notebooks/01_explorar_aisweb.ipynb)."""
import os
import time
import xml.etree.ElementTree as ET

import pandas as pd
import requests

import module_decea.config  # noqa: F401  (carrega o .env da raiz)

BASE_URL = "https://aisweb.decea.mil.br/api/"
SESSION = requests.Session()


class AiswebErro(Exception):
    pass


def aisweb(area, **params):
    query = {"apiKey": os.environ["AISWEB_API_KEY"], "apiPass": os.environ["AISWEB_API_PASS"], "area": area, **params}
    resp = SESSION.get(BASE_URL, params=query, timeout=120)
    resp.raise_for_status()
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        raise AiswebErro(f"Resposta não-XML para area={area!r}: {resp.text.strip()[:200]!r}")
    erro = root.find(".//*[@total='error']")
    if erro is not None:
        raise AiswebErro(erro.findtext("msg", "").strip())
    if root.find("error") is not None:
        raise AiswebErro(root.findtext("error").strip())
    return root


def itens(root):
    return root.findall("./*/item")


def total(root):
    return int(root[0].get("total", "0").strip())


def para_df(elementos):
    return pd.DataFrame([{f.tag: (f.text or "").strip() for f in el if len(f) == 0} for el in elementos])


def listar_paginado(area, pausa=0.3, **params):
    elementos, rowstart = [], 0
    while True:
        root = aisweb(area, rowstart=rowstart, **params)
        pagina = itens(root)
        elementos.extend(pagina)
        rowstart += len(pagina)
        if not pagina or rowstart >= total(root):
            return elementos
        time.sleep(pausa)
