import pandas as pd

from module_decea.dataset import historico_notam


def test_historico_marca_quando_cada_notam_apareceu_e_sumiu(tmp_path):
    coletas = {
        "2026-10-06_1005": ["1", "2"],
        "2026-10-06_1105": ["1", "2", "3"],
        "2026-10-06_1205": ["2", "3"],  # o 1 sumiu: cancelado ou substituído
    }
    for nome, ids in coletas.items():
        hora = pd.to_datetime(nome, format="%Y-%m-%d_%H%M").strftime("%Y-%m-%d %H:%M")
        pd.DataFrame({"coletado_em": hora, "id": ids}).to_csv(tmp_path / f"{nome}.csv.gz", index=False)

    hist = historico_notam(tmp_path)

    assert hist.loc["1", "visto_ultimo"] == pd.Timestamp("2026-10-06 11:05")
    assert hist.loc["3", "visto_primeiro"] == pd.Timestamp("2026-10-06 11:05")
    assert hist["coletas"].to_dict() == {"1": 2, "2": 3, "3": 2}
    assert hist["ainda_vigente"].to_dict() == {"1": False, "2": True, "3": True}
