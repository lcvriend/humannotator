# Humannotator

*Jenia Kim, Lawrence Vriend*

Library for creating annotators for your data.  
Works well with Jupyter notebooks:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lcvriend/humannotator/master?filepath=examples%2Fexamples.ipynb)

## Quick start
### Create a simple annotator

1. [Load the data]('#load-data')
2. [Define the tasks]('#define-tasks)
3. [Instantiate the annotator]('#annotator')

```Python
    import pandas as pd
    from humannotator import Annotator, task_factory

    df = pd.read_csv('news.csv', index_col=0)
    cols = ['title', 'date', 'news_id']

    choices={
        '0': 'not adverse media',
        '1': 'adverse media',
        '3': 'exclude from dataset',
    }
    instruct = "What is the topic in the title?"
    task1 = task_factory(choices, 'Adverse media')
    task2 = task_factory(
        'str',
        'Topic',
        instruction=instruct,
        nullable=True
    )

    annotator = Annotator(df[cols], [task1, task2])
```

### Annotate your data

- Use the annotator by calling it: `annotator()`.
- The annotator keeps track of where you were.

### Access your annotations

- Access the annotations with the `annotated` attribute.
- Return merged data and annotations with the `merged` method.
- The annotations are conveniently stored in a pandas `DataFrame`.

### Store your annotations

- Store the annotator with the `save` method.
- Load the annotator with the `load` method.

## Load data
The annotator accepts `list`, `dict` and `DataFrame` objects as data.  

**dataframes**

- By default, the annotator will use its `index` and all `columns`.  
- Use `load_data` to create a `data` object if you need more control:
    1. `id_col` sets the column to be used as index.
    2. `item_cols` set the column or columns to be displayed.

## Define tasks
Tasks are set up, using the `task_factory`.
Create a task by passing it:

- the `kind` of task
- the `name` of the task
- (optionally) an `instruction`
- if its `nullable` (default is False)

**Kind of tasks**

kind      | kwargs     | dtype            | description
--------- | -----------| ---------------- | ----------------
str       |            | object           | String
regex     | regex      | object           | String validated by regex
int       |            | Int64            | Nullable integer
float     |            | float64          | Float
bool      |            | bool             | Boolean
category  | categories | CategoricalDtype | Categorical variable
date      |            | datetime64[ns]   | Date

## Annotator

The annotator detects if it is run from Jupyter.
If so, the annotator will render itself in html and css.
If not, the annotator will render itself as text.

You can force the annotator to render to text.
Set `text_display` to True when instantiating.
