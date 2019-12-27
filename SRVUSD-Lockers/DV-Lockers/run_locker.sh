#!/bin/bash

while true; do
  echo "Starting at: " $(date)  
  start_num_emails=$( cat email_index.txt )
  echo "Start: " ${start_num_emails}
  python ./locker.py
  end_num_emails=$( cat email_index.txt )
  echo "End: " ${end_num_emails}
  sleep 300
  num_sent=$( expr ${end_num_emails} - ${start_num_emails} )
  echo "Sent: " ${num_sent}
  if test ${num_sent} -eq 0 ; then
    echo "Going to bed at: " $(date)
    sleep 3600
  fi
done
