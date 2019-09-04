# Humannotator

**Library for conveniently creating simple customizable annotators 
for manual annotation of your data**  
*Jenia Kim, Lawrence Vriend*

Works well with Jupyter notebooks:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lcvriend/humannotator/master?filepath=examples%2Fexamples.ipynb)

## Use case

The humannotator provides an easy way to set up custom annotators.
This tool is for you if manual annotation is part of your workflow 
and you are looking for a solution that is:

- Lightweight
- Customizable
- Easy to set up
- Integrates with Jupyter/pandas/Python

## Quick start

### Create a simple annotator

1. [Load the data](#load-data)
2. [Define the tasks](#define-tasks)
3. [Instantiate the annotator](#annotator)

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

    annotator = Annotator([task1, task2], df[cols])
```

### Annotate your data

- Use the annotator by calling it: `annotator()`.
- The annotator keeps track of where you were.
- <mark>Highlight</mark> phrases with the 'highlight_text' argument.

### Access your annotations

- Access the annotations with the `annotated` attribute.
- Return merged data and annotations with the `merged` method.
- The annotations are conveniently stored in a pandas `DataFrame`.

### Store your annotations

- Store the annotator with the `save` method.
- Load the annotator with the `load` method.

## Load data

The annotator accepts `list`, `dict`, `Series` and `DataFrame` objects as data.  
The data will be converted to a dataframe internally.

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
- any kwargs necessary

Typically: 
```Python
    task_factory(
        'kind',
        'name',
        instruction='instruction',
        nullable=True/False,
        kwarg=kwarg,
    )
```

Passing a dict or list to `kind` will create a categorical task.  
In this case the `categories` kwarg  is ignored.

**Available tasks**

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
Set `text_display` to True when instantiating or calling.

If you want to:
- Only annotate specific records, pass a list of ids to the annotator call.
- Pickle the data with the annotator, set the `save_data` flag to True.
