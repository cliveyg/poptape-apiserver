# poptape-apiserver

An apiserver written in Python Django that takes http requests and verifies 
them against a database containing rules for the api request. The apiserver 
then acts as proxy and forwards incoming requests to the relevant microservices
asyncronously. The apiserver then gathers all returned requests and formats a 
suitable response based on the api rules contained in it's own database. 

The api rules are entered via the django admin. All rules are verified on input 
using json schema. The api rules are an array of microservices to be called for
the input url and are of the format:
```
[
{ "url": "/microservice/url1", "fields": [{"ms-field-name": "out-field-name"}]}
{ "url": "/microservice/url2", "fields": [{"ms2-field1": "output-field1"}
					  {"ms2-field2": "output-field2"}]}
.
.
]
```
"url" and "field" are fixed names but the field names and what they transpose
to can be anything. Output field names should be unique but json schema (v7)
does not currently have any facility to check this - so user beware. The json
schema validates against the model when a user attempts to enter rules in the 
Django administration panel. 

For api endpoints where you want to return all fields then a field *return_all* 
can be added and then the fields json is ignored;
To only return selected fields then completely remove the *return_all* json element.
This is useful if the returned data can have variable fields or for testing the 
api_server microservice.
Example below:

```
  { 
    "url": "items/<uuid1>", 
    "pass_data": true,
    "return_all": true,
    "fields": [
      {"name": "name"},
      {"description": "description"},
      {"category": "category"},
      {"location": "location"}
    ]
  }
```

Also added via the Django admin are the incoming url and rules for allowed 
verbs and whether an api path is currently active. IP address restrictions can
also be imposed on the API routes.

Request headers are passed back and forth between the client and microservice
without alteration but could potentially be restricted or transformed by this
apiserver too.

------

##### Testing:

Test coverage has been added. Command to create tests coverage report is
`coverage run --source='.' --rcfile=apiserver/tests/.coveragerc  manage.py test`
and the report can be read with `coverage -m`. Coverage has an issue with a
symlinked directory in the omit section of the coverage config file. I have 
temporarily hardcoded the full path in the config file. Needs to be fixed.


------

##### TODO:

* Refactor URL matching regexs
* ~~Add dev error reporting - error rep array~~
* Add throttling
* Add Redis or similar store
* ~~Change DB to postgres~~
* ~~Add coverage to tests~~
* ~~Mock calls to other microservices in tests~~
* More tests
* Move rev\_proxy stuff into it's own django app
* General bug fixes
* Make pep8 compliant even though imo it's uglier and harder to read.
