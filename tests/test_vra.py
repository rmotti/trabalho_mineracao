import pandas as pd
import pytest

from module_decea.vra import COLUNAS, carregar_vra, para_utc


def _salvar_mes(pasta, ano, mes, voo):
    linha = {c: "" for c in COLUNAS} | {
        "Número Voo": voo,
        "Partida Prevista": f"01/{mes:02d}/{ano} 10:00",
        "Partida Real": f"01/{mes:02d}/{ano} 10:45",
        "Situação Voo": "REALIZADO",
    }
    pd.DataFrame([linha]).to_csv(pasta / f"VRA_{ano}_{mes:02d}.csv", sep=";", index=False)


def test_carrega_so_os_anos_pedidos(tmp_path):
    _salvar_mes(tmp_path, 2024, 12, "1")
    _salvar_mes(tmp_path, 2025, 1, "2")
    _salvar_mes(tmp_path, 2025, 2, "3")

    assert carregar_vra(2025, pasta=tmp_path)["voo"].tolist() == ["2", "3"]
    assert carregar_vra(2024, 2025, pasta=tmp_path)["voo"].tolist() == ["1", "2", "3"]
    assert carregar_vra(2025, pasta=tmp_path)["atraso_partida_min"].tolist() == [45, 45]


def test_ano_nao_baixado_avisa(tmp_path):
    with pytest.raises(FileNotFoundError, match="baixar_vra"):
        carregar_vra(2019, pasta=tmp_path)


def test_para_utc_segue_o_horario_de_verao_de_brasilia():
    horarios = pd.Series(
        pd.to_datetime(
            [
                "2017-01-10 12:00",  # horário de verão: UTC-2
                "2017-07-10 12:00",  # fora dele: UTC-3
                "2025-01-10 12:00",  # sem horário de verão desde 2019
                "2017-10-15 00:30",  # hora que não existiu (relógio pulou de 00:00 para 01:00)
            ]
        )
    )
    assert (
        para_utc(horarios).tolist()
        == pd.to_datetime(["2017-01-10 14:00", "2017-07-10 15:00", "2025-01-10 15:00", "2017-10-15 03:00"]).tolist()
    )
