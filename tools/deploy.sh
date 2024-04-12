#!/bin/bash

REGION="eu-west-3"
NAMESPACE="development"
VERSION="latest"

function update_config()
{
   NAMESPACE=$1

   RDS_ENDPOINT=$(aws rds describe-db-clusters --db-cluster-identifier aurora-cluster-wordpress-$NAMESPACE 2>&1 | grep -v DBClusterNotFoundFault | jq -r .DBClusters[0].Endpoint | tr -d '\n')
   RDS_SECRET=$(aws secretsmanager list-secrets | jq -r .SecretList[].Name | grep rds | tr -d '\n') 
   RDS_PASS=$(aws secretsmanager get-secret-value --secret-id "${RDS_SECRET}" | jq -r .SecretString | jq -r .password | tr -d '\n')

   sed -i "s/password_here/${RDS_PASS}/g" wordpress/wp-config-sample.php
   sed -i "s/localhost/${RDS_ENDPOINT}/g" wordpress/wp-config-sample.php
   sed -i "s/username_here/dbuser_${NAMESPACE}/g" wordpress/wp-config-sample.php
   sed -i "s/database_name_here/wordpress${NAMESPACE}/g" wordpress/wp-config-sample.php

cat<<EOF >>wordpress/wp-config-https.php
<?php
    define('FORCE_SSL_ADMIN', true);
    define('FORCE_SSL_LOGIN', true);
    \$WP_HOSTNAME = \$_SERVER['HTTP_HOST'];
    if (!empty(\$_SERVER['HTTP_X_FORWARDED_HOST'])) {
        \$WP_HOSTNAME = \$_SERVER['HTTP_X_FORWARDED_HOST'];
    }
   if (\$_SERVER['HTTP_X_FORWARDED_PROTO'] == 'https') {
        \$_SERVER['HTTPS']='on';
   }
   \$WP_HOSTNAME = "https://" . \$WP_HOSTNAME;
    define('WP_HOME', \$WP_HOSTNAME );
    define('WP_SITEURL', \$WP_HOSTNAME );
EOF
   sed -i 's/<?\(php\)*//g' wordpress/wp-config-sample.php
   cat wordpress/wp-config-sample.php >> wordpress/wp-config-https.php
   mv  wordpress/wp-config-https.php     wordpress/wp-config.php
   sed -i 's/\r$//g' wordpress/wp-config.php
}

function get_package()
{
   [ ! -z "$1" ] && NAMESPACE=$1
   [ ! -z "$2" ] && VERSION=$2
   [ ! -z "$3" ] && REGION=$3

   wget https://wordpress.org/${VERSION}.tar.gz && tar -xzvf ${VERSION}.tar.gz
   aws eks update-kubeconfig --region ${REGION} --name CLUSTER-WORDPRESS-$NAMESPACE
   update_config "$NAMESPACE"
   for pod in $(kubectl get pods -A | egrep "php-fpm|web" | awk -F' ' '{print $2}')
       do
         echo "kubectl cp wordpress/wp-config.php $NAMESPACE/$pod:/var/www/html/wordpress/"
         kubectl cp wordpress/ $NAMESPACE/$pod:/var/www/html/
         kubectl cp wordpress/wp-config.php $NAMESPACE/$pod:/var/www/html/wordpress/
       done
   rm -f latest.tar.gz && rm -rf wordpress
}


 while getopts "c:v:r:" opt;
    do
       case $opt in
       c)
          NAMESPACE=$OPTARG
          ;;
       v)
          VERSION=$OPTARG
          ;;
      r)
          REGION=$OPTARG
          ;;
       \?)
	      exit 1
          ;;
       esac
   done

   get_package "$NAMESPACE" "$VERSION" "$REGION"