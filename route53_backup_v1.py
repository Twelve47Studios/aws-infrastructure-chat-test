#exec(open("route53_backup_v1.py").read())
import boto3
import os
import json
import shutil
from git import Repo
from sys import argv

def run(commit_message):
  generate_route_files()
  push_to_github(commit_message)

def generate_route_files():
  base_path = os.path.join(os.getcwd(), 'aws')
  if not os.path.exists(base_path):
    os.mkdir(base_path)

  base_path = os.path.join(base_path, 'route53')
  shutil.rmtree(base_path)
  if not os.path.exists(base_path):
    os.mkdir(base_path)

  r53 = boto3.client('route53')
  zones = r53.list_hosted_zones()["HostedZones"]

  for zone in zones:
    print('zone: ',zone)
    zone_type = zone['Id'].split('/')[1]
    zone_id = zone['Id'].split('/')[2]
    zone_resource_path = os.path.join(base_path, zone_id)
    if not os.path.exists(zone_resource_path):
      os.mkdir(zone_resource_path)
    zone_file = open(os.path.join(zone_resource_path, zone_type + '.json'),'w')
    zone_file.write(json.dumps(zone, sort_keys=True, indent=2))
    paginator = r53.get_paginator('list_resource_record_sets')
    source_zone_records = paginator.paginate(HostedZoneId=zone['Id'])
    record_index = 0
    for record_set in source_zone_records:
      for record in record_set['ResourceRecordSets']:
        print('record: ',record)
        file_path = os.path.join(zone_resource_path, record['Name'] + "_" + record['Type'] + "_" + str(record_index) + '.json')
        zone_file = open(file_path,'w')
        print('file: ' + file_path)
        zone_file.write(json.dumps(record, sort_keys=True, indent=2))
        zone_file.flush()
        record_index += 1

def push_to_github(commit_message):
  repo_dir = os.getcwd()
  repo = Repo(repo_dir)
  repo.git.add(A=True)
  repo.git.commit(m=commit_message)
  origin = repo.remote('origin')
  origin.push()

script, commit_message = argv
if commit_message:
  run(commit_message)
