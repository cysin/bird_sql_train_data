# bird_sql_train_data
some scripts used to process bird text to sql training data

1. Get table schemas from sqlite file and table descriptions from csv files.
2. Clean and format csv data into json combined with 'create table' schemas.
3. Translate descriptions (column and value descriptions) to Chinese using QWen 14B model.
4. Translate train data (questions and hints) to Chinese, with QWen 14B.
5. Compose the training data for text to sql finetuning.
