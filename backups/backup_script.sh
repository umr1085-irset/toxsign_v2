#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

. "$DIR""/../.envs/.local/.django"
. "$DIR""/../.envs/.local/.postgres"

CELERY_BROKER_URL="${REDIS_URL}"
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
LOCAL_BACKUP_DIR="$DIR""/archives/"
REMOTE_BACKUP_DIR="/tmp/"
DATE=`eval date +%Y%m%d`

if docker-compose -f "$DIR""/../local.yml" exec -e DATABASE_URL=$DATABASE_URL -e CELERY_BROKER_URL=$CELERY_BROKER_URL django python manage.py check_signatures > /dev/null 2>&1; then

   docker-compose -f "$DIR""/../local.yml" exec postgres sh -c "pg_dump --clean -U $POSTGRES_USER $POSTGRES_DB > /backups/DB_backup"
   mv "$DIR""/DB_backup" "$DIR""/../toxsign/media/"
   tar -pzcf  "$BACKUP_DIR""archive-$DATE"".tar.gz" "$DIR""/../toxsign/media/"
   rm "$DIR""/../toxsign/media/DB_backup"
fi


cd $LOCAL_BACKUP_DIR
ls -1t  | tail -n +4 | xargs rm -f

rsync -av --delete --exclude=".*" $LOCAL_BACKUP_DIR $REMOTE_BACKUP_DIR
