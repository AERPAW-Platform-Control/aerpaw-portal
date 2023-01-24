## `users`

Script [`users.py`](./code/users.py) examples:

- `/users`: paginated list of users (GET)
- `/users?search=string`: paginated list of users with search (GET)
- `/users/{int:pk}`: retrieve single user (GET)
- `/users/{int:pk}`: update single user `display_name` (PUT)
- `/users/{int:pk}/credentials`: list of user credentials (GET)
- `/users/{int:pk}/tokens`: retrieve user tokens (GET)
- `/users/{int:pk}/tokens?refresh=true`: refresh user tokens (GET)
- `/users/{int:pk}/tokens?generate=true`: generate user tokens (GET)

Expected [example output](./output-users.md)
