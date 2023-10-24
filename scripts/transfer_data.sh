#!/bin/bash
USER="ben"
PASS="123"
DIR="/home/ben/Desktop/benchmarks/"
#LIST="cutlass" "deepbench" "ispass-2009" "pannotia" "parboil" "polybench" "rodinia" "shoc" "tango"
for suite in  "rodinia" "shoc" "tango"; do
    for bench in $(ls "$DIR""$suite"); do
        for topo in $(ls "$DIR""$suite""/$bench/"); do
            for nv in $(ls "$DIR""$suite""/$bench/""$topo"); do
                local_path="$DIR""$suite""/$bench/""$topo/""$nv""/4chiplet/"
                sshpass -p 123 scp -r $USER@157.193.213.86:"$local_path""data/"   $local_path
                sshpass -p 123 scp  $USER@157.193.213.86:"$local_path""*.csv"   $local_path
                #sshpass -p 123 scp -r $USER@157.193.213.86:"$local_path""plots/" $local_path
            done
            #sshpass -p 123 scp -r $USER@157.193.213.86:"$DIR""$suite""/$bench/""$topo/""*.csv" "$DIR""$suite""/$bench/""$topo/"
        done
        #sshpass -p 123 scp -r $USER@157.193.213.86:"$DIR""$suite""/$bench/""*.jpg" "$DIR""$suite""/$bench/"
        #sshpass -p 123 scp -r $USER@157.193.213.86:"$DIR""$suite""/$bench/""*.csv" "$DIR""$suite""/$bench/"
    done
    #sshpass -p 123 scp -r $USER@157.193.213.86:"$DIR""$suite/"".csv" "$DIR""$suite/"
    #sshpass -p 123 scp -r $USER@157.193.213.86:"$DIR""$suite/"".html" "$DIR""$suite/"
done
