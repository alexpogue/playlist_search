<?php
/**
 * Plugin Name: Playlist Search Plugin
 * Plugin URI: https://www.bandbuilderacademy.com
 * Description: Display the Playlist Search tool using a Wordpress shortcode
 * Version: 0.1
 * Text Domain: playlist-search-plugin
 * Author: Alex Pogue
 * Author URI: https://www.alexpogue.com
 */

function playlist_search_tool($atts) {
    $Content = '<div class="spotify_url_form">
                    Spotify song URL: <input type="text" id="spotify_url_textbox"></input>
                    <button class="do_search">Search Playlists</button>
                </div>
                <div>
                    <span id="error_label"></span><br /><br />
                    Name: <span id="song_name"></span><br />
                    Artist: <span id="song_artists"></span><br />
                    Album: <span id="song_album"></span><br /><br />
                    Playlists:<br />
                    <ul id="playlist_list">
                    </ul>
                    <span id="playlist_csv_link"></span>
                </div>';

    return $Content;
}

function scripts() {
    wp_register_style( 'custom_wp_admin_css', plugin_dir_url( __FILE__ ) . 'style/admin-style.css', false, '1.0.0' );
    wp_enqueue_style( 'custom_wp_admin_css' );

    wp_enqueue_script( 'playlist-search-tool', plugin_dir_url( __FILE__ ) . 'js/scripts.js', array( 'jquery' ), null, true );
    wp_localize_script('playlist-search-tool', 'settings', array(
        'ajaxurl' => admin_url('admin-ajax.php')
    ));

}

add_shortcode('playlist-search-tool', 'playlist_search_tool');
add_action('wp_enqueue_scripts', 'scripts');
add_action('admin_enqueue_scripts', 'scripts');
add_action( 'wp_ajax_get_track', 'get_track' );
add_action( 'wp_ajax_update_db', 'update_db' );
add_action( 'wp_ajax_get_update_db_status', 'get_update_db_status' );
add_action( 'wp_ajax_get_track_csv', 'get_track_csv' );

function myplugin_register_options_page() {
  add_options_page('Page Title', 'Plugin Menu', 'manage_options', 'myplugin', 'myplugin_options_page');
}
add_action('admin_menu', 'myplugin_register_options_page');

function myplugin_options_page() {
    ?>
      <div>
  <?php screen_icon(); ?>
  <h2>Playlist Search Plugin Settings</h2>
  <button class="update_db">Update db</button>
  <span class="update_db_status"></span><br />
  <div id="update_db_status_bar_container">
    <div id="update_db_status_bar"></div>
    <div id="update_db_failure_indicator"></div>
  </div>
  <div class="toggle_debug_link_container">
    <a href="#">Debug</a> 
  </div>
  <div id="update_db_status_details_block">
    URL: <span class="update_db_status_url"></span><br />
    Status: <span id="update_db_status_json"></span><br />
  </div>
  </div>
  <?php
}

function get_track() {
    $data = $_GET;

    $curl = curl_init();
    $url = "http://bandbuilderacademy.com:5000/track/";

    $query_params = array('spotify_id' => $data['track_id']);

    $url = sprintf("%s?%s", $url, http_build_query($query_params));
    curl_setopt($curl, CURLOPT_URL, $url);

    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    $result = curl_exec($curl);
    curl_close($curl);
    wp_send_json_success($result);
}

function update_db() {
    $data = $_GET;

    $curl = curl_init();
    $url = "http://bandbuilderacademy.com:5000/admin/reset_db";
    $url = sprintf("%s?%s", $url, http_build_query($query_params));
    $post_params = [];

    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_POST, 1);
    curl_setopt($curl, CURLOPT_POSTFIELDS, $post_params);

    // getting headers strategy from https://stackoverflow.com/a/9183272
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_VERBOSE, 1);
    curl_setopt($curl, CURLOPT_HEADER, 1);

    $result = curl_exec($curl);

    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $header = substr($result, 0, $header_size);
    $body = substr($result, $header_size);

    $headers = get_headers_from_curl_response($result);

    curl_close($curl);

    $json = array();
    $json['body'] = $body;
    $json['headers'] = $headers;
    wp_send_json_success($json);
}

// from https://stackoverflow.com/a/10590242
function get_headers_from_curl_response($response)
{
    $headers = array();

    $header_text = substr($response, 0, strpos($response, "\r\n\r\n"));

    foreach (explode("\r\n", $header_text) as $i => $line)
        if ($i === 0)
            $headers['http_code'] = $line;
        else
        {
            list ($key, $value) = explode(': ', $line);

            $headers[$key] = $value;
        }

    return $headers;
}

function get_update_db_status() {
    $data = $_GET;

    $curl = curl_init();
    $url = $data['db_status_url'];

    curl_setopt($curl, CURLOPT_URL, $url);

    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    $result = curl_exec($curl);
    curl_close($curl);

    $result_obj = json_decode($result);
    wp_send_json_success($result_obj);
}

function get_track_csv() {
    $data = $_GET;

    $curl = curl_init();
    $url = "http://bandbuilderacademy.com:5000/track/csv";

    $query_params = array('spotify_id' => $data['track_id']);

    $url = sprintf("%s?%s", $url, http_build_query($query_params));
    curl_setopt($curl, CURLOPT_URL, $url);

    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    $result = curl_exec($curl);
    curl_close($curl);
    wp_send_json_success($result);
}


