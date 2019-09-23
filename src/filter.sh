#!/bin/bash


# cat picsum |egrep -o 'https?://[^ ]+' | while read -r a; do echo $a; done > ddd
cat $1 | tr ' ' '\n' | sed 's/http/\nhttp/g' | egrep -o 'https?://picsum.photos/[^/]+[0-9]+[^/]+/[^/]+'| sed -r 's/^https?/https/g' | sed 's/\(.*[0-9]\)\(.*\)/\1/'| sed 's/\(https:\/\/picsum.photos\/\)//;s/[^0-9/]*//g;s/^/https:\/\/picsum.photos\//g'| sort -u > /opt/aaa
#[0-9]+/[0-9]+
#| sed 's/\(https:\/\/picsum.photos\)\(.*\)/\1/'
#\(^https:\/\/picsum.photos\/\)          s/\(.*[0-9]\)[^0-9/]*/\1/g
