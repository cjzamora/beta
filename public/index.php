<?php // -->

// output path
$output = dirname(__DIR__) . '/data/training/';

// if post data is set
if(isset($_POST['training'])) {
    try {
        // try to load training data
        $training = json_decode($_POST['training'], true);

        // generate hash
        $hash = md5($training['href']) . '.json';

        // save it!
        file_put_contents(
            $output . $hash, json_encode($training['training'], JSON_PRETTY_PRINT));

        die('Training data saved.');
    } catch (\Exception $e) {
        die('Unable to save training data.');
    }
}