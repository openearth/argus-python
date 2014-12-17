#!/bin/bash


# TODO: Lock the old database
# Dump the argus deltares database
mysqldump --defaults-file=~/.my.cnf --defaults-group-suffix=argus   --lock-tables=FALSE  argus > argusdeltares.sql
# Dump the TUD database
mysqldump --defaults-file=~/.my.cnf --defaults-group-suffix=argustud   --lock-tables=FALSE  argus-tud > argustud.sql

# Create two new databases....
# private and public
# Dump the schema only
echo "CREATE DATABASE IF NOT EXISTS arguspublic;" > arguspublic.sql
mysqldump --defaults-file=~/.my.cnf --defaults-group-suffix=argus --no-data --lock-tables=FALSE argus > arguspublic.sql
echo "CREATE DATABASE IF NOT EXISTS argusprivate;" > argusprivate.sql
mysqldump --defaults-file=~/.my.cnf --defaults-group-suffix=argus --no-data --lock-tables=FALSE argus > argusprivate.sql

# Now fill the databases with the appropriate info
