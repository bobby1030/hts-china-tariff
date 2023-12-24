import pandas as pd
import re
import json

class Tariff:
    def __init__(self):
        self.CN_tariff_list = [
            {
                "heading": "9903.88.01",
                "wave": "List 1",
                "duty": 25,
            },
            {
                "heading": "9903.88.02",
                "wave": "List 2",
                "duty": 25,
            },
            {
                "heading": "9903.88.03",
                "wave": "List 3",
                "duty": 25,
            },
            {
                "heading": "9903.88.15",
                "wave": "List 4A",
                "duty": 7.5,
            },
        ]

    def get_CN_tariff(self, heading):
        for tariff in self.CN_tariff_list:
            if tariff.get("heading") == heading:
                return tariff.get("duty")
        return 0  # no China tariff found
    
    def get_CN_wave(self, heading):
        for tariff in self.CN_tariff_list:
            if tariff.get("heading") == heading:
                return tariff.get("wave")
        return None

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

        self.CN_subheading, self.CN_wave, self.CN_tariff = self.extract_china_tariff()

    def extract_china_tariff(self):
        tariffs = Tariff()

        try:
            # try to extract footnote
            footnote_texts = "".join([fn.get("value") for fn in self.footnotes])
            heading = re.findall(r"(9903\.88\.(01|02|03|15))", footnote_texts)[0][0]
            return (heading, tariffs.get_CN_wave(heading), tariffs.get_CN_tariff(heading))
        except:
            # no footnote found
            return (None, None, 0)

with open("htsdata/hts_2023_revision_11_json.json", "r") as htsjson:
    htsdata = json.load(htsjson)
    product_list = [Product(prod) for prod in htsdata]

htsdf = pd.DataFrame([prod.__dict__ for prod in product_list])

htsdf["hs8"] = htsdf["htsno"].str.extract(r"(\d{4}\.\d{2}\.\d{2})").replace("\.", "", regex=True)
htsdf["hs6"] = htsdf["htsno"].str.extract(r"(\d{4}\.\d{2})\.?\d{2}").replace("\.", "", regex=True)
htsdf["hs2"] = htsdf["htsno"].str.extract(r"(\d{2})\d{2}\.\d{2}\.\d{2}").replace("\.", "", regex=True)

columns = ["htsno", "hs8", "hs6", "hs2", "description", "general", "special", "CN_subheading", "CN_wave", "CN_tariff"]
htsdf[columns].to_csv("outputs/hts8_2023.csv", index=False)