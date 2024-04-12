#!/bin/bash

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`
NAMESPACE=production

function get_ip()
{
  IPADDR=`nslookup $(kubectl get ingress -n $1 | awk 'BEGIN{FS=OFS=" ";}{print $4;}' | grep -v ADDRESS | tr -d '\n') | grep Address: | grep -v "#" | awk 'BEGIN{FS=OFS=" ";}{print $2;}' | head -n 1 | tr -d '\n'`
  echo $IPADDR
}

 while getopts "d:i:s:n:" opt;
    do
       case $opt in
        d)
	      DOMAINNAME=$OPTARG
          ;;
        s)
	      NAMERECORD=$OPTARG
          ;;
        i)
	      IPADDR=$OPTARG
          ;;
        i)
	      NAMESPACE=$OPTARG
          ;;
        \?)
	      exit 0
          ;;
       esac
   done


[[ -z "${IPADDR}" ]] && IPADDR=`get_ip ${NAMESPACE}`
python3 $SCRIPTPATH/dns.py -n $NAMERECORD -d $DOMAINNAME -i "${IPADDR}"