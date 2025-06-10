# Development

Depends on:

* Python >=3.8

---

1. Create and activate a python virtual environment of your choice.
1. Inside the virtual environment or machine:
    - Install an editable version of simple-action-pipeline.   
      `git clone https://github.com/antarctica/wfsai ./wfsai`  
      `cd ./wfsai`  
      `pip install -e .`  
    - Use `pip install -e ".[documentation]"` to edit/contribute to the documentation.

## Release/Versioning

Version numbers should be used in tagging commits on the `main` branch and should be of the form `v0.1.7` using the semantic versioning convention.

## Bugs & issues  

If you find a bug, or would like to contribute please [raise an issue](https://github.com/antarctica/wfsai/issues/new) in the first instance.

## Building & deploying the documentation

Run `mkdocs build` to build the docs.

Then run `mkdocs gh-deploy` to deploy to the `gh-pages` branch of the repository. You must have write access to the repo.