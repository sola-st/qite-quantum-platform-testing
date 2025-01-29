# Labeling of Clusters: Evaluation

1. Create a conda environment with the necessary dependencies.
```shell
conda create -n labeling python=3.10
conda activate labeling
pip install label-studio
pip install "dask[complete]"
```

2. Make the local folder accessible:
```shell
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/home/paltenmo/projects/crossplatform/data/labeling
```

3. Start the labeling server:
```shell
label-studio start
```

4. Prepare the data by sampling from the dataset:
```shell
python -m labeling.sample_crashes --input_folder program_bank/v005 --output_folder data/labeling/sample --sample_size 20 --random_seed 42
```

5. Import the data into the labeling server via the web interface. Use Local Storage option, you need to configure the path of the data folder on the server via environment variables.

6. Label the data using the web interface.

7. Export the labels to a JSON file, use the option to include also the data information itself and not only the labels. (Place them in the `data/labeled_datasets/v001` folder)

8. Run the notebook `notebooks/009_Benchmark_Clustering.ipynb` to evaluate the clustering results.