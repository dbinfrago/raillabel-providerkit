..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: MIT

=============================
2 Converting Annotation Files
=============================

Many annotation providers have their own proprietary format, that they use internally. If the project requirements demand the delivery of the data in the RailLabel format, then the `raillabel_providerkit.convert()` method can support you with that.

.. code-block:: python

    from raillabel_providerkit import convert
    import raillabel
    import json  # in the case the data is in the json-format

    with open("path/to/source/data.json") as f:
        raw_data = json.load(f)

    raillabel_scene = convert(raw_data)

    raillabel.save(raillabel_scene, "path/to/target/scene.json")

If you have created a proper loader class for your format in the loader_classes directory, your class should be selected automatically. If not, you should contact our engineers to create one.

In the case, that you do not want to publish your proprietary format, you can also keep your loader class local and provide it as a function parameter. Just make sure your loader class is a child of the `raillabel_providerkit.loader_classes.LoaderABC`-class.

.. code-block:: python

    from raillabel_providerkit import convert
    import raillabel
    import json  # in the case the data is in the json-format

    with open("path/to/source/data.json") as f:
        raw_data = json.load(f)

    raillabel_scene = convert(raw_data, YourLoaderClass)
