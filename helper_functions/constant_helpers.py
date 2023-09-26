import json

def find_branch(account_id):
     match account_id:
          case "413034898429":
               return "sandbox"
          case _:
               return "sandbox"

def find_repo_branch(account_id):
     match account_id:
          case "413034898429":
               return "sandbox"
          case _:
               return "playpen"

def find_VPCID(account_id):
     match account_id:
          case "413034898429":
               return "vpc-0284ec975b459d347"
          case _:
               return "vpc-0284ec975b459d347"


def find_CodeStarARN(account_id):
     match account_id:
          case "413034898429":
               return "arn:aws:codestar-connections:us-east-2:413034898429:connection/394e5ee7-0082-45fc-9da1-ca68c363ff58"
          case _:
               return "arn:aws:codestar-connections:us-east-2:413034898429:connection/394e5ee7-0082-45fc-9da1-ca68c363ff58"
