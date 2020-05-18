# API
This directory should contain scripts and notebooks for the acquisition of information on shows that are available on streaming platforms. 

## DATA

**WARNING: You must have a valid Guidebox API that is stored in a file named `api/guidebox_API_key.txt` to successfully run this script. Please feel free to request a one-week free trial key from https://www.guidebox.com/register**

## METADATA

`imdb_query.py` is a script that can be used to reproduce the acquisition of metadata for TV and movie shows. It requires a `csv` file that contains a `imdb_id` column that has the IMDB ID for each show. It also requires the user to specify the type of show being handled for metadata collection, which can be either `movie` or `tv`. 

USAGE:
```bash
python imdb_query.py movies.csv movie
```
