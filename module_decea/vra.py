"""Leitura do VRA (Voo Regular Ativo) da ANAC: siros.anac.gov.br/siros/registros/diversos/vra/"""
import glob

import pandas as pd

from module_decea.config import RAW_DATA_DIR

COLUNAS = {
    "Sigla ICAO Empresa Aérea": "empresa",
    "Número Voo": "voo",
    "Código DI": "di",
    "Código Tipo Linha": "tipo_linha",
    "Modelo Equipamento": "aeronave",
    "Número de Assentos": "assentos",
    "Sigla ICAO Aeroporto Origem": "origem",
    "Partida Prevista": "partida_prev",
    "Partida Real": "partida_real",
    "Sigla ICAO Aeroporto Destino": "destino",
    "Chegada Prevista": "chegada_prev",
    "Chegada Real": "chegada_real",
    "Situação Voo": "situacao",
}
FMT = "%d/%m/%Y %H:%M"


def carregar_vra(padrao=str(RAW_DATA_DIR / "vra" / "VRA_*.csv")):
    partes = [pd.read_csv(f, sep=";", dtype=str, usecols=list(COLUNAS)) for f in sorted(glob.glob(padrao))]
    df = pd.concat(partes, ignore_index=True).rename(columns=COLUNAS)
    for c in ["partida_prev", "partida_real", "chegada_prev", "chegada_real"]:
        df[c] = pd.to_datetime(df[c], format=FMT, errors="coerce")
    df["assentos"] = pd.to_numeric(df["assentos"], errors="coerce")
    df["cancelado"] = df["situacao"].eq("CANCELADO")
    df["atraso_partida_min"] = (df["partida_real"] - df["partida_prev"]).dt.total_seconds() / 60
    df["atraso_chegada_min"] = (df["chegada_real"] - df["chegada_prev"]).dt.total_seconds() / 60
    # Critério da ANAC nos relatórios de pontualidade: atraso acima de 30 minutos
    df["atrasado_30"] = df["atraso_partida_min"] > 30
    return df


def voos_regulares_domesticos(df):
    """Só voos regulares (DI = 0) de linha doméstica de passageiros (tipo N), com horário previsto."""
    return df[(df["di"] == "0") & (df["tipo_linha"] == "N") & df["partida_prev"].notna()].copy()
