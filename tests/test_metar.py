import pandas as pd

from module_decea.metar import carregar_iem, decodificar


def test_cavok_vale_visibilidade_maxima_e_ceu_ilimitado():
    d = decodificar("SBGR 101200Z 09010KT CAVOK 25/15 Q1015")
    assert (d["vis_m"], d["teto_ft"]) == (9999, 99999)
    assert (d["vento_dir"], d["vento_kt"]) == (90, 10)
    assert (d["temp_c"], d["orvalho_c"], d["qnh"]) == (25, 15, 1015)


def test_teto_e_a_camada_bkn_ovc_mais_baixa():
    d = decodificar("SBSP 101800Z 32015G28KT 3000 TSRA FEW015CB BKN008 OVC020 18/17 Q1012")
    assert d["teto_ft"] == 800
    assert d["vis_m"] == 3000
    assert d["rajada_kt"] == 28
    assert d["trovoada"] and d["chuva"] and d["cb"]


def test_descarta_boletim_sintetico_do_iem(tmp_path):
    pd.DataFrame(
        {
            "station": ["SBGR"] * 3,
            "valid": ["2011-03-01 15:00", "2011-03-01 16:00", "2011-03-01 17:00"],
            "metar": [
                "SBGR 011500Z AUTO 33011KT 7SM 32/15 A3000 RMK T03200150 IEM_DS3505",
                "SBGR 011600Z 33008KT 9999 SCT030 BKN080 29/21 Q1011",
                "SBGR 011700Z NIL",
            ],
        }
    ).to_csv(tmp_path / "SBGR_2011.csv", index=False)
    assert carregar_iem(tmp_path / "SBGR_2011.csv")["hora_utc"].tolist() == [pd.Timestamp("2011-03-01 16:00")]
