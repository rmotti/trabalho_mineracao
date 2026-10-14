"""Leitura do VRA (Voo Regular Ativo) da ANAC: siros.anac.gov.br/siros/registros/diversos/vra/"""
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


def para_utc(horario):
    """Horário do VRA para UTC (sem fuso, como o METAR do IEM).

    Todos os voos estão no horário oficial de Brasília, com horário de verão até fevereiro de 2019 (UTC−2 nesses meses),
    e não no horário local de cada aeroporto. Na hora repetida do fim do horário de verão, assume o horário de verão.
    """
    return (horario.dt.tz_localize("America/Sao_Paulo", ambiguous=True, nonexistent="shift_forward")
            .dt.tz_convert("UTC").dt.tz_localize(None))


def carregar_vra(*anos, pasta=RAW_DATA_DIR / "vra"):
    """Junta os meses baixados dos anos pedidos: carregar_vra(2025) ou carregar_vra(2023, 2024).

    Vale de 2010 em diante. Até 2009 o arquivo é outro (vírgula, latin-1, sem aeronave nem assentos).
    """
    arquivos = [f for ano in anos for f in sorted(pasta.glob(f"VRA_{ano}_*.csv"))]
    if not arquivos:
        raise FileNotFoundError(f"nenhum VRA de {anos} em {pasta}: rode baixar_vra(ano) antes")
    partes = [pd.read_csv(f, sep=";", dtype=str, usecols=list(COLUNAS)) for f in arquivos]
    df = pd.concat(partes, ignore_index=True).rename(columns=COLUNAS)
    for c in ["partida_prev", "partida_real", "chegada_prev", "chegada_real"]:
        df[c] = pd.to_datetime(df[c], format=FMT, errors="coerce")
    df["partida_prev_utc"] = para_utc(df["partida_prev"])
    df["assentos"] = pd.to_numeric(df["assentos"], errors="coerce")
    df["cancelado"] = df["situacao"].eq("CANCELADO")
    df["atraso_partida_min"] = (df["partida_real"] - df["partida_prev"]).dt.total_seconds() / 60
    df["atraso_chegada_min"] = (df["chegada_real"] - df["chegada_prev"]).dt.total_seconds() / 60
    # Critério da ANAC nos relatórios de pontualidade: atraso acima de 30 minutos
    df["atrasado_30"] = df["atraso_partida_min"] > 30
    return df


def voos_regulares_domesticos(df):
    """Só voos regulares (DI = 0) de linha doméstica de passageiros, com horário previsto.

    Até 2018 a ANAC separava as linhas regionais (tipo R) das nacionais (N); de 2019 em diante é tudo N.
    """
    return df[(df["di"] == "0") & df["tipo_linha"].isin(["N", "R"]) & df["partida_prev"].notna()].copy()
