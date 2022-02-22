import sys
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
import json

def main(organization):
  draft_file = f"../submissionform/public/locales/en-{organization}/drafts.json"
  js = json.load(open(draft_file))
  df = pd.DataFrame(js['plans'])
  datestring = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M")
  Path(f"exports/{organization}").mkdir(parents=True, exist_ok=True)

  file = (
        f"exports/{organization}/{organization}_prod_Drafts_{datestring}.csv"
   )
  df = df[df['show']]
  df = df[['id', 'link', 'title', 'text', 'type']]
  df.to_csv(file)
  print(f"Wrote {len(df.index)} drafts to {file}")
  print(f"To generate block assignments, gen any necessary cross-reference unit remappings and run\n   python assignments.py {organization} {file}")
def usage():
  print(f"Generates a CSV file with the active draft plans")
  print (f"Usage:  python {sys.argv[0]} DRAFTS.json")
  print (f"Usage:  python {sys.argv[0]} newexico")


if __name__ == "__main__":
  _,  organization = sys.argv 
  if organization:
    main( organization)
  else:
    usage()