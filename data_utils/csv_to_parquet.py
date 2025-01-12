import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os


def csv_to_parquet(csv_file_path, parquet_file_path):
    """
    Load a CSV file, resolve schema inconsistencies, and save it in Parquet format.

    Args:
        csv_file_path (str): Path to the CSV file.
        parquet_file_path (str): Output Parquet file path.
    """
    # Load CSV file
    print("Loading CSV file...")
    df = pd.read_csv(csv_file_path)
    # df["situsZip"] = df["situsZip"].astype(str)

    # Ensure situsZip is convertible to integer
    if "situsZip" in df.columns:
        print("Converting 'situsZip' to integer...")
        df["situsZip"] = (
            pd.to_numeric(df["situsZip"], errors="coerce").fillna(0).astype(int)
        )

    # Display schema
    print("Schema before conversion (Column Names and Data Types):")
    print(df.dtypes)

    # Resolve schema inconsistencies
    for col in df.columns:
        if df[col].dtype == "object":
            # Convert mixed-type object columns to strings
            df[col] = df[col].astype(str)

    # Display schema after conversion
    print("Schema after conversion (Column Names and Data Types):")
    print(df.dtypes)

    # Save to Parquet
    print(f"Saving to Parquet format at: {parquet_file_path}")
    df.to_parquet(parquet_file_path, index=False, engine="pyarrow")
    print("Conversion complete!")


def csv_to_parquet_filtered_old(
    csv_file_path, parquet_file_path, text_file_path, filter_column, filter_value
):
    """
    Load a CSV file, filter rows based on a condition, force 'situsZip' to string,
    save filtered data in Parquet format, and store filtered data in a text file.

    Args:
        csv_file_path (str): Path to the CSV file.
        parquet_file_path (str): Output Parquet file path.
        text_file_path (str): Output text file path to store filtered data.
        filter_column (str): Column name to apply the filter condition.
        filter_value (str): Value to filter the rows on.
    """
    # Load CSV file
    print("Loading CSV file...")
    df = pd.read_csv(csv_file_path)

    # Ensure 'situsZip' is converted to string
    if "situsZip" in df.columns:
        print("Converting 'situsZip' to string...")
        df["situsZip"] = df["situsZip"].astype(str)

    # Filter rows where filter_column == filter_value
    print(f"Filtering rows where '{filter_column}' equals '{filter_value}'...")
    filtered_df = df[df[filter_column] == filter_value]

    # Save filtered data to Parquet
    print(f"Saving filtered data to Parquet format at: {parquet_file_path}")
    filtered_df.to_parquet(parquet_file_path, index=False, engine="pyarrow")

    # Convert filtered data to key-value format and save to text file
    print(f"Saving filtered data to text file at: {text_file_path}")
    with open(text_file_path, "w") as file:
        for _, row in filtered_df.iterrows():
            row_dict = row.to_dict()
            line = ", ".join(f"{key}: {value}" for key, value in row_dict.items())
            file.write(line + "\n")

    print("Conversion to Parquet and saving to text file complete!")


import pandas as pd
import os


def csv_to_parquet_filtered(
    csv_file_path,
    parquet_file_path,
    text_file_prefix,
    filter_column,
    filter_value,
    max_records_per_file=50000,
):
    """
    Load a CSV file, filter rows based on partial match in 'filter_column' and 'ownerAddrZip',
    force 'situsZip' to string, save filtered data in Parquet format, and split into text files.

    Args:
        csv_file_path (str): Path to the CSV file.
        parquet_file_path (str): Output Parquet file path.
        text_file_prefix (str): Prefix for output text files.
        filter_column (str): Column name to apply the filter condition.
        filter_value (str): Value to partially match in 'filter_column' and 'ownerAddrZip'.
        max_records_per_file (int): Maximum number of records per text file.
    """
    # Load CSV file
    print("Loading CSV file...")
    df = pd.read_csv(csv_file_path)

    # Ensure 'situsZip' is converted to string
    if "situsZip" in df.columns:
        print("Converting 'situsZip' to string...")
        df["situsZip"] = df["situsZip"].astype(str)

    # Ensure relevant columns are strings for partial matching
    df[filter_column] = df[filter_column].astype(str)
    if "ownerAddrZip" in df.columns:
        df["ownerAddrZip"] = df["ownerAddrZip"].astype(str)

    # Filter rows based on partial match
    print(
        f"Filtering rows where '{filter_value}' is partially matched in '{filter_column}' or 'ownerAddrZip'..."
    )
    # Ensure filter_value is a string
    filter_value = str(filter_value)

    # Filter rows where the value is partially matched in 'filter_column' or 'ownerAddrZip'
    filtered_df = df[
        df[filter_column].str.contains(filter_value, na=False, case=False)
        | df["ownerAddrZip"].str.contains(filter_value, na=False, case=False)
    ]

    # Save filtered data to Parquet
    # print(f"Saving filtered data to Parquet format at: {parquet_file_path}")
    # filtered_df.to_parquet(parquet_file_path, index=False, engine="pyarrow")

    # Split filtered data into multiple text files
    print("Splitting filtered data into multiple text files...")
    total_records = len(filtered_df)
    file_index = 1

    for start in range(0, total_records, max_records_per_file):
        end = start + max_records_per_file
        chunk_df = filtered_df.iloc[start:end]

        # Convert the chunk to key-value format and save to a text file
        text_file_path = f"{text_file_prefix}_{file_index}.txt"
        print(f"Saving {len(chunk_df)} records to {text_file_path}...")

        with open(text_file_path, "w") as file:
            for _, row in chunk_df.iterrows():
                row_dict = row.to_dict()
                line = ", ".join(f"{key}: {value}" for key, value in row_dict.items())
                file.write(line + "\n")

        print(f"File {text_file_path} saved.")
        file_index += 1

    print("All files have been successfully created.")


# Example usage
data_path = "/usr/local/stage3technical/var/data/Colling-property-data"
csv_file = os.path.join(data_path, "Collin_CAD_Appraisal_Data_2024_20241208.csv")
parquet_file_75024 = os.path.join(
    data_path, "Collin_CAD_Appraisal_Data_2024_20241208-zip-75024.parquet"
)
parquet_file = os.path.join(
    data_path, "Collin_CAD_Appraisal_Data_2024_20241208.parquet"
)
text_file_75024 = os.path.join(data_path, "Collin_CAD_Appraisal_Data_75024.txt")
# csv_to_parquet(csv_file, parquet_file)
csv_to_parquet_filtered(
    csv_file, parquet_file_75024, text_file_75024, "situsZip", "75024"
)
