2. Restrict Chat Access by time
mandatory
Objective: implement a middleware that restricts access to the messaging up during certain hours of the day

Instructions:

Create a middleware class RestrictAccessByTimeMiddleware with two methods, __init__and__call__. that check the current server time and deny access by returning an error 403 Forbidden

if a user accesses the chat outside 9PM and 6PM.
Update the settings.py with the middleware.

Repo:

GitHub repository: alx-backend-python
Directory: Django-Middleware-0x03
File: Django-Middleware-0x03/chats/middleware.py