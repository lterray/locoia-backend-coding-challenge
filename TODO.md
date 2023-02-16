## Possible improvements
- Read GitHub Api responses into objects to avoid typos in keys, or other misuses, and to validate data
we get back from the Api. 
- Now we don't download big gist files. We should handle it in a more user-friendly way. 
- We need more tests. 
- Can we use a database? What for? SQL or NoSQL?

If we allow some caching in the process (you mentioned 4 hours delay) then we can use a database for that
or in memory caching like Redis.
Both the file contents and/or the list of gists (per user per pattern) can be cached.
I would check the general usage of the application to decide about it.

For such data a NoSQL database can be sufficient.

- How can we protect the api from abusing it?

Maybe we can use similar solution to GitHub: have a rate limit by ip, or if users get token then by token.

- How can we deploy the application in a cloud environment?

I'm not a guru of this topic, but we have a lot of options from the easiest/less scalable (like Heroku)
until the most expensive/nicely scalable (like a github / gitlab pipeline which automatically runs tests / built and
upload docker image and updates a kubernetes cluster descriptor to download the new image...)

- How can we be sure the application is alive and works as expected when deployed into a cloud environment?

Some possible solutions:
1. Uptime robot
2. Logging and create automatic notifications
3. Kubernetes liveness probe
