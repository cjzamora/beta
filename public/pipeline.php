<?php // -->

// get the root path
$root     = dirname(__DIR__);
// model we're going to use
$model    = '000';
// output path
$output   = $root . '/public/tmp/%s.json';
// log path
$log      = $root . '/public/tmp/%s.log';

// do we have post data?
if(!empty($_POST) && isset($_POST['url'])) {
    // format url
    $url = str_replace(
            array('?', '#', '&', '='), 
            array('\?', '\#', '\&', '\='), $_POST['url']);

    // generate id
    $id = md5($url);

    // generate output path
    $output = sprintf($output, $id);
    // generate log path
    $log    = sprintf($log, $id);

    // create output file
    file_put_contents($output, '{}');
    
    // execute command
    $exec = exec('cd ' . $root . ' && bin/pipeline -u ' . $url . ' -m ' . $model . ' -o ' . $output . ' > ' . $log . ' 2>&1 &');

    // if debug
    if(isset($_GET['debug'])) {
        print file_get_contents($log);
    }

    // set header
    header('Content-Type: application/json');

    // get output
    try {
        // read the results
        $data = file_get_contents($output);

        // parse as json
        $data = json_encode(json_decode($data));

        // remove output
        unlink($output);
        // remove log
        unlink($log);

        // output data
        die($data);
    } catch(\Exception $e) {
        // remove output if exists
        if(file_exists($output)) {
            // remove output
            unlink($output);
        }

        // remove log if exists
        if(file_exists($log)) {
            // remove log
            unlink($log);
        }

        die(json_encode(array(
            'error'     => true,
            'message'   => 'An error occured while processing request.'
        )));
    }
} else {
    die(json_encode(array(
        'error'     => true,
        'message'   => 'Invalid request.'
    )));
}