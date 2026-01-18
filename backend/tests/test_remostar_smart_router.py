
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the root directory to the Python path to allow for correct module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import the class from the root directory
from remostar_smart_router import RemostarSmartRouter

class TestRemostarSmartRouter(unittest.TestCase):
    """Unit tests for the RemostarSmartRouter class."""

    @patch('remostar_smart_router.GraphDatabase.driver')
    def test_initialization(self, mock_driver):
        """
        Test that the RemostarSmartRouter class initializes correctly.
        """
        # Arrange
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "password"
        
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance

        # Act
        router = RemostarSmartRouter(neo4j_uri=uri, neo4j_user=user, neo4j_password=password)

        # Assert
        # Check if the driver was called correctly
        mock_driver.assert_called_once_with(uri, auth=(user, password))
        self.assertEqual(router.neo4j_driver, mock_driver_instance)

        # Check if model configurations are set correctly
        self.assertEqual(router.qwen_model, "Mostar/remostar-light:dcx1")
        self.assertEqual(router.mistral_model, "Mostar/remostar-light:dcx2")

        # Check if neo4j_tools are defined correctly
        self.assertIsInstance(router.neo4j_tools, list)
        self.assertEqual(len(router.neo4j_tools), 3)

        # Check the first tool
        self.assertEqual(router.neo4j_tools[0]['function']['name'], 'query_mind_graph')
        self.assertIn('cypher_query', router.neo4j_tools[0]['function']['parameters']['properties'])

        # Check the second tool
        self.assertEqual(router.neo4j_tools[1]['function']['name'], 'get_soul_info')
        self.assertIn('soul_name', router.neo4j_tools[1]['function']['parameters']['properties'])

        # Check the third tool
        self.assertEqual(router.neo4j_tools[2]['function']['name'], 'log_mostar_moment')
        self.assertIn('thought', router.neo4j_tools[2]['function']['parameters']['properties'])
        self.assertIn('action', router.neo4j_tools[2]['function']['parameters']['properties'])
        self.assertIn('residue', router.neo4j_tools[2]['function']['parameters']['properties'])


if __name__ == '__main__':
    unittest.main()
