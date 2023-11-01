import pandas as pd
import re
import json

class Tariff:
    def __init__(self):
        self.CN_tariff_list = [
            {
                "heading": "9903.88.01",
                "duty": 25,
            },
            {
                "heading": "9903.88.02",
                "duty": 25,
            },
            {
                "heading": "9903.88.03",
                "duty": 25,
            },
            {
                "heading": "9903.88.15",
                "duty": 7.5,
            },
        ]

    def get_CN_tariff(self, heading):
        for tariff in self.CN_tariff_list:
            if tariff.get("heading") == heading:
                return tariff.get("duty")
        return 0  # no China tariff found


class Product:
    def __init__(self, dict):
        self.htsno = dict.get("htsno")
        self.indent = dict.get("indent")
        self.description = dict.get("description")
        self.units = dict.get("units")
        self.general = dict.get("general")
        self.special = dict.get("special")
        self.other = dict.get("other")
        self.footnotes = dict.get("footnotes")
        self.quotaQuantity = dict.get("quotaQuantity")
        self.additionalDuties = dict.get("additionalDuties")

        self.CN_subheading, self.CN_tariff = self.extract_china_tariff()

    def extract_china_tariff(self):
        tariffs = Tariff()

        try:
            # try to extract footnote
            footnote_text = self.footnotes[0].get("value")
            heading = re.findall(r"9903\.88\.\d{2}", footnote_text)[0]
            return (heading, tariffs.get_CN_tariff(heading))
        except:
            # no footnote found
            return (None, 0)

with open("htsdata/hts_2023_revision_11_json.json", "r") as htsjson:
    htsdata = json.load(htsjson)
    product_list = [Product(prod) for prod in htsdata]

htsdf = pd.DataFrame([prod.__dict__ for prod in product_list])


columns = ["htsno", "description", "general", "special", "CN_subheading", "CN_tariff"]
hts8df = htsdf.loc[htsdf["htsno"].str.len() == 10][columns] # keep 8-digit entries

hts8df["hs8"] = hts8df["htsno"].str.extract(r"(\d{4}\.\d{2}\.\d{2})").replace("\.", "", regex=True)
hts8df["hs6"] = hts8df["htsno"].str.extract(r"(\d{4}\.\d{2})\.?\d{2}").replace("\.", "", regex=True)
hts8df["hs2"] = hts8df["htsno"].str.extract(r"(\d{2})\d{2}\.\d{2}\.\d{2}").replace("\.", "", regex=True)

hts8df.to_csv("outputs/hts8_2023.csv", index=False)