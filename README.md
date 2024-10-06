
# Geospatial Processing Pipeline



## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/konishon/geoprocessing_pipeline.git
   cd geoprocessing_pipeline
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Run the Pipeline

1. Edit the configuration in `configs/pipeline_config.json` to define your pipeline steps.
2. Run the pipeline:
   ```bash
   python scripts/run_pipeline.py
   ```

## Folder Structure

- **`geoprocessing_pipeline/`**: Core modules.
- **`configs/`**: JSON configuration files.
- **`scripts/`**: Scripts to run the pipeline.
- **`data/`**: OSM graph data and other files.
