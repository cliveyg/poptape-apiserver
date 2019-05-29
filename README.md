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

Also added via the Django admin are the incoming url and rules for allowed 
verbs and whether an api path is currently active. Also as part of this 
restrictions can be added as to valid ip addresses.

Request headers are passed back and forth between the client and microservice
but could potentially be restricted or transformed by this apiserver too.

TODO:
.....
* Add throttling
* Add Redis or similar store
* Change DB to postgres or mysql
* More tests
* General bug fixes
