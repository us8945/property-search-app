import csv
import os


def reformat_csv_to_files(input_csv, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Define the key replacements
    key_replacements = {
        "ownerName": "owner name",
        "ownerNameAddtl": "owner name additional",
    }

    # Read the CSV file
    with open(input_csv, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        count = 0
        for row in reader:
            # Check the condition for ownerAddrZip or situsZip
            owner_zip = row.get("ownerAddrZip", "")
            situs_zip = row.get("situsZip", "")
            if owner_zip == "75024" or situs_zip == "75024":
                # Only process if condition met
                count += 1
                output_pairs = []
                for key, value in row.items():
                    # Apply key replacements if applicable
                    new_key = key_replacements.get(key, key)
                    # Format the key-value pair as "key"::"value"
                    pair_str = f'"{new_key}"::"{value}"'
                    output_pairs.append(pair_str)

                # Create a single line with all pairs space-separated
                output_line = " ".join(output_pairs)

                # Construct the output file name (e.g. line_1.txt, line_2.txt, etc.)
                output_filename = os.path.join(output_folder, f"line_{count}.txt")

                # Write the output line to the file
                with open(output_filename, "w", encoding="utf-8") as outfile:
                    outfile.write(output_line + "\n")

    # Define the key replacements


key_replacements = {
    "propYear": "property year",
    "propID": "property ID",
    "geoID": "geographical ID",
    "propType": "property type",
    "propSubType": "property subtype",
    "propCategoryCode": "property category code",
    "legalDescription": "legal description",
    "dbaName": "doing business as name",
    "propCreateDate": "property creation date",
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
    "ownerAddrLine1": "owner address line 1",
    "ownerAddrLine2": "owner address line 2",
    "ownerAddrCity": "owner address city",
    "ownerAddrState": "owner address state",
    "ownerAddrZip": "owner address ZIP",
    "ownerAddrCountry": "owner address country",
    "taxAgentID": "tax agent ID",
    "taxAgentName": "tax agent name",
    "imprvYearBuilt": "improvement year built",
    "currValYear": "current value year",
    "currValImprv": "current value improvement",
    "currValLand": "current value land",
    "currValMarket": "current value market",
    "currValAgLoss": "current value agriculture loss",
    "currValAppraised": "current value appraised",
}

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


def reformat_csv_to_single_file(input_csv, output_file):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Open a single output file

    with open(input_csv, mode="r", newline="", encoding="utf-8") as csvfile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:

        reader = csv.DictReader(csvfile)

        for row in reader:
            # Check the condition for ownerAddrZip or situsZip
            owner_zip = row.get("ownerAddrZip", "")
            situs_zip = row.get("situsZip", "")
            if owner_zip == "75024" or situs_zip == "75024":
                # Gather only the keys that are in key_replacements
                output_pairs = []
                for original_key, new_key in key_replacements.items():
                    if original_key in row:
                        value = row[original_key]
                        pair_str = f'"{new_key}"::"{value}"'
                        output_pairs.append(pair_str)

                # If no keys from key_replacements are found, skip this row
                if not output_pairs:
                    continue

                # Create a single line with all pairs space-separated
                output_line = " ".join(output_pairs)

                # Write the output line to the single file
                outfile.write(output_line + "\n")


def reformat_csv_to_csv(input_csv, output_file):

    # Prepare the output CSV fieldnames based on the dictionary values
    fieldnames = list(key_replacements.values())

    with open(input_csv, mode="r", newline="", encoding="utf-8") as csvfile, open(
        output_file, mode="w", newline="", encoding="utf-8"
    ) as outfile:

        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Write the header row to the output CSV
        writer.writeheader()

        for row in reader:
            # Check the condition for ownerAddrZip or situsZip
            owner_zip = row.get("ownerAddrZip", "")
            situs_zip = row.get("situsZip", "")

            if owner_zip == "75024" or situs_zip == "75024":
                # Build a dictionary for the row to write to the output CSV
                output_row = {}
                for original_key, new_key in key_replacements.items():
                    # If the original key is present in the row, use that value
                    # Otherwise, leave it as an empty string
                    output_row[new_key] = row.get(original_key, "")

                # Write the filtered and remapped row to the CSV
                writer.writerow(output_row)


# Example usage:
# reformat_csv_to_files("input.csv", "output_folder")
# Example usage:
data_path = "/usr/local/stage3technical/var/data/Colling-property-data"
csv_file = os.path.join(data_path, "Collin_CAD_Appraisal_Data_2024_20241208.csv")
output_file = os.path.join(data_path, "Collin_CAD_Appraisal_Data_75024.csv")
output_folder = os.path.join(data_path, "csv_by_line")
# reformat_csv_to_files(csv_file, output_folder)
# reformat_csv_to_single_file(csv_file, output_file)
reformat_csv_to_csv(csv_file, output_file)
