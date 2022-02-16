"""
Notebook/script to retrieve data from portal for an
organization and generate reports. 
Note: This retrieves personal information that must be secured.  
It also includes submissions and comments that are hidden or no verified.
This full set of data should only be provided to the
customer through secure channels and with appropriate caveats.
"""

from datetime import datetime, timezone
from pathlib import Path
from evaltools.data.full_data import json_as_dataframes, portal_data_json
import os

def get_portal_data_and_generate_csvs(environment: str, organization: str, API_KEY: str):
    """
  Get data from portal API and save as CSVs to local disk 
  """
    json = portal_data_json(environment, organization, API_KEY)

    submissions_df, comments_df = json_as_dataframes(json, organization)

    ## Informational logging of unverified/hidden entries
    df = submissions_df[
                (submissions_df["hidden"] == True)
                | (submissions_df["emailverified"] == False) & ~submissions_df["type"].isin(["plan", "coi"])
            ]
    print(f"Hidden or unverified submissions {len(df.index)}")
    print(df)
            
    df = comments_df[(comments_df["hidden"] == True) | (comments_df["emailverified"] == False)]
    print(f"Hidden or unverified comments {len(df.index)}")
    print(df)

    ### Write to disk
    datestring = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M")

    Path("exports").mkdir(parents=True, exist_ok=True)

    file = (
        f"exports/{organization}_{environment}_CumulativeSubmissions_{datestring}.csv"
    )
    submissions_df.sort_values(by="id").to_csv(file,index=False)
    print(f"Wrote {len(submissions_df.index)} to {file}")

    file = f"exports/{organization}_{environment}_CumulativeComments_{datestring}.csv"
    comments_df.sort_values(by="id").to_csv(file, index=False)
    print(f"Wrote {len(comments_df.index)} to {file}")


# %%
def usage():
    print(f"Usage: python csv_reports.py ENV ORGANIZATION")
    print(f"Ex:    python csv_reports.py qa ohio")
    print(f"Ex:    python csv_reports.py prod ohio")
    print(f"Ex:    python csv_reports.py main michigan")


# %%
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    if "ipykernel" in sys.argv[0]:
        environment = "qa"
        organization = "minneapolis"
    else:
        # Support running as a plain python script
        if len(sys.argv) >= 2:
            environment = sys.argv[1]
            organization = sys.argv[2]

    # At this point, environment and organization should have been set
    if environment and organization:
        print(f"Loading .env.{environment}")
        load_dotenv(f".env.{environment}")
        if "API_KEY" not in os.environ:
            raise Exception(
            f"Please define API_KEY environment variable.  Easiest way is to use a .env file and the python-dotenv package"
        )
        API_KEY = os.getenv(f"API_KEY")
        get_portal_data_and_generate_csvs(environment, organization, API_KEY)

    else:
        usage()

