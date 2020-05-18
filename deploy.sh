#!/bin/bash

echo -e "3\nStreamHopper\nY\n2\nn\nn" | eb init -i
eb create StreamHopper-App
aws codepipeline create-pipeline --cli-input-json file://pipeline.json

# eb create -t worker ProductAnalytics-Worker
# aws codepipeline create-pipeline --cli-input-json file://pipeline_worker.json