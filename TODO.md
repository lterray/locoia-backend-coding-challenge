## Possible improvements
* Read GitHub Api responses into objects to avoid typos in keys, or other misuses, and to validate data
we get back from the Api. 
* Now we don't download [big gist files and we don't handle gists with more than 300 files](https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28).
We should handle these cases.
  * One idea for the big files:
    * Return the gist_urls and the corresponding big file urls when their small ones did not match the pattern. 
    * Separate backend call can start a check of these big files. This call can be web socket based to be more verbose. 
    * Then the server git-pulls the files. The huge ones can be read as a stream.
    * Maybe we can warn the user not to use a regexp which checks multiple lines as that would make the streaming
solution harder. Alternatively we can check few lines together with the regexp but that will slow down the search
significantly (if we check x lines together then it will be O(x * N) instead of O(N) which is a constant increase but
significant in this case I think)
    * When we find a match or finish a big file then we can send back its result to the frontend

* We need more tests.
* Maybe the "big file" size limit can be converted to environment variable with time. Same can happen with the auth
token if we use one.
* Can we use a database? What for? SQL or NoSQL?

  * If we allow some caching in the process (you mentioned 4 hours delay) then we can use a database for that
or in memory caching like Redis.
Both the file contents and/or the list of gists (per user per pattern) can be cached.
I would check the general usage of the application to decide about it.

  * For such data a NoSQL database can be sufficient.

* How can we protect the api from abusing it?

  * Maybe we can use similar solution to GitHub: have a rate limit by ip, or if users get token then by token.

* How can we deploy the application in a cloud environment?

  * I'm not a guru of this topic, but we have a lot of options from the easiest/less scalable (like Heroku)
until the most expensive/nicely scalable (like a github / gitlab pipeline which automatically runs tests / built and
upload docker image and updates a kubernetes cluster descriptor to download the new image...)

* How can we be sure the application is alive and works as expected when deployed into a cloud environment?

  * Some possible solutions:
    * Uptime robot
    * Logging and create automatic notifications
    * Kubernetes liveness probe
