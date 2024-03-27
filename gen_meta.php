<?php

// Function to get table schemas from SQLite database
function get_table_schemas($db_path)
{
    $db = new SQLite3($db_path);
    $tables = [];

    $result = $db->query("SELECT name, sql FROM sqlite_master WHERE type='table'");
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $tables[strtolower($row['name'])] = utf8_encode($row['sql']);
    }

    $db->close();
    return $tables;
}

// Function to read CSV files and get table descriptions
function get_table_descriptions($dir)
{
    $descriptions = [];

    if ($handle = opendir($dir)) {
        while (false !== ($entry = readdir($handle))) {
            if ($entry != '.' && $entry != '..') {
                $file_path = $dir . '/' . $entry;
                $table = strtolower(pathinfo($entry, PATHINFO_FILENAME));

                $file = fopen($file_path, 'r');
                $header = fgetcsv($file); // Read header row

                $column_descriptions = [];
                while (($data = fgetcsv($file, 0, ',')) !== false) {
                    $original_column_name = isset($data[0]) ? utf8_encode($data[0]) : '';
                    $column_name = isset($data[1]) ? utf8_encode($data[1]) : '';
                    $column_description = isset($data[2]) ? utf8_encode($data[2]) : '';
                    $data_format = isset($data[3]) ? utf8_encode($data[3]) : '';
                    $value_description = isset($data[4]) ? utf8_encode($data[4]) : '';

                    $column_descriptions[$original_column_name] = [
                        'column_name' => $column_name,
                        'data_format' => $data_format,
                        'column_description' => $column_description,
                        'value_description' => $value_description,
                    ];
                }

                $descriptions[strtolower($table)] = [
                    'column_comment' => $column_descriptions,
                ];
                fclose($file);
            }
        }
        closedir($handle);
    }

    return $descriptions;
}

// Traverse 'train_databases' directory
$train_databases_dir = 'train_databases';
$output_file = 'bird_training_data_alpaca.json';

$databases = [];

if ($handle = opendir($train_databases_dir)) {
    while (false !== ($db_dir = readdir($handle))) {
        if ($db_dir != '.' && $db_dir != '..') {
            $db_path = $train_databases_dir . '/' . $db_dir;

            if (is_dir($db_path)) {
                $db_name = pathinfo($db_path, PATHINFO_BASENAME);
                $sqlite_path = $db_path . '/' . $db_name . '.sqlite';
                $description_dir = $db_path . '/database_description';

                $table_schemas = get_table_schemas($sqlite_path);
                $table_descriptions = get_table_descriptions($description_dir);

                foreach ($table_schemas as $table_name => $schema) {
                    $databases[$db_name][strtolower($table_name)] = [
                        'schema' => $schema,
                        'column_comment' => isset($table_descriptions[strtolower($table_name)]['column_comment']) ? $table_descriptions[strtolower($table_name)]['column_comment'] : [],
                    ];
                }
            }
        }
    }
    closedir($handle);
}

// Output JSON file
$json_data = json_encode($databases, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
file_put_contents($output_file, $json_data);

echo "JSON file generated: $output_file\n";

?>
