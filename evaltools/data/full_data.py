
# %%
# from os import environ
from typing import Any, Tuple
import pandas as pd
import os
import requests
import json

'''
Functions related to fetch the unabridged data for an env/org from the portal
The API_KEY must be passed in as an environment variable named API_KEY
'''
# %%
def fetch_json(url: str, API_KEY: str) -> Any:
    """
  Utility to retrieve json from a url, using an AWS API_KEY
  """
    headers = {"X-API-Key": API_KEY}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Error retrieving data\n {r.status_code} {r.text}")
    json_struct = json.loads(r.text)
    return json_struct


# %%


def portal_data_json(environment: str, organization: str, API_KEY: str) -> Any:
    """
  Call portal API  that returns the submission, comments and their tags
  """

    ENDPOINTS = {
        "qa": f"https://ik3ewh40tg.execute-api.us-east-2.amazonaws.com/qa/submissions/star/{organization}",
        "prod": f"https://k61e3cz2ni.execute-api.us-east-2.amazonaws.com/prod/submissions/star/{organization}",
        "main": f"https://o1siz7rw0c.execute-api.us-east-2.amazonaws.com/prod/submissions/star/michigan",
    }
    endpoint = ENDPOINTS[environment]
    # Use paging API to get a bunch of records at a time until
    # we get an empty set of records.
    limit = 1000
    offset = 0
    done = False
    all_records = {"submissions": [], "comments": [], "tags": [], "commenttags": []}
    while not done:
        url = f"{endpoint}?offset={offset}&limit={limit}"
        json = fetch_json(url, API_KEY)
        message = json["message"]
        print(
            f"submissions {len(message['submissions'])} comments {len(message['comments'])}"
        )
        all_records["submissions"].extend(message["submissions"])
        all_records["comments"].extend(message["comments"])
        all_records["tags"].extend(message["tags"])
        all_records["commenttags"].extend(message["commenttags"])

        if (
            len(message["submissions"]) == 0
            and len(message["comments"]) == 0
            and len(message["tags"]) == 0
            and len(message["commenttags"]) == 0
        ):
            done = True
        else:
            offset = offset + limit
    return all_records


# %%
def json_as_dataframes(json, organization) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
  Get full data from portal API and convert submissions and comments to Panda Dataframes
  TODO: Could also return DFs for tags and commenttags if anyone wanted them
  """

    if organization == "michigan":
        submission_cols = [
            "id",
            "title",
            "type",
            "text",
            "link",
            "salutation",
            "first",
            "last",
            "email",
            "city",
            "state",
            "zip",
            "datetime",
            "verified",
            "key",
            "sourceip",
            "useragent",
            "districttype",
            "profanity",
            "token",
            "emailverified",
        ]
    else:
        submission_cols = [
            "id",
            "title",
            "type",
            "text",
            "link",
            "salutation",
            "first",
            "last",
            "email",
            "city",
            "state",
            "zip",
            "datetime",
            "hidden",
            "emailverified",
            "hasprofanity",
            "districttype",
            "contactable",
            "phone",
            "coalition",
            "language",
            "draft",
        ]

    if organization == "michigan":
        comment_cols = [
            "id",
            "submission",
            "text",
            "salutation",
            "first",
            "last",
            "email",
            "city",
            "state",
            "zip",
            "datetime",
            "emailverified",
            "profanity",
            "draft",
        ]
    else:
        comment_cols = [
            "id",
            "submission",
            "text",
            "salutation",
            "first",
            "last",
            "email",
            "city",
            "state",
            "zip",
            "datetime",
            "emailverified",
            "hidden",
            "hasprofanity",
            "contactable",
            "phone",
            "coalition",
            "language",
            "draft",
        ]

    if len(json["submissions"]) == 0:
        submissions_df = pd.DataFrame(columns=submission_cols)
    else:
        submissions_df = pd.DataFrame(json["submissions"])

    if len(json["comments"]) == 0:
        comments_df = pd.DataFrame(columns=comment_cols)
    else:
        comments_df = pd.DataFrame(json["comments"])
        
    # The Michigan DB lacks a column called 'hidden'
    # For consistency, add it was a false of False
    if "hidden" not in submissions_df.columns:
      submissions_df["hidden"] = False
    if "hidden" not in comments_df.columns:
      comments_df["hidden"] = False

    # The Michigan DB calls the column called 'profanity' instead of 'hasprofanity'
    if "profanity" in submissions_df.columns:
      submissions_df = submissions_df.rename(columns={"profanity": "hasprofanity"})
    if "profanity" in comments_df.columns:
      comments_df = comments_df.rename(columns={"profanity": "hasprofanity"})


    return submissions_df, comments_df

