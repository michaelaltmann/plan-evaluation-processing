import csv
from pathlib import Path
from wsgiref import headers
import pandas as pd
import os
from evaltools.data import remap
import sys
import json
from evaltools.data.fetch import Submission, individual, parse_id, tabularized

'''
Script that takes a CSV file that has a column with Districtr links
and generates block assignment files for each Districtr plan
'''

def as_submissions(df: pd.DataFrame):
    submissions = []
    df = df[df['link'].notna() &  df['link'].str.lower().str.startswith("https://districtr.org/")]
    df['districtrID'] = parse_id(df["link"], df=True)
    print('Getting plan for Districtr IDs: ', end='', flush=True)
    for _,row in df[df['districtrID'].notna()].iterrows():
      identifier = row['districtrID']
      if identifier and row['type'] != 'other':
          # Retrieve the required data points.
          print(f' {identifier}', end='', flush=True)
          districtr = individual(identifier)
          if "plan" in districtr:
            # Force all plan keys and values to strings.
            if "assignment" in districtr["plan"]:
              assignments = {
                  str(k): str(v) if type(v) is not list else str(v[0])
                  for k, v in districtr["plan"]["assignment"].items()
              }
            else:
              #User drew a completely empty map
              assignments = {}
          else:
            print (f"\nDistrictr for {identifier} object did not have plan")
            print (districtr)
            continue
          units = districtr["plan"]["units"]["name"]
          unitsType = districtr["plan"]["units"]["unitType"]
          tileset = districtr["plan"]["units"]["tilesets"][0]["sourceLayer"]

          # Create a new Submission.
          submissions.append(Submission(
              link=row["link"],
              id=identifier,
              plan=districtr["plan"],
              assignments=assignments,
              units=units,
              unitsType=unitsType,
              tileset=tileset,
              type=row["type"]
          ))
    print('')
    return submissions

def main(organization, file):

  ## Read a CSV file that includes a column called "link"
  df = pd.read_csv(file)
  
  ## Convert the DF to a list of Submission object
  ## This includes fetching the Districtr plan
  submissions = as_submissions(df)
  _plans = [s.dict() for s in submissions]
  submissions_df = pd.DataFrame.from_records(_plans)

  folder =  Path("exports") / organization / "geojson"
  Path(folder).mkdir(parents=True, exist_ok=True)

  # First, write the orig geojson with orig assignments and features
  print ('Writing maps to ', end='', flush=True)
  for submission in submissions:
    # Write row["plan"] to disk
    file = folder / f"map-{submission.id}.json"
    plan = submission.plan
    with open(file, 'w') as f:
      json.dump(plan, f)
    print (f" {file}", end='', flush=True)
  print ('')
  
  # Provide any remapping to target units
  unitmaps = {
        # "2020 VTDs": vtds_to_blocks,
        # "Precincts": precincts_to_blocks
    }
  plans = remap(submissions_df, unitmaps)
  
  # Write the resulting plans back to disk, one file per plan
  folder =  Path("exports") / organization / "assignments"
  Path(folder).mkdir(parents=True, exist_ok=True)

  print ('Writing assignments to ', end='', flush=True)
  for _,row in plans.iterrows():
    # Write row["plan"] to disk
    file = folder / f"assignments-{row['id']}.csv"
    plan = row["plan"]
    if row["type"] == "plan" or row["type"] == "draft":
      fieldnames = ['BLOCKID', 'DISTRICT']
    elif row["type"] == "coi":
      fieldnames = ['BLOCKID', 'COI']
    else:
      print(f"\nUnexpected type {row['type']}")
      fieldnames = ['BLOCKID', 'REGION']
    import csv
    with open(file, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
      writer.writerow(fieldnames)
      writer.writerows(plan.items())
    print (f" {file}", end='', flush=True)
  print ('')

def usage():
  print (f"Usage:  python {sys.argv[0]} ORG, CSV_FILE")
  print (f"Usage:  python {sys.argv[0]} minneapolis exports/minneapolis_prod_CumulativeSubmissions_2021-12-20T14:59.csv")


if __name__ == "__main__":
  _, organization, file = sys.argv 
  if organization and file:
    main(organization, file)
  else:
    usage()

