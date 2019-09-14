#!/usr/bin/env bash

# This script is to keep calling reset_db until we process all user's playlists
#
# NOTE: very much in progress, still has some issues

num_playlists="$(curl https://playlist-search-252817.appspot.com/admin/count_playlists)"

i=0
while [[ "$num_playlists" -lt 8000 ]]; do
    curl https://playlist-search-252817.appspot.com/admin/reset_db
    limit=3
    same_how_many_times=0
    prevretval=0
    retval=0
    while [ "$same_how_many_times" -eq "$limit" ]; do
        retval="$(curl https://playlist-search-252817.appspot.com/admin/count_playlists)"
        echo "retval = $retval"
        if [ "$retval" -eq "$prevretval" ]; then
            echo "same $same_how_many_times times"
            (( same_how_many_times++ ))
        fi
        sleep 5s
    done
done

echo "got 8000 playlists, aborting"
