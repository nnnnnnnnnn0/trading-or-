"""Ichimoku combiné à d'autres signaux (or, journalier GC=F + dollar + taux).

ATTENTION MÉTHODE : le contrôle 2021-2026 a déjà été vu pour l'Ichimoku seul. On ne peut donc plus le garder « vierge ».
Remplacement : tout l'échantillon coupé en 4 blocs de durée égale ; un signal doit être positif dans au moins 3 blocs,
battre le hasard (décalages aléatoires de la même série de positions) et rester positif avec frais doublés.
Essais comptés : 16 combinaisons x 2 modes + 2 références, en plus des 34 essais du backtest précédent."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_indicateurs as bi  # noqa: E402
from backtest_indicateurs import atr, fr, machine, nw, nz, rsi, sharpe  # noqa: E402

RACINE = bi.RACINE
SORTIE = RACINE / "resultats" / "ichimoku_v1.md"
FC = bi.FRAIS_COTE


def facteur(nom, index):
    d = pd.read_csv(RACINE / "data" / nom)
    d["date"] = pd.to_datetime(d["date_utc"].str[:10])
    return d.drop_duplicates("date", keep="last").set_index("date")["close"].reindex(index).ffill(limit=3).shift(1)  # veille


def signaux(d):
    c, h, l = d["close"], d["high"], d["low"]
    n = len(d)
    tk = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kj = (h.rolling(26).max() + l.rolling(26).min()) / 2
    saf = (tk + kj) / 2
    sbf = (h.rolling(52).max() + l.rolling(52).min()) / 2
    sa, sb = saf.shift(26), sbf.shift(26)
    haut, bas = pd.concat([sa, sb], axis=1).max(axis=1), pd.concat([sa, sb], axis=1).min(axis=1)
    L0, S0 = (c > haut).values, (c < bas).values
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    up_m, dn_m = h.diff(), -l.diff()
    a14 = atr(h, l, c, 14)
    pdi = 100 * pd.Series(np.where((up_m > dn_m) & (up_m > 0), up_m, 0), index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / a14
    mdi = 100 * pd.Series(np.where((dn_m > up_m) & (dn_m > 0), dn_m, 0), index=d.index).ewm(alpha=1 / 14, adjust=False).mean() / a14
    adx = (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / 14, adjust=False).mean()
    r14 = rsi(c, 14)
    dxy = facteur("facteur_dollar_dxy.csv", d.index)
    t10 = facteur("facteur_taux_10ans.csv", d.index)
    vol = c.pct_change().rolling(20).std()
    pvol = vol.rolling(250).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)
    F = {  # (filtre achat, filtre vente)
        "Tenkan > Kijun (confirmation TK)": ((tk > kj).values, (tk < kj).values),
        "Chikou libre (cours > cours d'il y a 26 j)": ((c > c.shift(26)).values, (c < c.shift(26)).values),
        "Nuage futur de la bonne couleur": ((saf > sbf).values, (saf < sbf).values),
        "ADX 14 > 25 (tendance forte)": ((adx > 25).values, (adx > 25).values),
        "RSI 14 du bon côté de 50": ((r14 > 50).values, (r14 < 50).values),
        "RSI 14 pas en excès (< 70 / > 30)": ((r14 < 70).values, (r14 > 30).values),
        "MACD du bon côté de son signal": ((macd > sig).values, (macd < sig).values),
        "Dollar sous / sur sa MA50 (veille)": ((dxy < dxy.rolling(50).mean()).values, (dxy > dxy.rolling(50).mean()).values),
        "Taux 10 ans sous / sur leur MA50 (veille)": ((t10 < t10.rolling(50).mean()).values, (t10 > t10.rolling(50).mean()).values),
        "Volatilité hors des 20 % les plus hauts": ((pvol < 0.8).values, (pvol < 0.8).values),
    }
    base_ok = (sa.notna() & sb.notna()).values
    S = {}
    for nom, (fl, fs) in F.items():
        S[nom] = np.where(base_ok & L0 & fl, 1, np.where(base_ok & S0 & fs, -1, 0)).astype(float)
    t3l = F["Tenkan > Kijun (confirmation TK)"][0] & F["Chikou libre (cours > cours d'il y a 26 j)"][0] & F["Nuage futur de la bonne couleur"][0]
    t3s = F["Tenkan > Kijun (confirmation TK)"][1] & F["Chikou libre (cours > cours d'il y a 26 j)"][1] & F["Nuage futur de la bonne couleur"][1]
    S["Triple confirmation (TK + Chikou + nuage futur)"] = np.where(base_ok & L0 & t3l, 1, np.where(base_ok & S0 & t3s, -1, 0)).astype(float)
    adxf = F["ADX 14 > 25 (tendance forte)"][0]
    S["Triple confirmation + ADX > 25"] = np.where(base_ok & L0 & t3l & adxf, 1, np.where(base_ok & S0 & t3s & adxf, -1, 0)).astype(float)
    dl, ds = F["Dollar sous / sur sa MA50 (veille)"]
    S["Triple confirmation + dollar"] = np.where(base_ok & L0 & t3l & dl, 1, np.where(base_ok & S0 & t3s & ds, -1, 0)).astype(float)
    c_, kj_, tk_, hh, bb = c.values, nz(kj), nz(tk), nz(haut), nz(bas)
    S["Sortie sur la Kijun (au lieu du nuage)"] = machine(n, lambda t: base_ok[t] and L0[t], lambda t: c_[t] < kj_[t],
                                                         lambda t: base_ok[t] and S0[t], lambda t: c_[t] > kj_[t])
    lv, tkp, kjp = l.values, np.roll(tk_, 1), np.roll(kj_, 1)
    S["Entrée sur repli vers la Kijun"] = machine(
        n, lambda t: base_ok[t] and L0[t] and t > 0 and lv[t - 1] <= kjp[t] and c_[t] > kj_[t], lambda t: c_[t] < bb[t] or c_[t] < hh[t] * 0 + bb[t],
        lambda t: base_ok[t] and S0[t] and t > 0 and h.values[t - 1] >= kjp[t] and c_[t] < kj_[t], lambda t: c_[t] > hh[t])
    S["Croisement TK au-dessus / sous le nuage"] = machine(
        n, lambda t: base_ok[t] and t > 0 and tk_[t] > kj_[t] and tkp[t] <= kjp[t] and c_[t] > hh[t], lambda t: tk_[t] < kj_[t],
        lambda t: base_ok[t] and t > 0 and tk_[t] < kj_[t] and tkp[t] >= kjp[t] and c_[t] < bb[t], lambda t: tk_[t] > kj_[t])
    S["RÉFÉRENCE : Ichimoku seul (cours / nuage)"] = np.where(base_ok & L0, 1, np.where(base_ok & S0, -1, 0)).astype(float)
    return S


def main():
    d = bi.charger()
    n = len(d)
    ret = d["close"].pct_change().shift(-1).fillna(0).values.copy()
    ret[-1] = 0
    deb = 270
    bornes = np.linspace(deb, n - 1, 5).astype(int)
    S = signaux(d)
    rng = np.random.default_rng(2026)
    lignes, probables, proches = [], [], []
    bh = ret[deb:n - 1]
    for nom, pos in S.items():
        for mode in ("achat + vente", "achat seulement"):
            p = pos.copy() if mode == "achat + vente" else np.clip(pos, 0, None)
            x, x2, prev = bi.perf(p, ret, deb, n - 1)
            blocs = []
            for a, b in zip(bornes[:-1], bornes[1:]):
                xb, _, _ = bi.perf(p, ret, a, b)
                blocs.append(xb.mean() * 252 * 100)
            pv = bi.p_decalage(p, ret, deb, n - 1, x.mean(), rng)
            t = nw(x)
            entrees = int(((np.abs(np.diff(np.concatenate([[0], p[deb:n - 1]]))) > 0) & (p[deb:n - 1] != 0)).sum())
            pos3 = sum(1 for b in blocs if b > 0)
            ok = pos3 >= 3 and x2.mean() > 0 and t >= 2.5 and pv <= 0.01
            proche = pos3 >= 3 and x2.mean() > 0 and pv <= 0.05
            v = "Candidat" if ok else ("À surveiller" if proche else "Rejeté")
            if ref := nom.startswith("RÉFÉRENCE"):
                v = "Référence"
            elif ok:
                probables.append("%s (%s)" % (nom, mode))
            elif proche:
                proches.append("%s (%s)" % (nom, mode))
            lignes.append("| %s | %s | %s | %s | %s | %s | %s | %s | %d | %s |" % (
                nom, mode, fr(sharpe(x)), fr(x.mean() * 252 * 100, 1) + " %", fr(t, 1), fr(pv * 100, 0) + " %",
                " / ".join(fr(b, 0) for b in blocs), fr(sharpe(x2)), entrees, v))
    dates = [str(d.index[b].date())[:4] for b in bornes]
    texte = ["# Ichimoku combiné à d'autres signaux (v1)", "",
             "Données : %d jours (%s à %s), futures GC=F, dollar et taux. 4 blocs de durée égale : %s." % (
                 n, d.index[0].date(), d.index[-1].date(), " | ".join("%s-%s" % (dates[i], dates[i + 1]) for i in range(4))),
             "", "**%d essais comptés ici, plus 34 au backtest précédent (soit %d au total).** Paramètres standard, aucun réglage." % (len(lignes), len(lignes) + 34),
             "", "**Un bon backtest ne prouve rien sur l'avenir ; un mauvais est une information utile.**", "",
             "**Précaution** : la période 2021-2026 avait déjà été vue pour l'Ichimoku seul, donc plus de contrôle vierge. Un résultat n'est retenu que s'il est positif dans au moins 3 blocs sur 4, bat le hasard (au plus 1 %), a t ≥ 2,5 et reste positif avec frais doublés. Même alors, il n'est qu'un **candidat à confirmer en paper trading**.", "",
             "Référence : garder l'or sur toute la période = Sharpe %s, rendement annuel %s %%." % (fr(sharpe(bh)), fr(bh.mean() * 252 * 100, 1)), "",
             "| Stratégie | Mode | Sharpe | Rendement annuel | t | Hasard | Rendement annuel par bloc | Sharpe frais ×2 | Entrées | Verdict |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"] + lignes + ["", "## Conclusion", ""]
    texte.append("Candidats : " + "; ".join(probables) + "." if probables else "**Aucune combinaison ne passe le filtre strict.**")
    if proches:
        texte.append("\nÀ surveiller (positifs dans 3 blocs, au plus 5 % de hasard, mais pas assez nets) : " + "; ".join(proches) + ".")
    texte += ["", "## Limites", "",
              "- Signal et exécution à la même clôture ; frais 0,05 % l'aller-retour, sans financement de nuit.",
              "- Dollar et taux de la veille pour éviter le regard dans le futur (clôtures décalées).",
              "- %d essais au total : plusieurs résultats flatteurs sont attendus par pur hasard. Seule la confirmation en conditions réelles (paper trading) compte." % (len(lignes) + 34),
              "- Le mode « achat seulement » profite de la hausse de l'or ; le test de hasard le corrige en partie."]
    SORTIE.write_text("\n".join(texte) + "\n", encoding="utf-8")
    print("\n".join(texte))


if __name__ == "__main__":
    main()
