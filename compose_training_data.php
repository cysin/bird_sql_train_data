<?php

function generate_alpaca_data($_bird_data, $_train_data) {
  $alpaca_data = [];

  foreach ($_train_data as $row) {
    $db_id = $row['db_id'];
    $question_translated = $row['question_translated'];
    $evidence_translated = $row['evidence_translated'];
    $sql = $row['SQL'];

    if (!isset($_bird_data[$db_id])) {
      continue; // Skip if database not found in schema
    }

    $table_schema = $_bird_data[$db_id];
    $table_name = key($table_schema);
    $instructions = build_instructions($table_schema, 'zh-CN', $evidence_translated, $table_name);

    $alpaca_data[] = [
      "instruction" => implode("\n", $instructions),
      "input" => $question_translated,
      "output" => $sql,
      "system" => "",
      "history" => [],
    ];
  }

  return $alpaca_data;
}

function build_instructions($table_schema, $language = 'en', $evidence_translated, $table_name) {
  $instructions = [];
  $schema = $table_schema[$table_name]['schema'];
  $instructions[] = "创建表 `$table_name` 的 SQL 为:";
  $instructions[] = $schema;

  $columns = $table_schema[$table_name]['column_comment'];
  foreach ($columns as $column_name => $column_info) {
    $translated_description = isset($column_info['column_description_translated']) ? $column_info['column_description_translated'] : '';
    $translated_value_description = isset($column_info['value_description_translated']) ? $column_info['value_description_translated'] : '';
    $data_type = $column_info['data_format'];

    if ($language === 'zh-CN') {
      $instructions[] = "列 `$column_name` 的数据格式为 `$data_type`。";
      if ($translated_description) {
        $instructions[] = "该列的描述为: $translated_description";
      }
      if ($translated_value_description) {
        $instructions[] = "该列的值描述为: $translated_value_description";
      }
    } else {
      $instructions[] = "The column `$column_name` has data format `$data_type`.";
      if ($translated_description) {
        $instructions[] = "The translated description for `$column_name` is: $translated_description";
      }
      if ($translated_value_description) {
        $instructions[] = "The translated value description for `$column_name` is: $translated_value_description";
      }
    }
  }



  $instructions[] = $evidence_translated; // Add evidence for reference

  return $instructions;
}

// Load your JSON data files
$bird_data = json_decode(file_get_contents('bird_training_data_alpaca_translated.json'), true);
$train_data = json_decode(file_get_contents('train_translated.json'), true);

// Generate Alpaca training data
$alpaca_data = generate_alpaca_data($bird_data, $train_data);

// Encode Alpaca data to JSON
$json_data = json_encode($alpaca_data, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE);

// Save the generated JSON data
file_put_contents('alpaca_training_data.json', $json_data);

echo "LLM training data in Alpaca format generated successfully!";

?>
