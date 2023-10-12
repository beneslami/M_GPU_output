#!/bin/bash
SUB_PATH="/home/ben/Desktop/benchmarks/$1/$2"
if [ -d $SUB_PATH ]; then
    for topo in "$SUB_PATH"/*; do
        if [ -d $topo ]; then
            for nv in "$topo"/*; do
                if [ -d $nv ]; then
                    for ch in "$nv"/*; do
                        if [ -d $ch ]; then
                            num=$(ls $ch | wc -l)
                            if [[ $num != 0 ]]; then
                               for file in $(ls $ch/*.txt); do
                                   touch "$ch/temp.txt"
                                   new_file="$ch/temp.txt"
                                   counter=1
                                   IFS=$'\n'
                                   for line in $(cat $file); do
                                     if [[ $line == *"-kernel id"* ]]; then
                                        echo "-kernel id = $counter" >> $new_file
                                        counter=$(($counter+1))
                                     else
                                         echo "$line" >> $new_file
                                     fi
                                   done
                                   rm $file
                                   mv $new_file $file
                               done
                            fi
                        fi
                    done
                fi
            done
        fi
    done
fi
