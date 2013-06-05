#!/bin/bash

SCRIPT_PATH="/path/to/script"
${SCRIPT_PATH}/add_backlog.py > ${SCRIPT_PATH}/add_backlog.txt
echo $?
cat ${SCRIPT_PATH}/add_backlog.txt >> ${SCRIPT_PATH}/all_backlog.txt
echo $?

# send mail only of it's not empty
if [ -s ${SCRIPT_PATH}/add_backlog.txt ]
then
  mail -s 'New Kanban Ticket(s)' your@email.com < ${SCRIPT_PATH}/add_backlog.txt 
  rm ${SCRIPT_PATH}/add_backlog.txt
fi
