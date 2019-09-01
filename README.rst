Humannotator
------------

Library for creating annotators for your data.
Works well with Jupyter notebooks.

### Create a simple annotator

1. Load the data
2. Define the tasks
3. Instantiate the annotator

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
    task2 = task_factory('str', 'Topic', instruction=instruct, nullable=True) 

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
