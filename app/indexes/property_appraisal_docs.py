import csv

"""
Generate Python Python program that will read CSV file, and output array of items, one item per row.
Each item in the array will have two elements:
1) Text string generated from the columns and their values in the row.
2) Dictionary with keys and values for each column in the row.
The keys in the dictionary will be remapped as in the below dictionary:
key_for_search = {
    "propID": "property ID",
    "legalDescription": "legal description",
    "dbaName": "doing business as name",
    "situsBldgNum": "situs building number",
    "situsStreetPrefix": "situs street prefix",
    "situsStreetName": "situs street name",
    "situsStreetSuffix": "situs street suffix",
    "situsUnit": "situs unit",
    "situsCity": "situs city",
    "situsZip": "situs ZIP",
    "situsConcat": "situs concatenated",
    "situsConcatShort": "situs concatenated short",
    "ownerID": "owner ID",
    "ownerName": "owner name",
    "ownerNameAddtl": "owner name additional",
}
"""
key_for_search = {
    "propID": "property ID",
    "legalDescription": "legal description",
    "dbaName": "doing business as name",
    "situsBldgNum": "situs building number",
    "situsStreetPrefix": "situs street prefix",
    "situsStreetName": "situs street name",
    "situsStreetSuffix": "situs street suffix",
    "situsUnit": "situs unit",
    "situsCity": "situs city",
    "situsZip": "situs ZIP",
    "situsConcat": "situs concatenated",
    "situsConcatShort": "situs concatenated short",
    "ownerID": "owner ID",
    "ownerName": "owner name",
    "ownerNameAddtl": "owner name additional",
}


def read_csv_and_generate_items(file_path):
    items = []
    with open(file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            text_string = ", ".join(
                [f"{key_for_search.get(col, col)}: {val}" for col, val in row.items()]
            )
            remapped_dict = {
                key_for_search.get(col, col): val for col, val in row.items()
            }
            items.append([text_string, remapped_dict])
    return items
