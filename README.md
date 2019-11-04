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

### Install the humannotator

Install with conda:

```
    conda install -c lcvriend humannotator
```

Or use pip:

```
    pip install humannotator
```

### Create a simple annotator

1. [Load the data](#load-data)
2. [Define the tasks](#define-tasks)
3. [Instantiate the annotator](#annotator)

```Python
    import pandas as pd
    from humannotator import Annotator

    # load data
    df = pd.read_csv('examples/popcorn_classics.csv', sep=';', index_col=0)

    # set up the annotator
    ratings = [
        'One bag',
        'Two bags',
        'Three bags',
        'Four bags',
        'Five-bagger',
    ]
    annotator = Annotator(df, name='VFA | Rate my popcorn classics')
    annotator.tasks['Bags of popcorn'] = ratings

    # run annotator
    annotator(user='GT')
```

In Jupyter this gives:

<img src="/examples/popcorn_classics.png" alt="Humannotator" width="847">

### Annotate your data

- Use the annotator by calling it: `annotator()`.
- The annotator keeps track of where you were.
- Highlight phrases with the 'phrases' argument.
- The annotator stores user (if provided) and timestamp with the annotation.

### Access your annotations

- The annotations are conveniently stored in a pandas `DataFrame`.
- Access the annotations with the `annotated` attribute.
- Get the indeces of the records without annotation with `unannotated`.
- Return the data merged with its annotations with the `merged` method.

### Store your annotations

- Store the annotator with the `save` method.
- Load the annotator with the `load` method.

## Load data

The annotator accepts `list`, `dict`, `Series` and `DataFrame` objects as data.  
The data will be converted to a dataframe internally.

### Dataframes

- By default, the annotator will use the dataframe's `index` and all `columns`.
- Use `load_data` to easily create a `data` object if you need more control:
    1. `id_col` sets the column to be used as index.
    2. `item_cols` set the column or columns to be displayed.

## Define tasks

Tasks can be set up through subscription or with the `task_factory`.

### Setting up tasks with the task factory
Create a task by passing `task_factory`:

- the `kind` of task
- the `name` of the task
- (optionally) an `instruction`
- (optionally) a list of `dependencies`
- whether it is `nullable` (default is False)
- any [kwargs](#Available-tasks) necessary (depends on the kind of task)

Typically: 
```Python
    task_factory(
        'kind',
        'name',
        instruction='instruction',
        dependencies=dependencies,
        nullable=True/False,
        **kwargs,
    )
```

Passing a dict or list to `kind` will create a categorical task.  
In this case the `categories` kwarg is ignored.

### Setting up tasks through subscription

It is also possible to instantiate an annotator and add tasks through subscription:  

```Python
    a = Annotator()
    a.tasks['topic'] = ['economy', 'politics', 'media', 'other']
    a.tasks['factual'] = bool, "Is the article factual?", False
```

To add a task like this, you minimally need to provide the `kind` of task you are trying to create.
Optionally, you can add `instruction`, `nullability`, `dependencies` and any other kwargs (as dictionary).
Change the order in which tasks are prompted to the user with the `order` attribute on `tasks`.

### Available tasks

kind      | kwargs     | dtype            | description
--------- | -----------| ---------------- | ----------------
str       |            | object           | String
regex     | regex      | object           | String validated by regex
int       |            | Int64            | Nullable integer
float     |            | float64          | Float
bool      |            | bool             | Boolean
category  | categories | CategoricalDtype | Categorical variable
date      |            | datetime64[ns]   | Date

### Dependencies

Dependencies consist of a *condition* and a *value*, that can be passed as tuple:

```Python
    ("col1 == 'x'", False)
```

The condition is a [pandas query statement](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html#pandas.DataFrame.query).
Before prompting the user for input, the condition is evaluated on the current annotation.
If the query evaluates to True then the value will be assigned automatically.

## Annotator

### Calling the annotator

The annotator detects if it is run from Jupyter.
If so, the annotator will render itself in html and css.
If not, the annotator will render itself as text.
You can annotate a selection of records by passing a list of ids to the annotator call. If you want to reannotate ids that have already been annotated, then set `redo` to True when calling the annotator.

### Instantiating the annotator

> arguments
> ---------
> tasks : *Task, list of Task objects, Tasks, Annotations or DataFrame*
>
>     Annotation task(s).
>     If passed a DataFrame, then the tasks will be inferred from it.
>     Annotation data in the dataframe will also be initialized.
>
> data : *data, list-/dict-like, Series or DataFrame, default None*  
>
>     Data to be annotated.
>     If `data` is not already a data object,
>     then it will be passed through `load_data`.
>     The annotator can be instantiated without data,
>     but will only work after data is loaded.
>
> user : *str, default None*  
>
>     Name of the user.
>
> name : *str, default 'HUMANNOTATOR'*  
>
>     Name of the annotator.
>
> save_data : *boolean, default False*  
>
>     Set flag to True if you want to store the data with the annotator.
>     This will ensure that the pickled object, will contain the data.
> 
> other parameters
> ----------------
> **DISPLAY**  
> text_display : *boolean, default None*  
>
>     If True will display the annotator in plain text instead of html.
> 
> **DATA**  
> item_cols : *str or list of str, default None*  
>
>     Name(s) of dataframe column(s) to display when annotating.
>     By default: display all columns.
>
> id_col : *str, default None*  
>
>     Name of dataframe column to use as index.
>     By default: use the dataframe's index.
> 
> **HIGHLIGHTER**  
> phrases : *str, list of str, default None*  
>
>     Phrases to highlight in the display.
>     The phrases can be regexes.
>     It also to pass in a dict where:
>     - the keys are the phrases
>     - the values are the css styling
>
> escape : *boolean, default False*  
>
>     Set escape to True in order to escape the phrases.
>
> flags : *int, default 0 (no flags)*  
>
>     Flags to pass through to the re module, e.g. re.IGNORECASE.
> 
> **TRUNCATER**  
> truncate : *boolean, default True*  
>
>     Set to False to not truncate items.
>
> trunc_limit : *int, default 32*  
>
>     The number of words beyond which an item will be truncated.
>
