#!/bin/bash

PROJECT=aqueous-choir-160420
gcloud -q --project=$PROJECT tasks queues create p1s1t1-create-need
gcloud -q --project=$PROJECT tasks queues create p1s1t2-create-hashtag
gcloud -q --project=$PROJECT tasks queues create p1s1t3-create-needer
gcloud -q --project=$PROJECT tasks queues create p1s1t4-create-user
gcloud -q --project=$PROJECT tasks queues create p1s1t5-create-cluster
gcloud -q --project=$PROJECT tasks queues create p1s1t6-create-caretaker-skill

gcloud -q --project=$PROJECT app deploy --version 1 3>> upload_log.txt
