import asyncio
import os
from datetime import datetime
from backend.training.pipeline import GridTrainingPipeline  # Updated import path

async def test_pipeline():
    """Test the GridTrainingPipeline class with Neo4j integration."""
    # Ensure environment variables are set
    os.environ["NEO4J_URI"] = "neo4j+s://1d55c1d3.databases.neo4j.io"
    os.environ["NEO4J_USER"] = "<username>"
    os.environ["NEO4J_PASSWORD"] = "<password>"

    # Initialize the training pipeline manager
    pipeline_manager = GridTrainingPipeline()

    try:
        # Create a new training pipeline
        print("Creating a new training pipeline...")
        config = {"learning_rate": 0.01, "epochs": 10}
        pipeline = await pipeline_manager.create_pipeline("Test Pipeline", config)
        print(f"Pipeline created: {pipeline.pipeline_id}")

        # Start the training pipeline
        print("Starting the training pipeline...")
        await pipeline_manager.start_pipeline(pipeline.pipeline_id)
        print(f"Pipeline {pipeline.pipeline_id} started.")

        # Wait for a few seconds to simulate monitoring
        await asyncio.sleep(15)

        # Retrieve the pipeline from the database
        print("Retrieving the pipeline from the database...")
        retrieved_pipeline = await pipeline_manager._get_pipeline_from_db(pipeline.pipeline_id)
        if retrieved_pipeline:
            print(f"Pipeline retrieved: {retrieved_pipeline.pipeline_id}")
            print(f"Status: {retrieved_pipeline.status}")
            print(f"Config: {retrieved_pipeline.config}")
        else:
            print("Pipeline not found in the database.")

    finally:
        # Close the Neo4j driver
        pipeline_manager.close()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_pipeline())
