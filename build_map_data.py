"""
build_map_data.py — reproducible pipeline for the Chicago food-access map.

Inputs (not committed; see README):
  - chicago_food_access.dta : USDA Food Access Research Atlas (2019), Cook County,
                              merged to Chicago community areas (ECO 575 practicum data)
  - tracts_raw.geojson      : City of Chicago 2010 census tract boundaries
                              (data.cityofchicago.org dataset 74p9-q2aq)

Output:
  - site/tracts.geojson     : tract polygons joined to model inputs + predicted
                              food-desert probability, ready for the Leaflet map.

Model: logistic regression of USDA LILA-at-half-mile status on
  % Black, % Hispanic, log median family income, % SNAP, % no-vehicle.
Predicted probabilities use the published full-specification coefficients
(cluster-robust SEs by community area).
"""
import json
import numpy as np
import pandas as pd

DTA = "data/chicago_food_access.dta"
GEO = "data/tracts_raw.geojson"
OUT = "tracts.geojson"

# Published full-specification (Spec 2) logit coefficients
B = dict(
    const=8.531588467449476,
    pct_black=0.026309172332362084,
    pct_hispanic=0.007552025918424031,
    log_medfaminc=-0.9553299893687184,
    pct_snap=0.010724191224655767,
    pct_hunv=-0.03416965421446072,
)
COVARS = ["pct_black", "pct_hispanic", "log_medfaminc", "pct_snap", "pct_hunv"]


def load_tracts():
    df = pd.read_stata(DTA)
    df = df[df["area_name"].notna() & (df["area_name"].astype(str).str.strip() != "")].copy()
    num = ["censustract", "pop2010", "ohu2010", "tractblack", "tracthispanic",
           "tractsnap", "tracthunv", "medianfamilyincome", "povertyrate",
           "lilatracts_halfand10"]
    for c in num:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["geoid"] = df["censustract"].astype("int64").astype(str).str.zfill(11)
    df["pct_black"] = 100 * df["tractblack"] / df["pop2010"]
    df["pct_hispanic"] = 100 * df["tracthispanic"] / df["pop2010"]
    df["pct_snap"] = 100 * df["tractsnap"] / df["ohu2010"]
    df["pct_hunv"] = 100 * df["tracthunv"] / df["ohu2010"]
    df["log_medfaminc"] = np.log(df["medianfamilyincome"].replace(0, np.nan))

    z = B["const"] + sum(B[k] * df[k] for k in COVARS)
    df["pred"] = 1 / (1 + np.exp(-z))
    return df


def trim(coords, p=5):
    if isinstance(coords[0], (float, int)):
        return [round(coords[0], p), round(coords[1], p)]
    return [trim(c, p) for c in coords]


def main():
    df = load_tracts()
    by_id = df.set_index("geoid").to_dict("index")
    geo = json.load(open(GEO))

    feats = []
    for f in geo["features"]:
        gid = f["properties"].get("geoid10")
        d = by_id.get(gid)
        if not d:
            continue
        g = f["geometry"]
        g["coordinates"] = trim(g["coordinates"])
        nn = lambda v: None if pd.isna(v) else v
        feats.append({
            "type": "Feature",
            "geometry": g,
            "properties": {
                "geoid": gid,
                "tract": f["properties"].get("name10"),
                "area": (d["area_name"] or "").title(),
                "pred": None if pd.isna(d["pred"]) else round(d["pred"], 3),
                "actual": nn(d["lilatracts_halfand10"]),
                "pct_black": nn(round(d["pct_black"], 1)),
                "pct_hispanic": nn(round(d["pct_hispanic"], 1)),
                "pct_snap": nn(round(d["pct_snap"], 1)),
                "pct_hunv": nn(round(d["pct_hunv"], 1)),
                "medinc": None if pd.isna(d["medianfamilyincome"]) else round(d["medianfamilyincome"]),
                "poverty": nn(round(d["povertyrate"], 1)),
                "pop": nn(d["pop2010"]),
            },
        })

    json.dump({"type": "FeatureCollection", "features": feats},
              open(OUT, "w"), separators=(",", ":"))
    n_pred = sum(1 for x in feats if x["properties"]["pred"] is not None)
    print(f"wrote {OUT}: {len(feats)} tracts ({n_pred} with predictions)")


if __name__ == "__main__":
    main()
