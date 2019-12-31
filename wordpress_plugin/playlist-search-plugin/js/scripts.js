(function ($) {
    window.playlistSearchNamespace = {};
    $( document ).ready( function() {
        $( '.spotify_url_form' ).on( 'click', '.do_search', function( event ) {
            submitPlaylistSearch();
        } );
        $( '.update_db' ).click(function() {
            submitUpdateDbRequest();
        });
        $( '.get_update_db_status' ).click(function() {
            getUpdateDbStatus();
        });
        $( '.toggle_debug_link_container a' ).click(function() {
            toggleDebugBlock();
        });
    } );
    function removeTrailingCharIfExists(url, theChar) {
        var lastSlash = url.lastIndexOf(theChar);
        if (lastSlash == url.length - 1) {
            url = url.substr(0, url.length - 1);
        }
        return url
    }

    function getNthLastSegment(input, separatorChar, indexFromEnd) {
        var inputCopy = (' ' + input).slice(1); // https://stackoverflow.com/a/31733628/3846218
        inputCopy = removeTrailingCharIfExists(inputCopy, separatorChar);
        var arr = inputCopy.split(separatorChar);
        var index = arr.length - 1 - indexFromEnd;
        return arr[index];
    }

    function getSpotifyIdFromLink(urlInput) {
        var parser = document.createElement('a');
        parser.href = urlInput;
        pathname = parser.pathname;
        return getNthLastSegment(pathname, '/', 0);
    }

    function getSpotifyTypeFromLink(urlInput) {
        var parser = document.createElement('a');
        parser.href = urlInput;
        pathname = parser.pathname;

        return getNthLastSegment(pathname, '/', 1);
    }

    function getSpotifyIdFromUri(uriInput) {
        return getNthLastSegment(uriInput, ':', 0);
    }

    function getSpotifyTypeFromUri(uriInput) {
        return getNthLastSegment(uriInput, ':', 1);
    }

    function getSpotifyQueryType(query) {
        firstFourChars = query.substring(0, 4)
        if (firstFourChars === "http") {
            return "link";
        }
        if (firstFourChars === "spot") {
            return "uri";
        }
    }

    function toggleDebugBlock() {
        $("#update_db_status_details_block").toggle()
    }

    function submitPlaylistSearch() {
        var spotifyQuery = $("#spotify_url_textbox").val();
        var queryType = getSpotifyQueryType(spotifyQuery);
        console.log("type = " + queryType);

        var spotifyId = null;
        var spotifyType = null;

        if (queryType === "link") {
            spotifyId = getSpotifyIdFromLink(spotifyQuery);
            spotifyType = getSpotifyTypeFromLink(spotifyQuery);
        }
        else if (queryType === "uri") {
            spotifyId = getSpotifyIdFromUri(spotifyQuery);
            spotifyType = getSpotifyTypeFromUri(spotifyQuery);
        }
        else {
            console.log("can't handle spotify type " + queryType + ". Aborting");
            return;
        }
        console.log('spotifyId = ' + spotifyId)
        console.log('spotifyType = ' + spotifyType)

        if (spotifyType == 'track') {
            var playlistSearchNamespace = window.playlistSearchNamespace || {};
            console.log('before setting: playlistSearchNamespace.recentlySearchedTrack = ' + playlistSearchNamespace.recentlySearchedTrack);
            playlistSearchNamespace.recentlySearchedTrack = spotifyId;
            console.log('playlistSearchNamespace.recentlySearchedTrack = ' + playlistSearchNamespace.recentlySearchedTrack);
            console.log('playlistSearchNamespace = ' + JSON.stringify(playlistSearchNamespace));

            var data = {
                'action' : 'get_track',
                'track_id' : spotifyId
            };
            $.get(settings.ajaxurl, data, function(response) {
                console.log('ok');
                console.log('response = ' + JSON.stringify(response));
                track = JSON.parse(response.data);

                $('#error_label').text('');
                $('#playlist_list').text('');
                $('#song_name').text('');
                $('#song_artists').text('');
                $('#song_album').text('');
                $('#playlist_csv_link').text('');

                if ($.isEmptyObject(track)) {
                    $('#error_label').text('Error: Track not found in database (does not exist in any playlists)');
                    return;
                }

                $('#song_name').text(track.name);
                var artistNames = $.map(track.artists, function(artist) { return artist["name"] });
                $('#song_artists').text(artistNames.join(', '))
                $('#song_album').text(track.album.name);
                $.each(track.playlists, function(index, playlist) {
                    console.log(playlist);
                    var playlistUrl = playlist.external_urls["spotify"];
                    var trackRankInPlaylist = playlist.track_rank
                    var trackAddedAt = playlist.added_at
                    var playlistLink = "<a href=\"" + playlistUrl + "\">" + playlist.name + "</a>";
                    var internalList = '<ul><li>Current position: ' + trackRankInPlaylist + '</li><li>Added at: ' + trackAddedAt + '</li></ul>';
                    $('#playlist_list').append($('<li>', {
                        html: playlistLink
                    })).append(internalList);

                });
                requestCsvDownload();

                console.log(track);
            });

        }
    }

    function updateDbRequestStatusBar(updateInterval) {
        var updateDbStatusUrl = $('.update_db_status_url').text();
        console.log('updateDbStatusUrl = ' + updateDbStatusUrl);
        var data = {
            'action' : 'get_update_db_status',
            'db_status_url' : updateDbStatusUrl
        };

        $.ajax({
            type: 'GET',
            url: settings.ajaxurl,
            data: data,
            success: function(data, textStatus, request){
                console.log("getting status " + JSON.stringify(data["data"]));
                $('.update_db_status').text(data["data"]["current"] + " / " + data["data"]["total"]);

                console.log("data['data']['current'] = " + data['data']['current']);
                console.log("typeof data['data']['current'] = " + typeof data['data']['current']);

                var percentageComplete = (data["data"]["current"] / data["data"]["total"]) * 100;
                console.log("percentage complete = " + percentageComplete);
                $('#update_db_status_bar').css('width', percentageComplete + '%');
                $('#update_db_status_json').text(JSON.stringify(data["data"]));
                if (percentageComplete >= 100 || data["data"]["state"] == "FAILURE") {
                    clearInterval(updateInterval);
                }
                if (data["data"]["state"] == "FAILURE") {
                    $('#update_db_failure_indicator').css('width', '100%');
                    $('#update_db_status_bar').css('width', '0');
                }

            },
            error: function (request, textStatus, errorThrown) {
                console.log("error getting update db status");
                clearInterval(updateInterval);
            }
        });

    }
    
    function submitUpdateDbRequest() {
        // hide failure indicator if it's still visible from past failure
        $('#update_db_failure_indicator').css('width', '0');
        var data = {
            'action' : 'update_db'
        };

        $.ajax({
           type: 'GET',
           url: settings.ajaxurl,
           data: data,
           success: function(data, textStatus, request){
                status_url = data['data']['headers']['Location'];
                $('.update_db_status_url').text(status_url);
                var updateInterval = setInterval(function() {
                    updateDbRequestStatusBar(updateInterval);
                }, 1000);
           },
           error: function (request, textStatus, errorThrown) {
                console.log("error submitting update db request");
           }
        });
    }

    function getUpdateDbStatus() {
        var updateDbStatusUrl = $('.update_db_status_url').text();
        console.log('updateDbStatusUrl = ' + updateDbStatusUrl);
        var data = {
            'action' : 'get_update_db_status',
            'db_status_url' : updateDbStatusUrl
        };

        $.ajax({
           type: 'GET',
           url: settings.ajaxurl,
           data: data,
           success: function(data, textStatus, request){
                console.log("getting status " + JSON.stringify(data["data"]));
                $('.update_db_status').text(data["data"]["current"] + " / " + data["data"]["total"]);

                console.log("data['data']['current'] = " + data['data']['current']);
                console.log("typeof data['data']['current'] = " + typeof data['data']['current']);

                var percentageComplete =  Math.floor((data["data"]["current"] / data["data"]["total"]) * 100);
                console.log("percentage complete = " + percentageComplete);
                $('#update_db_status_bar').css('width', percentageComplete + '%');

                $('#update_db_status_json').text(JSON.stringify(data["data"]));
                
           },
           error: function (request, textStatus, errorThrown) {
                console.log("error getting update db status");
           }
        });
    }

    function requestCsvDownload() {
        var playlistSearchNamespace = window.playlistSearchNamespace || {};
        console.log('playlistSearchNamespace = ' + JSON.stringify(playlistSearchNamespace));
        console.log('playlistSearchNamespace.recentlySearchedTrack = ' + playlistSearchNamespace.recentlySearchedTrack);
        var spotifyId = playlistSearchNamespace.recentlySearchedTrack;
        var data = {
            'action': 'get_track_csv',
            'track_id': spotifyId
        }

        $.ajax({
            type: 'GET',
            url: settings.ajaxurl,
            data: data,
            success: function(data, textStatus, request) {
                var encodedData = encodeURI(data['data']);
                console.log(data);
                console.log(encodedData);
                $('#playlist_csv_link').html('<a href="data:application/octet-stream,' + encodedData + '" download="track_' + spotifyId + '.csv">Download CSV</a>');
            }
        });
    }

})(jQuery);
