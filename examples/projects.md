## `projects`

### Endpoints

`/projects`

- GET - retrieve list of projects
- POST - create new project

`/projects/{int:pk}`

- GET - retrieve project detail
- POST - update project detail

### Code

### Output

Script [`projects.py`](./code/projects.py) examples:

- `/projects`: paginated list with search (GET), create new project (POST)
- `/projects/{int:pk}`: detail for single project (GET), update single project (PUT)
- `/projects/{int:pk}/experiments`: list of project experiments (GET)
- `/projects/{int:pk}/membership`: list of project membership (GET), edit project membership (PUT)

Expected [example output](./output-projects.md)



