#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

. "$DIR""/../.envs/.production/.django_prod"
. "$DIR""/../.envs/.production/.postgres_prod"

CELERY_BROKER_URL="${REDIS_URL}"
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
LOCAL_BACKUP_DIR="$DIR""/archives/"
REMOTE_BACKUP_DIR="/groups/irset/archives/web/TOXsIgNv2/archives/"
DATE=`eval date +%Y%m%d`

echo "Writing Postgres dump"
/usr/local/bin/docker-compose -f "$DIR""/../production.yml" exec -T postgres sh -c "pg_dump --clean -U $POSTGRES_USER $POSTGRES_DB > /backups/DB_backup"
mv "$DIR""/DB_backup" "$DIR""/../toxsign/media/"
echo "Building archive"
tar -pzcf  "$LOCAL_BACKUP_DIR""archive-$DATE"".tar.gz" "$DIR""/../toxsign/media/"
rm "$DIR""/../toxsign/media/DB_backup"

cd $LOCAL_BACKUP_DIR
ls -1t  | tail -n +3 | xargs rm -f
echo "Rsync.."
#rsync -av --delete --exclude=".*" $LOCAL_BACKUP_DIR $REMOTE_BACKUP_DIR

# mboudet 16/12/22 stop keeping a copy on the local machine (space issue)
mv "$LOCAL_BACKUP_DIR""archive-$DATE"".tar.gz" $REMOTE_BACKUP_DIR
ls -1t $REMOTE_BACKUP_DIR/*  | tail -n +3 | xargs rm -f
